import os
import cv2
import enlighten

from enum import Enum
from tube_dl import Youtube, Playlist
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

from . import textfile
from . import csvfile
from ..system import filesys

class VideoUtils:
    @staticmethod
    def _default_meta_extractor(video_path):
        """Default video metadata extractor function."""
        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Check if the video was opened successfully
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return None

        # Get the frame count
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Get the FPS
        fps = cap.get(cv2.CAP_PROP_FPS)

        # get frame size
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Release the video capture object
        cap.release()

        meta_dict = {
            "video_path": video_path,
            "width": width,
            "height": height,
            "frame_count": frame_count,
            "fps": fps,
        }
        return meta_dict

    @staticmethod
    def get_video_meta_dict(video_path, meta_dict_extractor_func=None):
        assert os.path.exists(video_path), f"Video file {video_path} does not exist"
        if meta_dict_extractor_func and callable(meta_dict_extractor_func):
            assert (
                meta_dict_extractor_func.__code__.co_argcount == 1
            ), "meta_dict_extractor_func must take exactly one argument (video_path)"
            meta_dict = meta_dict_extractor_func(video_path)
            assert isinstance(
                meta_dict, dict
            ), "meta_dict_extractor_func must return a dictionary"
            assert "video_path" in meta_dict, "meta_dict must contain 'video_path'"
        else:
            meta_dict = VideoUtils._default_meta_extractor(video_path=video_path)
        return meta_dict

    @staticmethod
    def get_video_dir_meta_df(
        video_dir,
        video_exts=[".mp4", ".avi", ".mov", ".mkv"],
        search_recursive=False,
        csv_outfile=None,
    ):
        assert os.path.exists(video_dir), f"Video directory {video_dir} does not exist"
        video_files = filesys.filter_files_by_extension(
            video_dir, video_exts, recursive=search_recursive
        )
        assert (
            len(video_files) > 0
        ), f"No video files found in {video_dir} with extensions {video_exts}"
        video_meta_list = []
        for vfile in video_files:
            meta_dict = VideoUtils.get_video_meta_dict(vfile)
            if meta_dict:
                video_meta_list.append(meta_dict)
        dfmk = csvfile.DFCreator()
        columns = list(video_meta_list[0].keys())
        assert len(columns) > 0, "No video metadata found"
        assert "video_path" in columns, "video_path column not found in video metadata"
        # move video_path to the first column
        columns.remove("video_path")
        columns.insert(0, "video_path")
        dfmk.create_table("video_meta", columns)
        rows = [[meta[col] for col in columns] for meta in video_meta_list]
        dfmk.insert_rows("video_meta", rows)
        dfmk.fill_table_from_row_pool("video_meta")

        if csv_outfile:
            dfmk["video_meta"].to_csv(csv_outfile, index=False, sep=";")
        return dfmk["video_meta"].copy()


    # -----------------------------
    # FFmpeg Horizontal Stack
    # -----------------------------
    @staticmethod
    def hstack(video_files, output_file):
        """Horizontally stack multiple videos using FFmpeg."""
        tmp_file = "video_list.txt"
        try:
            with open(tmp_file, "w") as f:
                for video in video_files:
                    f.write(f"file '{video}'\n")

            ffmpeg_cmd = (
                f"ffmpeg -f concat -safe 0 -i {tmp_file} "
                f'-filter_complex "[0:v][1:v][2:v]hstack=inputs={len(video_files)}[v]" '
                f'-map "[v]" -c:v libx264 -preset fast -crf 22 {output_file}'
            )

            os.system(ffmpeg_cmd)
            print(f"[INFO] Video stacked successfully: {output_file}")

        except Exception as e:
            print(f"[ERROR] Video stacking failed: {e}")
        finally:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)


class VideoResolution(Enum):
    VR480p = "720x480"
    VR576p = "1280x720"
    VR720p_hd = "1280x720"
    VR1080p_full_hd = "1920x1080 "
    VR4K_uhd = "3840x2160"
    VR8K_uhd = "7680x4320"

    def __str__(self):
        return "%s" % self.value


def get_video_resolution_size(video_resolution):
    separator = "x"
    resolution_str = str(video_resolution)
    info_arr = resolution_str.split(separator)
    width, height = int(info_arr[0]), int(info_arr[1])
    return width, height


def get_videos_by_resolution(
    directory, video_resolution, video_ext="mp4", include_better=True
):
    video_paths = filesys.filter_files_by_extension(directory, video_ext)
    filtered_video_paths = []
    for path in video_paths:
        vid = cv2.VideoCapture(path)
        height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        valid = False
        video_width, video_height = get_video_resolution_size(video_resolution)
        if not include_better:
            if width == video_width and height == video_height:
                valid = True
        else:
            if width >= video_width and height >= video_height:
                valid = True

        if valid:
            filtered_video_paths.append(path)
    return filtered_video_paths


# time in seconds
def trim_video(source, destination, start_time, end_time):
    ffmpeg_extract_subclip(source, start_time, end_time, targetname=destination)


progress_bar = None

def on_progress(bytes_done, total_bytes):
    global progress_bar
    if progress_bar is None:
        progress_bar = enlighten.get_manager().counter(
            total=20, desc="Downloading", unit="byte", color="blue"
        )

    progress_bar.total = total_bytes
    progress_bar.count = bytes_done
    progress_bar.update(incr=0)
    # print(bytes_done)
    if bytes_done >= total_bytes:
        progress_bar.close()
        progress_bar = None


def get_youtube_url(full_url_or_video_code):
    if "youtube" in full_url_or_video_code:
        url = full_url_or_video_code
    else:
        url = f"https://youtube.com/watch?v={full_url_or_video_code}"
    return url


def download_yt_video(
    full_url_or_video_code,
    save_folder="./",
    report_progress=False,
    video_idx="1",
    total_video="1",
):
    url = get_youtube_url(full_url_or_video_code)
    filesys.make_dir(save_folder)
    filesys.change_current_dir(save_folder)
    try:
        yt = Youtube(url)
        title_en = yt.title.encode("ascii", "ignore")
        file_download = yt.formats.first()
        if report_progress:
            print(f"\n[{video_idx}/{total_video}][DOWNLOAD]{title_en}")
            file_download.download(onprogress=on_progress, skip_existing=True)
    except TypeError:
        print(f"[ERROR] download {url}")


def download_playlist(
    playlist_url, save_folder="./", report_progress=False, start_pattern=None
):
    print(f"[DOWNLOAD PLAYLIST] {playlist_url}")
    pl = Playlist(playlist_url).videos
    total_video = len(pl)
    should_start = False
    url = None
    count = 0
    for idx, code in enumerate(pl):
        try:
            url = f"https://youtube.com/watch?v={code}"
            yt = Youtube(url)
            count += 1
            if start_pattern is None:
                should_start = True
            elif start_pattern in yt.title:
                should_start = True
            if should_start:
                download_yt_video(
                    url,
                    save_folder,
                    report_progress,
                    video_idx=str(count),
                    total_video=str(total_video),
                )

        except TypeError:
            print(f"[ERROR] download {url}")
    enlighten.get_manager().stop()


# Pntt https://www.youtube.com/playlist?list=PLYaaU301HUe06Zlf3qv9q2dnVulj35gOb
# Format line: playlist_save_folder_path [SPACE] playlist_url
def download_multiple_playlist_in_files(text_file, report_progress=False):
    playlists = textfile.read_line_by_line(text_file)
    for folder_plUrl in playlists:
        folder = folder_plUrl.split()[0]
        plUrl = folder_plUrl.split()[1]
        download_playlist(plUrl, save_folder=folder, report_progress=report_progress)


# test code
# pl = 'https://youtube.com/playlist?list=PLYaaU301HUe03PabLEGbMGB8nhHgq58Zr'
# download_playlist(pl, './test', report_progress=True)
