from pathlib import Path


def format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def write_srt(srt_lines, video_path: str):

    video_path = Path(video_path)
    srt_path = video_path.with_suffix(".srt")

    with srt_path.open("w", encoding="utf-8") as f:
        for index, start, end, text in srt_lines:
            f.write(f"{index}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")

    return srt_path
