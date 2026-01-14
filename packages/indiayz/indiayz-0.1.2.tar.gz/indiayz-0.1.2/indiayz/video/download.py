from indiayz.core.base import BaseModule

class Video(BaseModule):
    @staticmethod
    def download(url: str):
        return Video._post("/video/download", {"url": url})
