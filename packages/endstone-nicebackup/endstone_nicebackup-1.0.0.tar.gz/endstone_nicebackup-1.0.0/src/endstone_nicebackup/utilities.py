import os
import shutil

BUFFER_SIZE = 64 * 1024


def del_folder(path: str) -> None:
    if os.path.exists(path):
        shutil.rmtree(path)


def copy_backup(src_folder: str, dest_folder: str, size_map: dict[str, int]) -> None:
    """Copy files from source to destination, optionally truncating based on size mapping.

    Recursively copies all files from src_folder to dest_folder. Files listed in
    size_map will be truncated to the specified byte size if they exceed it.

    Args:
        src_folder: Path to the source folder to copy from.
        dest_folder: Path to the destination folder to copy to.
        size_map: Dictionary mapping file paths to maximum byte sizes.
            Files not in the mapping are copied in full.
            Example: {"world/level.dat": 1024}
    """
    os.makedirs(dest_folder, exist_ok=True)

    folder_name = os.path.basename(src_folder.rstrip("/\\"))

    for root, dirs, files in os.walk(src_folder):
        rel_root = os.path.relpath(root, src_folder)

        for filename in files:
            rel_path = (
                filename if rel_root == "." else f"{rel_root}/{filename}"
            ).replace("\\", "/")

            src_path = os.path.join(root, filename)
            dest_path = os.path.join(dest_folder, rel_path)

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            map_key = f"{folder_name}/{rel_path}"
            file_size = os.path.getsize(src_path)

            with open(src_path, "rb") as f_src, open(dest_path, "wb") as f_dest:
                remaining = min(file_size, size_map.get(map_key, file_size))
                while remaining > 0:
                    chunk = f_src.read(min(BUFFER_SIZE, remaining))
                    if not chunk:
                        break
                    f_dest.write(chunk)
                    remaining -= len(chunk)
