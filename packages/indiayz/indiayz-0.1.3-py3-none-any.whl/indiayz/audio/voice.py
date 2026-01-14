from indiayz.core.base import BaseModule

class Audio(BaseModule):
    @staticmethod
    def tts(text: str):
        instance = Audio()
        return instance._post("/api/audio", {"text": text})
