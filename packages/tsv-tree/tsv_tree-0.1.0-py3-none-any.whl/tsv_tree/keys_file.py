import heapq
import os
import struct
import tempfile

from util import try_remove_files


def read_entry(f):
    header = f.read(10)
    if not header:
        return None
    value_offset, key_length = struct.unpack("<QH", header)
    key = f.read(key_length)
    assert len(key) == key_length
    return key, value_offset


def write_entry(f, key, value_offset):
    f.write(struct.pack("<QH", value_offset, len(key)))
    f.write(key)


def merge_files(input_paths, output_path):
    """
    Merge multiple sorted files into one sorted file using a min-heap.
    """

    file_handles = []
    heap = []
    
    # Open all input files and initialize heap with first entry from each
    for index, path in enumerate(input_paths):
        f = open(path, "rb")
        file_handles.append(f)
        entry = read_entry(f)
        if entry:
            key, value_offset = entry
            heapq.heappush(heap, (key, index, value_offset))
    
    # Merge using heap
    with open(output_path, "wb") as out_f:
        while heap:
            key, index, value_offset = heapq.heappop(heap)
            write_entry(out_f, key, value_offset)
            entry = read_entry(file_handles[index])
            if entry:
                next_key, next_offset = entry
                heapq.heappush(heap, (next_key, index, next_offset))
    
    # Close all file handles
    for f in file_handles:
        f.close()


def sort_keys_file(input_path, output_path):
    """
    External merge sort for keys file with memory and file constraints.
    """

    chunk_size = 40 * 1024 * 1024 # 40MB per chunk
    max_merge_way = 500 # Merge up to 500 files at once
    chunk_files = []

    tmp_dir_dir = os.path.dirname(output_path)
    tmp_dir_prefix = os.path.basename(output_path) + ".sort."
    with tempfile.TemporaryDirectory(dir=tmp_dir_dir, prefix=tmp_dir_prefix) as tmp_dir:
        
        # Phase 1: Split into sorted chunks
        with open(input_path, "rb") as f:
            chunk_num = 0
            while True:
                entries = []
                bytes_read = 0
                
                # Read entries until we hit chunk_size
                while bytes_read < chunk_size:
                    entry = read_entry(f)
                    if not entry:
                        break
                    key, value_offset = entry
                    entries.append((key, value_offset))
                    bytes_read += 10 + len(key)
                
                if not entries:
                    break
                
                # Sort by key
                entries.sort(key=lambda x: x[0])
                
                # Write sorted chunk
                chunk_path = os.path.join(tmp_dir, f"chunk_{chunk_num:06d}.tmp")
                with open(chunk_path, "wb") as chunk_f:
                    for key, value_offset in entries:
                        write_entry(chunk_f, key, value_offset)
                
                chunk_files.append(chunk_path)
                chunk_num += 1
        
        # Phase 2: Multi-level merge if needed
        merge_level = 0
        while len(chunk_files) > 1:
            next_chunks = []
            
            for i in range(0, len(chunk_files), max_merge_way):
                batch = chunk_files[i:i + max_merge_way]
                
                if len(chunk_files) <= max_merge_way and i == 0:
                    # Final merge - write to output
                    output = output_path
                else:
                    # Intermediate merge
                    output = os.path.join(tmp_dir, f"merge_L{merge_level}_{len(next_chunks):06d}.tmp")
                    next_chunks.append(output)
                
                merge_files(batch, output)
                
                # Clean up input files after merging
                try_remove_files(batch)
            
            chunk_files = next_chunks
            merge_level += 1
        
        # If only one chunk, just rename it
        if len(chunk_files) == 1 and chunk_files[0] != output_path:
            os.rename(chunk_files[0], output_path)
    