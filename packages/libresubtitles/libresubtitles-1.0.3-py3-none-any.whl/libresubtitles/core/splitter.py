from pydub import AudioSegment, silence
from pathlib import Path
from libresubtitles.core.globals import MIN_SILENCE_LEN, SILENCE_THRESH, KEEP_SILENCE


def split_audio(audio_path: str):
    audio = AudioSegment.from_wav(audio_path)

    nonsilient_ranges = silence.detect_nonsilent(
        audio,
        min_silence_len=MIN_SILENCE_LEN,
        silence_thresh=audio.dBFS - SILENCE_THRESH,
    )

    chunks = []
    for start_ms, end_ms in nonsilient_ranges:
        start = max(0, start_ms - KEEP_SILENCE)
        end = min(len(audio), end_ms + KEEP_SILENCE)
        chunk_audio = audio[start:end]
        chunks.append((chunk_audio, start_ms / 1000))
    return chunks
