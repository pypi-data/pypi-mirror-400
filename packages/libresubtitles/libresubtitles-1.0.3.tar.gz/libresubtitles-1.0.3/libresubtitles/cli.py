import argparse
import logging
from pathlib import Path

from libresubtitles.core.splitter import split_audio
from libresubtitles.core.stt import STT
from libresubtitles.core.srt import write_srt
from libresubtitles.core.audio import video_to_audio

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="LibreSubtitles - generate SRT subtitles from video/audio"
    )
    parser.add_argument(
        "-i", "--input", type=str, required=True, help="Path to the video or audio file"
    )
    parser.add_argument(
        "--device", type=str, default="cpu", required=False, help="hardware acceleration device cuda, mps, cpu"
    )
    args = parser.parse_args()
    video_path = args.input
    device = args.device

    if not Path(video_path).exists():
        logger.error(f"File not found: {video_path}")
        return

    logger.info("Converting video to audio...")
    audio_path = video_to_audio(video_path)

    logger.info("Splitting audio into chunks...")
    chunks = split_audio(audio_path)

    logger.info(f"Total chunks: {len(chunks)}")

    stt = STT(device)
    logger.info("Transcribing chunks (this may take a while)...")
    srt_lines = stt.transcribe_chunks(chunks)

    logger.info("Writing SRT file...")
    write_srt(srt_lines, video_path)
    logger.info("Done!")
