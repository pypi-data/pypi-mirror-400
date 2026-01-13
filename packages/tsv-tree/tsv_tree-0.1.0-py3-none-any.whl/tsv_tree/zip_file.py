import bisect
import struct
import zipfile
import os


class ZipBatchWriter:
    def __init__(self, base_path, max_entry_count=65_000):
        self.base_path = base_path
        self.current_id = 0
        self.current_file = None
        self.current_file_entry_count = None
        self.max_entry_count = max_entry_count

    def __enter__(self):
        self.switch_file()
        return self
    
    def __exit__(self, *_):
        if self.current_file:
            self.current_file.close()

    def switch_file(self):
        if self.current_file:
            self.current_file.close()
        self.current_id += 1
        path = f"{self.base_path}.{self.current_id}.zip"
        self.current_file = zipfile.ZipFile(
            path, "w",
            zipfile.ZIP_DEFLATED,
            compresslevel=6)
        self.current_file_entry_count = 0

    def add_entry(self, name, data):
        if self.current_file_entry_count >= self.max_entry_count:
            self.switch_file()
        self.current_file.writestr(name, data)
        self.current_file_entry_count += 1


def write_zip_batch_index(base_path, index_size=256):
    entries = []
    current_id = 1
    while os.path.isfile(f"{base_path}.{current_id}.zip"):
        with zipfile.ZipFile(f"{base_path}.{current_id}.zip", "r") as zip_file:
            for entry in zip_file.infolist():
                entries.append((entry.filename, 0, current_id))
        current_id += 1
    entries.sort(key=lambda x: x[0])
    with open(f"{base_path}.index.bin", "wb") as index_file:
        index_file.write(b"\0" * 8)
        level_nodes = entries
        while len(level_nodes) > 1:
            next_level = []
            for i in range(0, len(level_nodes), index_size):
                chunk = level_nodes[i:i + index_size]
                data = "\n".join("\t".join(map(str, x)) for x in chunk)
                data = data.encode()
                node_offset = index_file.tell()
                index_file.write(struct.pack("<Q", len(data)))
                index_file.write(data)
                next_level.append((chunk[0][0], 1, node_offset))
            level_nodes = next_level
        root_offset = level_nodes[0][2] if level_nodes else 0
        index_file.seek(0)
        index_file.write(struct.pack("<Q", root_offset))


class ZipBatchReader:
    def __init__(self, base_path):
        self.base_path = base_path
        self.index_file = None
        self.root_offset = None

    def __enter__(self):
        self.index_file = open(f"{self.base_path}.index.bin", "rb")
        self.root_offset = struct.unpack("<Q", self.index_file.read(8))[0]
        return self
    
    def __exit__(self, *_):
        if self.index_file:
            self.index_file.close()

    def find(self, name):
        next_offset = self.root_offset
        if next_offset == 0:
            raise KeyError(name)
        while True:
            self.index_file.seek(next_offset)
            block_size = struct.unpack("<Q", self.index_file.read(8))[0]
            raw_data = self.index_file.read(block_size)
            data = raw_data.decode().split("\n")
            # Leaf Node
            if data and data[0].endswith("\t0"):
                index = bisect.bisect_left(data, name)
                if index < len(data) and data[index].startswith(name + "\t"):
                    _, _, batch_id = data[index].split("\t")
                    return int(batch_id)
                raise KeyError(name)
            # Index Node
            index = bisect.bisect_right(data, name + " ")
            if index == 0:
                raise KeyError(name)
            next_offset = int(data[index - 1].split("\t")[2])

    def open(self, name, mode="r"):
        batch_id = self.find(name)
        with zipfile.ZipFile(f"{self.base_path}.{batch_id}.zip", "r") as zip_file:
            return zip_file.open(name, mode)

    def read(self, name):
        with self.open(name, "r") as entry_file:
            return entry_file.read()
