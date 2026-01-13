import tempfile
import whisper
import os
from tqdm import tqdm
from libresubtitles.core.globals import MODEL_DIR


class STT:
    def __init__(self, device):
        self.model = self.load_model(device)

    def load_model(self, device, model_name="tiny"):
        os.makedirs(MODEL_DIR, exist_ok=True)
        os.environ["XDG_CACHE_HOME"] = MODEL_DIR
        model = whisper.load_model(model_name, device=device)
        return model

    def transcribe_audio(self, file_path: str):
        result = self.model.transcribe(file_path, fp16=False)
        return result["segments"]

    def transcribe_chunks(self, chunks):
        srt_lines = []
        srt_index = 1

        for chunk, chunk_start in tqdm(chunks):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                chunk.export(f.name, format="wav")
                segments = self.transcribe_audio(f.name)
                for seg in segments:
                    start = seg["start"] + chunk_start
                    end = seg["end"] + chunk_start
                    text = seg["text"].strip()
                    srt_lines.append([srt_index, start, end, text])
                    srt_index += 1
        return srt_lines
