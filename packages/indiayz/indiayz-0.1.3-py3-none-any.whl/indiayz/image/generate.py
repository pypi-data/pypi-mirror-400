from indiayz.core.base import BaseModule

class Image(BaseModule):
    @staticmethod
    def generate(prompt: str):
        instance = Image()
        return instance._post("/api/image", {"prompt": prompt})
