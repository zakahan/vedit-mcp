import os
import shutil
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from loguru import logger

# -----------------------------------------------------------------------------
# Setting Environment Variable
# Logging Configuration
if os.getenv("MCP_USING_LOGGER") == "True":
    USING_LOGGER = True
else:
    USING_LOGGER = False
# ---
if os.getenv("MCP_LOGGER_LEVEL") is None:
    LOGGER_LEVEL = "DEBUG"
else:
    LOGGER_LEVEL = os.getenv("MCP_LOGGER_LEVEL")

# LOGGER_FILE_DIR: this folder must：
# This directory must already exist, and an mcp.log file will be created here to record logs. 
# If you have any other ideas, please modify the code yourself.
LOGGER_FILE_DIR = os.getenv("LOGGER_FILE_DIR")

# Video Folder Base
KB_DIR = os.getenv("KB_BASE_PATH")
KB_CLIP = "clip"
KB_MERGE = "merge"
KB_RESULT = "result"

# -----------------------------------------------------------------------------


# Config Logger
def get_logger():
    if not USING_LOGGER:
        logger.remove()

    if LOGGER_FILE_DIR is None:
        raise ValueError("If you set `USING_LOGGER` to `True`, then you must configure " \
        "the environment variable `LOGGER_FILE_DIR` and " \
        "ensure that this directory already exists. ")

    elif not os.path.exists(os.path.abspath(LOGGER_FILE_DIR)):
        raise ValueError(f"The environment `LOGGER_FILE_DIR`={LOGGER_FILE_DIR} must already" \
                         "exist, we can not find it now.")


# Check the path
def check_paths():
    if KB_DIR is None:
        raise ValueError("KB_BASE_PATH is None, you must configure the environment variable " \
        "KB_BASE_PATH and ensure that this path truly exists. The function of this path is to " \
        "store the original video files, temporary files, and result files.")
    
    elif not os.path.exists(os.path.abspath(KB_DIR)):
        raise ValueError(
            f"The environment `KB_BASE_PATH`={KB_DIR} must already exist, we can not find it now.")




# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# start of functions -----------------------------------------------------------
# ------------------------------------------------------------------------------
# Underlying Implementation ----------------------------------------------------
# """
# ## Plan
# Actually, at a cursory glance, video editing can still be divided into the following operations: create, read, update, and delete.
# Create: Add filters, add subtitles, add background music, etc.
# Delete: Delete specified segments, delete subtitles, delete audio tracks, etc.
# Update: Merge multiple videos, cut out a small segment from the original video.
# Read: Query basic information of the original video, such as duration, frame rate, etc. (It seems this isn't very useful).

# ## What has been achieved so far
# 1. clip_video_tool: cut out a small segment from the original video.
# 2. move_videos_tool: merge multiple videos.
# 3. add_bgm_tool: add background music.
# """
# -----------------------------------------------------------------------------


# clip_video:
def clip_video(
        original_video_path: str,
        save_folder: str,
        start_time: int,
        stop_time: int,
        title: str,
) -> tuple[bool, str, str]:
    """
    Cut a video and save it to a specified folder.
    :param original_video_path: The path of the original video file.
    :param save_folder: The path of the folder where the cut video will be saved.
    :param start_time: The start time for cutting (in seconds; this time unit is sufficient for most operations).
    :param stop_time: The end time for cutting (in seconds).
    :return: A tuple where the first element is a boolean indicating whether the operation was successful, the second element is the output location, and the third element is the log information.
    """
    logger.debug("-----------------------------------------------------------------------------")
    logger.debug("Parameter check <clip_video> ------------------------------------------------")
    logger.debug(f"origin_video_path: {original_video_path}")
    logger.debug(f"save_folder: {save_folder}")
    logger.debug(f"start_time: {start_time}")
    logger.debug(f"stop_time: {stop_time}")
    logger.debug("-----------------------------------------------------------------------------")


    # Check if the original video file exists
    if not os.path.isfile(original_video_path):
        error_msg = f"Error: The original video file does not exist."
        logger.error(error_msg)
        return False, "", error_msg
    
    _, file_extension = os.path.splitext(original_video_path)

    # Check if the target folder exists. If it doesn't exist, create it. 
    if not os.path.exists(save_folder):
        try:
            os.makedirs(save_folder)
        except OSError as e:
            error_msg = f"Error: Failed to create the folder. Error message: {e}"
            logger.error(error_msg)
            return False, "", error_msg

    # Generate the output file path
    output_path = os.path.join(save_folder, f"{title}{file_extension}")

    try:
        # Build the FFmpeg command
        command = [
            'ffmpeg',
            '-y',
            '-ss', str(start_time),
            '-to', str(stop_time),
            '-i', original_video_path,
            '-c', 'copy',
            output_path
        ]
        # Execute the FFmpeg command
        subprocess.run(command, check=True)
        success_msg = f"The video has been successfully cut and is being saved. "
        logger.info(success_msg)
        return True, output_path, success_msg
    except subprocess.CalledProcessError as e:
        error_msg = f"Error: An error occurred while executing the FFmpeg command. Error message: {e}"
        logger.error(error_msg)
        return False, "", error_msg
    

def merge_videos(video_paths: list[str], save_folder: str) -> tuple[bool, str, str]:
    """
    Merge multiple local video files.
    :param video_paths: A list containing the paths of video files.
    :param save_folder: The folder where the merged video will be saved.
    :return: A tuple where the first element is a boolean indicating whether the operation was successful, the second element is the output path, and the third element is the log information.
    """
    logger.debug("-----------------------------------------------------------------------------")
    logger.debug("Parameter check <merge_videos> ----------------------------------------------")
    logger.debug(f"video_path: {str(video_paths)}")
    logger.debug(f"save_folder: {save_folder}")
    logger.debug("-----------------------------------------------------------------------------")
    # Check if all video files exist
    for path in video_paths:
        if not os.path.isfile(path):
            error_msg = f"Error: The video file does not exist."
            logger.error(error_msg)
            return False, "", error_msg

    # Check if the target folder exists. If not, create it.
    if not os.path.exists(save_folder):
        try:
            os.makedirs(save_folder)
        except OSError as e:
            error_msg = f"Error: Failed to create the folder. Error message: {e}"
            logger.error(error_msg)
            return False, "", error_msg

    # Create a temporary file list
    temp_file_list = 'temp_file_list.txt'
    try:
        with open(temp_file_list, 'w', encoding='utf-8') as f:
            for path in video_paths:
                f.write(f"file '{path}'\n")

        # Generate the output file path
        output_path = os.path.join(save_folder, f'result.mp4')

        # Build the FFmpeg command
        command = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', temp_file_list,
            '-c', 'copy',
            output_path
        ]
        # Execute the FFmpeg command
        subprocess.run(command, check=True)
        success_msg = f"The videos have been successfully merged and saved."
        logger.info(success_msg)
        return True, output_path, success_msg
    except subprocess.CalledProcessError as e:
        error_msg = f"Error: An error occurred while executing the FFmpeg command. Error message: {e}"
        logger.error(error_msg)
        return False, "", error_msg
    except Exception as e:
        error_msg = f"An unknown error occurred: {e}"
        logger.error(error_msg)
        return False, "", error_msg
    finally:
        # Delete the temporary file list
        if os.path.exists(temp_file_list):
            os.remove(temp_file_list)



# copy file and rename
def copy_file(source_file: str, target_folder: str, rename: str) -> tuple[bool, str]:
    if not os.path.isfile(source_file):
        return False, f"it is not a file, path {source_file}"

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Build target file and rename
    target_file = os.path.join(target_folder, rename)

    # Copy File
    shutil.copy2(source_file, target_file)
    return True, "success"


# end of functions -------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------



# MCP Service and Logger --------------------
logger = get_logger()
check_paths()

mcp = FastMCP(
    name="VideoEditorMCP",
    description="A video editing MCP tool service that has implemented " \
    "the basic functions among the fundamental functions.",
    version="0.1.4",

)

# --------------------------------
# MCP Tools ----------------------

# --------------------------------------------------------------------------
# mcp-tools注册
@mcp.tool()
def clip_video_tool(
        original_video_path: str,
        task_id: str,
        start_time: int,
        stop_time: int,
        title: str,
) -> dict:
    """
    Clip a video based on the given start and stop times.
    
    Parameters:
    original_video_path (str): The path of the original video file.
    task_id (str): The unique identifier for the clipping task.
    start_time (int): The start time (in some appropriate unit) for the clipping.
    stop_time (int): The stop time (in some appropriate unit) for the clipping.
    task_id (str): title: the title of the clipping.
    Returns:
    dict: A dictionary containing the result of the clipping operation.
          The dictionary has the following keys:
          - "success": A boolean indicating whether the operation was successful.
          - "message": A string providing additional information about the operation.
          - "output_path": The path of the clipped video file.
    """
    # In fact, both the `original_video_path` and `output_path` are based on the `KB_DIR`, 
    # that is, in the form of `$KB_DIR/xxxxx`. 
    # 
    # It is necessary to ensure that each input is based on the `KB_DIR``, 
    # and each output is also based on the KB. 
    # The reason for this design is mainly due to the concern that errors may occur 
    # when generating paths and other operations. 
    # Therefore, every effort is made to avoid such instability.  
    _original_video_path = os.path.join(KB_DIR, original_video_path)
    _save_folder = os.path.join(KB_DIR, KB_CLIP, task_id)
    success, output_path, message = clip_video(
        _original_video_path, _save_folder, start_time, stop_time, title)
    return {"success": success, "message": message, "output_path": output_path[len(KB_DIR)+1:]}



@mcp.tool()
def merge_videos_tool(video_paths: list[str], task_id: str) -> dict:
    """
    Merge multiple videos into one.

    Parameters:
    video_paths (list[str]): A list of paths of the video files to be merged.
    task_id (str): The unique identifier for the merging task.

    Returns:
    dict: A dictionary containing the result of the merging operation.
          The dictionary has the following keys:
          - "success": A boolean indicating whether the operation was successful.
          - "message": A string providing additional information about the operation.
          - "output_path": The path of the merged video file.
    """
    # the `video_paths` and `output_path` relative to the `KB_DIR``
    _video_paths = []
    for path in video_paths:
        _video_paths.append(os.path.join(KB_DIR, path))
        pass
    _save_folder = os.path.join(KB_DIR, KB_MERGE, task_id)
    success, output_path, message = merge_videos(_video_paths, _save_folder)

    return {"success": success, "message": message, "output_path": output_path[len(KB_DIR)+1:]}


def task_endding(task_id: str, source_file: str, title: str = "") -> str:
    """
    This function should be called every time a task ends to push the result document after task processing to the result folder.
    Parameters:
    task_id (str): Represents the ID of the current task, uniquely identifying the current task.
    source_file(str): Indicates the location of the result file to be pushed, 
    which is the file location provided after the previous process of this task ends.
    title(str): If you need to modify the file name (note: including the file extension), use this parameter. Otherwise, keep the file name the same as that of the source_file or simply don't input this parameter as there is a default parameter here.
    Returns:
    str: Returns "success" if successful, or an error message if failed. If an error occurs, notify the user of the reason for the error and apologize sincerely.
    """
    _source_file = os.path.join(KB_DIR, source_file)
    _target_dir = os.path.join(KB_DIR, KB_RESULT, task_id)
    if not os.path.exists(_target_dir):
        os.makedirs(_target_dir)

    if not os.path.exists(_source_file):
        return "This file does not exist. Please check if the path is correct."

    if len(title) == 0:
        _title = os.path.basename(source_file)
    else:
        _title = title

    try:
        _, msg = copy_file(_source_file, _target_dir, _title)
        return msg
    except Exception as e:
        return f"Error: {str(e)}"
    



if __name__ == "__main__":
    logger.info("Video Editor MCP Server Running......")
    mcp.run(transport='stdio')