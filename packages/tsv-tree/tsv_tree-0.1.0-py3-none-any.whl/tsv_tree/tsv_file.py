import bisect
import struct
import json
import zstd


class TsvWithTreeWriter:
    def __init__(self, path, leaf_size=1000, index_size=256):
        self.path = path
        self.file = None
        self.leaf_size = leaf_size
        self.index_size = index_size
        self.last_key = None
        self.count = 0
        self.accumulator = []
        self.summary = []
        # Expectation: caller will populate 'metadata_files' into this dict
        # before the writer closes.
        self.header = {} 

    def __enter__(self):
        self.file = open(self.path, "wb")
        # Reserve 8 bytes for pointer to the Header Block
        self.file.write(b"twt\1\0\0\0\0" + b"\0" * 8) 
        return self

    def __exit__(self, *_):
        self._close()

    def _write_leaf(self):
        # Leaf Node (Type 0): Compressed Text
        data = "\n".join("\t".join(map(str, x)) for x in self.accumulator)
        data = zstd.compress(data.encode(), 3)
        offset = self.file.tell()
        self.file.write(b"\0" + struct.pack("<Q", len(data)))
        self.file.write(data)
        self.summary.append((self.accumulator[0][0], offset))
        self.accumulator = []

    def add_entry(self, entry):
        key = entry[0]
        if self.last_key is not None:
            if key == self.last_key:
                raise RuntimeError(f"entry key {key} duplicated")
            if key < self.last_key:
                raise RuntimeError(f"entries not sorted: {key} < {self.last_key}")
        self.last_key = key
        self.count += 1
        self.accumulator.append(entry)
        if len(self.accumulator) >= self.leaf_size:
            self._write_leaf()
    
    def _close(self):
        if self.accumulator:
            self._write_leaf()
            
        # Build Index (Bottom-Up)
        level_nodes = self.summary
        while len(level_nodes) > 1:
            next_level = []
            for i in range(0, len(level_nodes), self.index_size):
                chunk = level_nodes[i:i + self.index_size]
                # Index Node (Type 1): Uncompressed Text
                data = "\n".join("\t".join(map(str, x)) for x in chunk)
                data = data.encode()
                node_offset = self.file.tell()
                self.file.write(b"\1" + struct.pack("<Q", len(data)))
                self.file.write(data)
                next_level.append((chunk[0][0], node_offset))
            level_nodes = next_level
            
        tree_offset = level_nodes[0][1] if level_nodes else 0
        
        # Write Header Block (Type 2)
        self.header["count"] = self.count
        self.header["tree_offset"] = tree_offset
        header = json.dumps(self.header).encode()
        header = zstd.compress(header, 3)
        header_offset = self.file.tell()
        self.file.write(b"\2" + struct.pack("<Q", len(header)))
        self.file.write(header)
        
        # Update position 8 (after magic) to point to Header Block
        self.file.seek(8)
        self.file.write(struct.pack("<Q", header_offset))
        self.file.close()


class TsvWithTreeReader:
    def __init__(self, path):
        self.path = path
        self.file = None
        self.header = {}

    def __enter__(self):
        self.file = open(self.path, "rb")
        
        # Validate magic bytes
        magic = self.file.read(8)
        if magic != b"twt\1\0\0\0\0":
            raise ValueError(f"Invalid file magic: expected b'twt\\1\\0\\0\\0\\0', got {magic!r}")
        
        # Read header offset (at position 8)
        header_offset_bytes = self.file.read(8)
        if len(header_offset_bytes) < 8:
            raise ValueError("File header is truncated")
        self.header_offset = struct.unpack("<Q", header_offset_bytes)[0]
        
        self.file.seek(self.header_offset)
        block_type, header = self.read_block()
        if block_type != 2:
            raise RuntimeError(f"Expected Header Block (Type 2), found {block_type}")
        self.header = header
        return self
    
    def __exit__(self, *_):
        if self.file:
            self.file.close()

    def read_block(self):
        block_type, block_size = struct.unpack("<BQ", self.file.read(9))
        raw_data = self.file.read(block_size)

        # Type 0: Leaf (Compressed Text)
        if block_type == 0:
            data = zstd.decompress(raw_data).decode().split("\n")
            return block_type, data
            
        # Type 1: Index (Uncompressed Text)
        if block_type == 1:
            data = raw_data.decode().split("\n")
            return block_type, data
            
        # Type 2: Header (Compressed JSON)
        if block_type == 2:
            data = json.loads(zstd.decompress(raw_data).decode())
            return block_type, data
            
        raise RuntimeError(f"unknown block type {block_type} in database")

    def iter_entries(self):
        # Leafs are written sequentially starting at byte 16 (after magic + header offset)
        self.file.seek(16)
        while True:
            try:
                block_type, data = self.read_block()
            except struct.error:
                break # EOF
                
            if block_type != 0:
                # We hit the Index or Header blocks; stop iterating
                break
                
            for entry in data:
                yield entry.split("\t")
    
    def find(self, key):
        """
        Retrieves [SRX, SRA, metadata_file] for a given SRX accession (key).
        Raises KeyError if not found.
        """
        next_offset = self.header["tree_offset"]
        if next_offset == 0:
            raise KeyError(key)
            
        while True:
            self.file.seek(next_offset)
            block_type, data = self.read_block()
            
            if block_type == 0: # Leaf
                index = bisect.bisect_left(data, key)
                
                # Check for prefix match (key + tab)
                if index < len(data) and data[index].startswith(key + "\t"):
                    return data[index].split("\t")
                raise KeyError(key)
                
            if block_type == 1: # Index
                # Bisect Right on 'key + space' (ASCII 32 < ASCII 9 (tab) is false, 
                # but ' ' > '\t' isn't what we want.
                # We want bisect_right against "SRX... " vs "SRX...\t"
                # Space (32) > Tab (9). This works.
                index = bisect.bisect_right(data, key + " ")
                
                if index == 0:
                    raise KeyError(key)
                    
                next_offset = int(data[index - 1].split("\t")[1])
                continue
                
            raise RuntimeError(f"Unexpected block type {block_type} during traversal")

