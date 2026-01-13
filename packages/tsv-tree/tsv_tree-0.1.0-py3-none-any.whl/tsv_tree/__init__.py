import builtins
import zipfile
import os
import tempfile
import subprocess


from .tsv_file import TsvWithTreeReader, TsvWithTreeWriter
from .map_file import MapWithTreeReader, MapWithTreeWriter
from .zip_file import ZipBatchWriter, ZipBatchReader


def open(path, mode="r", **kwargs):
    with open(path, "rb") as f:
        magic = f.read(8)
    if magic[:3] == "mwt":
        if mode.startswith("r"):
            return MapWithTreeReader(path, **kwargs)
        if mode.startswith("w"):
            return MapWithTreeWriter(path, **kwargs)
    if magic[:3] == "twt":
        if mode.startswith("r"):
            return TsvWithTreeReader(path, **kwargs)
        if mode.startswith("w"):
            return TsvWithTreeWriter(path, **kwargs)
    if magic[:4] == b"PK\x03\x04":
        if mode.startswith("r"):
            return ZipBatchReader(path, **kwargs)
        if mode.startswith("w"):
            return ZipBatchWriter(path, **kwargs)
    raise ValueError(f"unknown file type for '{path}' or invalid mode '{mode}'")


def convert_zip_batch_to_tsv_with_tree(base_path, output_path, rename_entry=None, **writer_kwargs):
    tmp_prefix = os.path.basename(output_path) + ".tmp."
    with tempfile.TemporaryDirectory(prefix=tmp_prefix, dir=os.path.dirname(output_path)) as tmp_dir:
        with builtins.open(f"{tmp_dir}/entry_list", "w") as entry_list_file:
            current_id = 1
            while os.path.isfile(f"{base_path}.{current_id}.zip"):
                with zipfile.ZipFile(f"{base_path}.{current_id}.zip", "r") as zip_file:
                    for entry in zip_file.infolist():
                        entry_list_file.write(f"{entry.filename}\t{current_id}\n")
                current_id += 1
        subprocess.run([
            "sort",
            "-T", tmp_dir,
            "-k", "1,1",
            "-o", f"{tmp_dir}/sorted_entry_list",
            f"{tmp_dir}/entry_list"],
            check=True,
            env={**os.environ, "LC_ALL": "C"})
        with builtins.open(f"{tmp_dir}/sorted_entry_list", "r") as entry_list_file:
            with TsvWithTreeWriter(output_path, **writer_kwargs) as writer:
                current_zip_file = None
                current_zip_id = None
                try:
                    for entry in entry_list_file:
                        entry_key, entry_zip_id = entry.strip().split("\t")
                        entry_zip_id = int(entry_zip_id)
                        if entry_zip_id != current_zip_id or not current_zip_file:
                            if current_zip_file:
                                current_zip_file.close()
                            current_zip_file = zipfile.ZipFile(
                                f"{base_path}.{entry_zip_id}.zip", "r")
                            current_zip_id = entry_zip_id
                        entry_data = current_zip_file.read(entry_key).decode()
                        if rename_entry:
                            entry_key = rename_entry(entry_key)
                        writer.add_entry([entry_key, entry_data])
                finally:
                    if current_zip_file:
                        current_zip_file.close()


def convert_zip_batch_to_map_with_tree(base_path, output_path, rename_entry=None, **writer_kwargs):
    with ZipBatchReader(base_path) as reader:
        with MapWithTreeWriter(output_path, **writer_kwargs) as writer:
            for entry_name, entry_data in reader.iter_entries():
                if rename_entry:
                    entry_name = rename_entry(entry_name)
                writer.add_entry([entry_name, entry_data.decode()])
