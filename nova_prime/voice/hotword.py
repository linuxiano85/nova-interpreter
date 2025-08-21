import threading
import queue
import numpy as np
from typing import Optional, Callable

class HotwordListener:
    """
    Wake word detection using openwakeword.
    
    Note: This is a placeholder implementation. The actual implementation
    requires the openwakeword package which is only installed with [nova-prime] extras.
    """
    
    def __init__(self, phrase: str = "hey nova", samplerate: int = 16000, blocksize: int = 512):
        self.phrase = phrase
        self.samplerate = samplerate
        self.blocksize = blocksize
        self._stream = None
        self._q = queue.Queue()
        self._running = False
        self._model = None
        self._threshold = 0.5
        self.on_trigger: Optional[Callable[[], None]] = None
        
        # Try to import optional dependencies
        try:
            import sounddevice as sd
            import openwakeword.model
            self._sd = sd
            self._model = openwakeword.model.Model()
        except ImportError:
            self._sd = None
            self._model = None

    def _audio_cb(self, indata, frames, time, status):
        if status:
            pass
        mono = indata.copy()
        if mono.ndim == 2 and mono.shape[1] > 1:
            mono = np.mean(mono, axis=1, keepdims=True)
        self._q.put(mono)

    def start(self):
        if self._running or not self._sd or not self._model:
            return
        self._running = True
        self._stream = self._sd.InputStream(
            channels=1,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype="float32",
            callback=self._audio_cb,
        )
        self._stream.start()
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def _loop(self):
        phrase_keys = [self.phrase.replace(" ", "_"), "hey_nova", "hey_computer"]
        while self._running:
            try:
                block = self._q.get(timeout=0.2)
            except queue.Empty:
                continue
            scores = self._model.predict(block)
            score = 0.0
            if isinstance(scores, dict):
                for k, v in scores.items():
                    if any(pk in k for pk in phrase_keys):
                        score = max(score, float(v))
            else:
                try:
                    score = float(max(scores))
                except Exception:
                    score = 0.0
            if score >= self._threshold and self.on_trigger:
                self.on_trigger()