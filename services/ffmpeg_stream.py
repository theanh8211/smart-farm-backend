import subprocess
import os

HLS_BASE_DIR = "hls"

def start_camera_hls(camera_id: int, rtsp_url: str):
    output_dir = f"{HLS_BASE_DIR}/camera_{camera_id}"
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-rtsp_transport", "tcp",
        "-i", rtsp_url,
        "-c:v", "copy",
        "-c:a", "aac",
        "-f", "hls",
        "-hls_time", "2",
        "-hls_list_size", "6",
        "-hls_flags", "delete_segments",
        f"{output_dir}/index.m3u8"
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return process
    except Exception as e:
        print(f"Error starting FFmpeg for camera {camera_id}: {e}")
        return None  # Trả None để endpoint xử lý lỗi

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

