import subprocess
import re
from tqdm import tqdm
from libresubtitles.core.globals import SAMPLE_RATE


def video_to_audio(video_path: str) -> str:
    audio_path = video_path.rsplit(".", 1)[0] + ".wav"

    process = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-ac",
            "1",
            "-ar",
            str(SAMPLE_RATE),
            audio_path,
        ],
        check=True,
    )

    return audio_path
