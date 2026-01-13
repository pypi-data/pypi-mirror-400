import json
import os
import struct
import zstd

from .keys_file import sort_keys_file
from .util import try_remove_files


class MapWithTreeWriter:
    def __init__(self, path, keys_per_node=256):
        if keys_per_node < 2:
            raise ValueError("keys_per_node must be at least 2")
        self.path = path
        self.keys_per_node = keys_per_node
        self.file = open(self.path, "wb")
        
        # Reserve 8 bytes at start for header offset
        self.file.write(b"mwt\1\0\0\0\0" + b"\0" * 8)
        
        self.keys_file = open(f"{self.path}.keys.tmp", "wb")
        self.header = {}
        self._closed = False

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is None:
            self.close()
        else:
            # In case of error, attempt cleanup
            if not self.file.closed:
                self.file.close()
            if not self.keys_file.closed:
                self.keys_file.close()
            self._clean()

    def add_entry(self, key, value):
        if not isinstance(key, bytes):
            raise TypeError(f"Key must be bytes, got {type(key)}")
        
        # 1. Write Key to tmp index (Format: ValueOffset(8) + KeyLen(2) + Key)
        value_offset = self.file.tell()
        self.keys_file.write(struct.pack("<QH", value_offset, len(key)))
        self.keys_file.write(key)
        
        # 2. Write Compressed Value to main file (Format: ValLen(8) + CompressedBytes)
        c_value = zstd.compress(value, level=3)
        self.file.write(struct.pack("<Q", len(c_value)))
        self.file.write(c_value)

    def _build_index(self):
        if "tree_offset" in self.header:
            return
            
        self.keys_file.close()
        
        # 1. External Sort
        sorted_keys_path = f"{self.path}.keys.sorted.tmp"
        sort_keys_file(f"{self.path}.keys.tmp", sorted_keys_path)
        try_remove_files([f"{self.path}.keys.tmp"])
        
        next_level_info = [] 
        leaf_offsets = []
        entry_count = 0
        
        # 2. Build Leaf Nodes
        with open(sorted_keys_path, "rb") as keys_in:
            leaf_buffer = []
            first_key_in_leaf = None
            
            while True:
                header = keys_in.read(10)
                if len(header) < 10:
                    # Write final partial leaf
                    if leaf_buffer:
                        self._write_node(leaf_buffer, is_leaf=True, 
                                         first_key=first_key_in_leaf, 
                                         level_info=next_level_info, 
                                         offsets_list=leaf_offsets)
                    break
                
                val_offset, key_len = struct.unpack("<QH", header)
                key = keys_in.read(key_len)
                
                if not leaf_buffer:
                    first_key_in_leaf = key
                
                leaf_buffer.append((key, val_offset))
                entry_count += 1
                
                if len(leaf_buffer) >= self.keys_per_node:
                    self._write_node(leaf_buffer, is_leaf=True, 
                                     first_key=first_key_in_leaf, 
                                     level_info=next_level_info, 
                                     offsets_list=leaf_offsets)
                    leaf_buffer = []
                    first_key_in_leaf = None

        try_remove_files([sorted_keys_path])
        
        # Handle Empty Data
        if not next_level_info:
            self.header["tree_offset"] = 0
            self.header["entry_count"] = 0 
            return

        # 3. Link Leaf Nodes
        for i in range(len(leaf_offsets) - 1):
            curr_offset = leaf_offsets[i]
            next_offset = leaf_offsets[i+1]
            self.file.seek(curr_offset + 3)
            self.file.write(struct.pack("<Q", next_offset))
            
        self.file.seek(0, 2)

        # 4. Build Internal Nodes
        current_level = next_level_info
        while len(current_level) > 1:
            next_level_info = []
            for i in range(0, len(current_level), self.keys_per_node):
                children = current_level[i : i + self.keys_per_node]
                node_first_key = children[0][0]
                self._write_node(children, is_leaf=False, 
                                 first_key=node_first_key, 
                                 level_info=next_level_info)
            current_level = next_level_info
            
        self.header["tree_offset"] = current_level[0][1]
        self.header["entry_count"] = entry_count

    def _write_node(self, entries, is_leaf, first_key, level_info, offsets_list=None):
        offset = self.file.tell()
        level_info.append((first_key, offset))
        if offsets_list is not None:
            offsets_list.append(offset)
        
        # Header: Type(1), Count(2), Next/Padding(8)
        node_type = 1 if is_leaf else 0
        self.file.write(struct.pack("<BHQ", node_type, len(entries), 0))
        
        for key, ptr in entries:
            self.file.write(struct.pack("<H", len(key)))
            self.file.write(key)
            self.file.write(struct.pack("<Q", ptr))

    def close(self):
        if self._closed:
            return
        self._build_index()
        self._clean()
        
        # Write JSON footer and pointer
        header_offset = self.file.tell()
        self.file.write(json.dumps(self.header).encode())
        # Write header offset at position 8 (after magic)
        self.file.seek(8)
        self.file.write(struct.pack("<Q", header_offset))
        
        self.file.close()
        self._closed = True

    def _clean(self):
        try_remove_files([f"{self.path}.keys.tmp", f"{self.path}.keys.sorted.tmp"])


class MapWithTreeReader:
    def __init__(self, path):
        self.path = path
        self.file = open(self.path, "rb")
        
        # Validate magic and read header offset
        self.file.seek(0)
        magic = self.file.read(8)
        if magic != b"mwt\1\0\0\0\0":
            raise ValueError(f"Invalid file magic: expected b'mwt\\1\\0\\0\\0\\0', got {magic!r}")
        
        # Read header offset (at position 8)
        header_offset_bytes = self.file.read(8)
        if len(header_offset_bytes) < 8:
            raise ValueError("File header is truncated")
        header_offset = struct.unpack("<Q", header_offset_bytes)[0]
        
        # Read JSON header
        self.file.seek(header_offset)
        self.header = json.loads(self.file.read().decode())

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def _read_node(self, offset):
        """
        Reads node header and entries.
        Returns: (is_leaf, entries, next_offset)
        """
        self.file.seek(offset)
        # Header: Type(1), Count(2), Next/Padding(8)
        node_type, count, next_offset = struct.unpack("<BHQ", self.file.read(11))
        is_leaf = (node_type == 1)
        
        entries = []
        for _ in range(count):
            key_len_bytes = self.file.read(2)
            if not key_len_bytes: break
            key_len = struct.unpack("<H", key_len_bytes)[0]
            key = self.file.read(key_len)
            ptr_bytes = self.file.read(8)
            ptr = struct.unpack("<Q", ptr_bytes)[0]
            entries.append((key, ptr))
        
        return is_leaf, entries, next_offset

    def _search_tree(self, key):
        if self.header.get("tree_offset", 0) == 0:
            return None
        
        current_offset = self.header["tree_offset"]
        
        while True:
            is_leaf, entries, _ = self._read_node(current_offset)
            
            if is_leaf:
                for entry_key, value_offset in entries:
                    if entry_key == key:
                        return value_offset
                return None
            else:
                # Find the rightmost child where key >= entry_key
                child_offset = None
                for entry_key, ptr in entries:
                    if key >= entry_key:
                        child_offset = ptr
                    else:
                        break # Keys are sorted, no need to check further
                
                if child_offset is None:
                    return None
                current_offset = child_offset

    def get(self, key, default=None):
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        value_offset = self._search_tree(key)
        if value_offset is None:
            return default
        
        self.file.seek(value_offset)
        value_len = struct.unpack("<Q", self.file.read(8))[0]
        return zstd.decompress(self.file.read(value_len))

    def __getitem__(self, key):
        res = self.get(key)
        if res is None:
            raise KeyError(key)
        return res

    def __contains__(self, key):
        if isinstance(key, str):
            key = key.encode('utf-8')
        return self._search_tree(key) is not None

    def __len__(self):
        return self.header.get("entry_count", 0)

    def __iter__(self):
        if self.header.get("tree_offset", 0) == 0:
            return
        
        # 1. Drill down to leftmost leaf
        current_offset = self.header["tree_offset"]
        while True:
            is_leaf, entries, _ = self._read_node(current_offset)
            if is_leaf:
                break
            current_offset = entries[0][1] # Follow first child
        
        # 2. Iterate linked leaves
        while current_offset != 0:
            is_leaf, entries, next_leaf_offset = self._read_node(current_offset)
            
            for key, value_offset in entries:
                # Lazy load value
                self.file.seek(value_offset)
                v_len = struct.unpack("<Q", self.file.read(8))[0]
                val = zstd.decompress(self.file.read(v_len))
                yield (key, val)
            
            current_offset = next_leaf_offset

    def close(self):
        if hasattr(self, 'file') and not self.file.closed:
            self.file.close()
