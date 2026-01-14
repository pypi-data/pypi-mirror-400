from indiayz.core.base import BaseModule

class Voice(BaseModule):
    @staticmethod
    def tts(text: str):
        return Voice._post("/audio/tts", {"text": text})
