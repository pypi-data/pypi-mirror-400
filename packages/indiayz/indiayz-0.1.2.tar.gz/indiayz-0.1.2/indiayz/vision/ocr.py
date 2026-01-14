from indiayz.core.base import BaseModule

class Vision(BaseModule):
    @staticmethod
    def read(image_url: str):
        return Vision._post("/vision/ocr", {"image_url": image_url})
