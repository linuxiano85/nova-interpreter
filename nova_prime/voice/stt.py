import numpy as np
from typing import Optional

class STTSession:
    """
    Speech-to-text using faster-whisper.
    
    Note: This is a placeholder implementation. The actual implementation
    requires the faster-whisper package which is only installed with [nova-prime] extras.
    """
    
    def __init__(self, model_size: str = "small", samplerate: int = 16000):
        self.model_size = model_size
        self.samplerate = samplerate
        self._recording = False
        self._frames = []
        self._stream = None
        self._model = None
        
        # Try to import optional dependencies
        try:
            import sounddevice as sd
            import faster_whisper
            self._sd = sd
            self._model = faster_whisper.WhisperModel(model_size, compute_type="int8")
        except ImportError:
            self._sd = None
            self._model = None

    def start_recording(self):
        if self._recording or not self._sd:
            return
        self._frames = []
        self._recording = True
        self._stream = self._sd.InputStream(
            channels=1, samplerate=self.samplerate, dtype="float32", callback=self._cb
        )
        self._stream.start()

    def _cb(self, indata, frames, time, status):
        if self._recording:
            self._frames.append(indata.copy())

    def stop_and_transcribe(self) -> str:
        if not self._recording or not self._sd or not self._model:
            return ""
        self._recording = False
        self._stream.stop()
        self._stream.close()
        
        try:
            audio = np.concatenate(self._frames, axis=0).flatten().astype(np.float32)
            segments, info = self._model.transcribe(audio, language=None, vad_filter=True)
            text = "".join(seg.text for seg in segments) if segments else ""
            return text.strip()
        except Exception:
            return ""