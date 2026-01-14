from ..common.common import *
from ..filetype import csvfile
import pandas as pd
import platform
import re  # <--- [FIX 1] Added missing import
import csv
from importlib import resources

PC_TO_ABBR = {}
ABBR_DISK_MAP = {}
pc_df = None
cPlatform = platform.system().lower()


def load_pc_meta_info():
    # 1. Define the package where the file lives (dotted notation)
    #    Since the file is in 'halib/system/', the package is 'halib.system'
    package_name = "halib.system"
    file_name = "_list_pc.csv"

    # 2. Locate the file
    csv_path = resources.files(package_name).joinpath(file_name)
    global PC_TO_ABBR, ABBR_DISK_MAP, pc_df
    pc_df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    PC_TO_ABBR = dict(zip(pc_df['pc_name'], pc_df['abbr']))
    ABBR_DISK_MAP = dict(zip(pc_df['abbr'], pc_df['working_disk']))
    # pprint("Loaded PC meta info:")
    # pprint(ABBR_DISK_MAP)
    # pprint(PC_TO_ABBR)
# ! must be called at the module load time
load_pc_meta_info()


def list_PCs(show=True):
    global pc_df
    if show:
        csvfile.fn_display_df(pc_df)
    return pc_df


def get_PC_name():
    return platform.node()


def get_PC_abbr_name():
    pc_name = get_PC_name()
    return PC_TO_ABBR.get(pc_name, "Unknown")


def get_os_platform():
    return platform.system().lower()


def get_working_disk(abbr_disk_map=ABBR_DISK_MAP):
    pc_abbr = get_PC_abbr_name()
    return abbr_disk_map.get(pc_abbr, None)

cDisk = get_working_disk()

# ! This funcction search for full paths in the obj and normalize them according to the current platform and working disk
# ! E.g: "E:/zdataset/DFire", but working_disk: "D:", current_platform: "windows" => "D:/zdataset/DFire"
# ! E.g: "E:/zdataset/DFire", but working_disk: "D:", current_platform: "linux" => "/mnt/d/zdataset/DFire"
def normalize_paths(obj, working_disk=cDisk, current_platform=cPlatform):
    # [FIX 3] Resolve defaults inside function to be safer/cleaner
    if working_disk is None:
        working_disk = get_working_disk()
    if current_platform is None:
        current_platform = get_os_platform()

    # [FIX 2] If PC is unknown, working_disk is None. Return early to avoid crash.
    if working_disk is None:
        return obj

    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = normalize_paths(value, working_disk, current_platform)
        return obj
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = normalize_paths(item, working_disk, current_platform)
        return obj
    elif isinstance(obj, str):
        # Normalize backslashes to forward slashes for consistency
        obj = obj.replace("\\", "/")

        # Regex for Windows-style path: e.g., "E:/zdataset/DFire"
        win_match = re.match(r"^([A-Z]):/(.*)$", obj)
        # Regex for Linux-style path: e.g., "/mnt/e/zdataset/DFire"
        lin_match = re.match(r"^/mnt/([a-z])/(.*)$", obj)

        if win_match or lin_match:
            rest = win_match.group(2) if win_match else lin_match.group(2)

            if current_platform == "windows":
                # working_disk is like "D:", so "D:/" + rest
                new_path = f"{working_disk}/{rest}"
            elif current_platform == "linux":
                # Extract drive letter from working_disk (e.g., "D:" -> "d")
                drive_letter = working_disk[0].lower()
                new_path = f"/mnt/{drive_letter}/{rest}"
            else:
                return obj
            return new_path

    # For non-strings or non-path strings, return as is
    return obj
