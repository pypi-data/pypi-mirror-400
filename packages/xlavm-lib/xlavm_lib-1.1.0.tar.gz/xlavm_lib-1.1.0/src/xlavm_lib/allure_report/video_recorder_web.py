import subprocess
import os
import time
import imageio_ffmpeg

class VideoRecorderWeb:
    def __init__(self, output_path):
        self.output_path = output_path
        self.process = None
        self.ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    def start(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        self.process = subprocess.Popen(
            [
                self.ffmpeg,
                "-y",
                "-f", "gdigrab",
                "-framerate", "30",
                "-video_size", "1920x1080",
                "-i", "desktop",
                "-vcodec", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                self.output_path
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        time.sleep(1) # deja que FFmpeg escriba headers

    def stop(self):
        if not self.process:
            return
        try:
            # CIERRE CORRECTO
            self.process.stdin.write(b"q\n")
            self.process.stdin.flush()
            self.process.wait(timeout=3) # esperar máximo 3s
        except Exception:
            # fallback si ffmpeg no responde
            self.process.kill()
