import subprocess
import os
import threading
import time

HLS_BASE_DIR = "hls"

_supervised: dict[int, dict] = {}


def start_camera_hls(camera_id: int, rtsp_url: str):
    output_dir = f"{HLS_BASE_DIR}/camera_{camera_id}"
    os.makedirs(output_dir, exist_ok=True)

    # Use robust, low-latency H.264 encoding for better browser compatibility
    # Use TCP for RTSP inputs to improve reliability
    cmd = ["ffmpeg", "-fflags", "+genpts", "-max_muxing_queue_size", "1024"]
    if isinstance(rtsp_url, str) and rtsp_url.lower().startswith("rtsp://"):
        cmd += ["-rtsp_transport", "tcp"]
    cmd += ["-i", rtsp_url,
            # video: transcode to H.264 low-latency
            "-c:v", "libx264", "-preset", "veryfast", "-tune", "zerolatency", "-crf", "28", "-r", "15", "-g", "30",
            # audio
            "-c:a", "aac", "-b:a", "96k",
            # HLS output (mpeg-ts segments)
            "-f", "hls", "-hls_time", "2", "-hls_list_size", "6", "-hls_flags", "delete_segments+omit_endlist", "-hls_segment_type", "mpegts",
            f"{output_dir}/index.m3u8"]

    # Write ffmpeg logs to a file so we can inspect failures
    log_path = os.path.join(output_dir, "ffmpeg.log")
    try:
        log_file = open(log_path, "ab")
    except Exception:
        log_file = subprocess.DEVNULL

    try:
        process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=log_file
        )
        return process
    except Exception as e:
        try:
            if log_file not in (None, subprocess.DEVNULL):
                log_file.close()
        except Exception:
            pass
        print(f"Error starting FFmpeg for camera {camera_id}: {e}")
        return None


def _monitor_process(camera_id: int, rtsp_url: str, stop_event: threading.Event):
    """Monitor a ffmpeg process and restart with exponential backoff on exit."""
    backoff = 1
    max_backoff = 60
    while not stop_event.is_set():
        proc = None
        try:
            proc = start_camera_hls(camera_id, rtsp_url)
            if proc is None:
                # failed to start, wait and retry
                time.sleep(backoff)
                backoff = min(max_backoff, backoff * 2)
                continue
            # reset backoff on successful start
            backoff = 1

            # wait until process exits or stop_event is set
            while proc.poll() is None and not stop_event.is_set():
                time.sleep(1)

            # if stopped by request, ensure process is terminated
            if stop_event.is_set():
                try:
                    proc.terminate()
                except Exception:
                    pass
                break

            # process exited unexpectedly — log and restart after backoff
            try:
                with open(os.path.join(HLS_BASE_DIR, f"camera_{camera_id}", "ffmpeg.log"), "ab") as f:
                    f.write(b"\n[ffmpeg_supervisor] process exited, restarting...\n")
            except Exception:
                pass
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)

        except Exception:
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)
        finally:
            # cleanup local proc reference
            proc = None


def start_supervised_hls(camera_id: int, rtsp_url: str):
    """Start ffmpeg under a supervisor thread which restarts it on failure."""
    # If already supervised, return existing control dict
    existing = _supervised.get(camera_id)
    if existing:
        return existing

    stop_event = threading.Event()
    thread = threading.Thread(target=_monitor_process, args=(camera_id, rtsp_url, stop_event), daemon=True)
    control = {"thread": thread, "stop_event": stop_event}
    _supervised[camera_id] = control
    thread.start()
    return control


def stop_supervised_hls(camera_id: int):
    control = _supervised.pop(camera_id, None)
    if not control:
        return
    control["stop_event"].set()
    try:
        control["thread"].join(timeout=5)
    except Exception:
        pass


def restart_supervised_hls(camera_id: int, rtsp_url: str):
    stop_supervised_hls(camera_id)
    return start_supervised_hls(camera_id, rtsp_url)

def stop_camera_hls(process: subprocess.Popen):
    if process and process.poll() is None:
        process.terminate()
        process.wait()

def get_camera_hls_url(camera_id: int) -> str:
    return f"/hls/camera_{camera_id}/index.m3u8"

def is_hls_running(process: subprocess.Popen) -> bool:
    return process and process.poll() is None

def restart_camera_hls(camera_id: int, rtsp_url: str, process: subprocess.Popen) -> subprocess.Popen:
    stop_camera_hls(process)
    return start_camera_hls(camera_id, rtsp_url)    

def cleanup_hls_directory(camera_id: int):
    output_dir = f"{HLS_BASE_DIR}/camera_{camera_id}"
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        try:
            os.rmdir(output_dir)
        except Exception as e:
            print(f"Error deleting directory {output_dir}: {e}")

