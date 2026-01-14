from pathlib import Path
import shutil
import subprocess
import sys

from gstreamer_runtime import gstreamer_env


def __run(program: str):
    env, runtime_path = gstreamer_env()
    fullpath = shutil.which(program, path=runtime_path)
    if not fullpath:
        raise RuntimeError(f'{program} was not found in {runtime_path}')
    fullpath = str(Path(fullpath).resolve())
    subprocess.check_call([fullpath, *sys.argv[1:]], env=env)


def gst_device_monitor_1_0():
    __run('gst-device-monitor-1.0')
def gst_discoverer_1_0():
    __run('gst-discoverer-1.0')
def gst_inspect_1_0():
    __run('gst-inspect-1.0')
def gst_launch_1_0():
    __run('gst-launch-1.0')
def gst_play_1_0():
    __run('gst-play-1.0')
def gst_shell():
    __run('gst-shell')
def gst_typefind_1_0():
    __run('gst-typefind-1.0')
def ges_launch_1_0():
    __run('ges-launch-1.0')
def gst_dots_viewer():
    __run('gst-dots-viewer')
def gst_validate_1_0():
    __run('gst-validate-1.0')
def gst_validate_launcher():
    __run('gst-validate-launcher')
def gst_validate_media_check_1_0():
    __run('gst-validate-media-check-1.0')
def gst_validate_rtsp_server_1_0():
    __run('gst-validate-rtsp-server-1.0')
def gst_validate_transcoding_1_0():
    __run('gst-validate-transcoding-1.0')
