from indiayz.core.base import BaseModule

class Image(BaseModule):
    @staticmethod
    def generate(prompt: str):
        return Image._post("/image", {"prompt": prompt})
