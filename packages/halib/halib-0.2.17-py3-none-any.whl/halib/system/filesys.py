import glob
import os
import shutil
from distutils.dir_util import copy_tree
from concurrent.futures import ThreadPoolExecutor

COMMON_IMG_EXT = ["jpg", "jpeg", "png", "bmp", "tiff", "gif"]
COMMON_VIDEO_EXT = ["mp4", "avi", "mov", "mkv", "flv", "wmv"]

def is_exist(path):
    return os.path.exists(path)


def is_dir(path):
    return os.path.isdir(path)


def get_current_dir():
    return os.getcwd()


def change_current_dir(new_dir):
    if is_dir(new_dir):
        os.chdir(new_dir)


def get_dir_name(directory):
    return os.path.basename(os.path.normpath(directory))


def get_parent_dir(directory, return_full_path=False):
    if not return_full_path:
        return os.path.basename(os.path.dirname(directory))
    else:
        return os.path.dirname(directory)


def make_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def copy_dir(src_dir, dst_dir, dirs_exist_ok=True, ignore_patterns=None):
    shutil.copytree(
        src_dir, dst_dir, dirs_exist_ok=dirs_exist_ok, ignore=ignore_patterns
    )


def delete_dir(directory):
    shutil.rmtree(directory)


def list_dirs(directory):
    folders = list(
        filter(
            lambda x: os.path.isdir(os.path.join(directory, x)), os.listdir(directory)
        )
    )
    return folders


def list_files(directory):
    files = list(
        filter(
            lambda x: os.path.isfile(os.path.join(directory, x)), os.listdir(directory)
        )
    )
    return files

def filter_files_by_extension(directory, ext=None, recursive=True, num_workers=0):
    """
    Filters files using glob and multithreading.
    If ext is None, returns ALL files.

    Args:
        directory (str): Path to search.
        ext (str, list, or None): Extension(s) to find. If None, return all files.
        recursive (bool): Whether to search subdirectories.
        num_workers (int): Number of threads for checking file existence.
    """
    assert os.path.exists(directory) and os.path.isdir(
        directory
    ), "Directory does not exist"

    # 1. Normalize extensions to a tuple (only if ext is provided)
    extensions = None
    if ext is not None:
        if isinstance(ext, list):
            extensions = tuple(ext)
        else:
            extensions = (ext,)

    # 2. Define pattern
    pattern = (
        os.path.join(directory, "**", "*")
        if recursive
        else os.path.join(directory, "*")
    )

    # 3. Helper function for the thread workers
    def validate_file(path):
        if os.path.isfile(path):
            return path
        return None

    result_files = []
    if num_workers <= 0:
        num_workers = os.cpu_count() or 4
    # 4. Initialize ThreadPool with user-defined workers
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Step A: Get the iterator (lazy evaluation)
        all_paths = glob.iglob(pattern, recursive=recursive)

        # Step B: Apply Filter
        if extensions is None:
            # If ext is None, we skip the endswith check and pass everything
            candidate_paths = all_paths
        else:
            # Filter by extension string FIRST (Fast CPU op)
            candidate_paths = (p for p in all_paths if p.endswith(extensions))

        # Step C: Parallelize the disk check (Slow I/O op)
        for result in executor.map(validate_file, candidate_paths):
            if result:
                result_files.append(result)

    return result_files


def is_file(path):
    return os.path.isfile(path)


def get_file_name(file_path, split_file_ext=False):
    if is_file(file_path):
        if split_file_ext:
            filename, file_extension = os.path.splitext(os.path.basename(file_path))
            return filename, file_extension
        else:
            return os.path.basename(file_path)
    else:
        raise OSError("Not a file")


def get_absolute_path(file_path):
    return os.path.abspath(file_path)


# dest can be a directory
def copy_file(source, dest):
    shutil.copy2(source, dest)


def delete_file(path):
    if is_file(path):
        os.remove(path)


def rename_dir_or_file(old, new):
    os.renames(old, new)


def move_dir_or_file(source, destination):
    shutil.move(source, destination)
