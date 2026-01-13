import subprocess
import json

def get_stream_url(
    video_url: str,
    cookies_path: str = None,
    mode: str = "audio"   # "audio" | "video"
) -> str | None:
    try:
        if mode == "video":
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
            extra = ["--merge-output-format", "mp4"]
        else:
            fmt = "bestaudio[ext=m4a]/bestaudio"
            extra = []

        cmd = [
            "yt-dlp",
            "-j",
            "-f", fmt,
            "--no-playlist",
            "--no-check-certificate",
            *extra
        ]

        if cookies_path:
            cmd += ["--cookies", cookies_path]

        cmd.append(video_url)

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print("❌ yt-dlp error:", result.stderr)
            return None

        data = json.loads(result.stdout)
        return data.get("url")

    except Exception as e:
        print(f"❌ Error extracting stream URL: {e}")
        return None
