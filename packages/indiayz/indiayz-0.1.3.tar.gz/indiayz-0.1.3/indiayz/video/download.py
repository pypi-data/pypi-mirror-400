from indiayz.core.base import BaseModule

class Video(BaseModule):
    @staticmethod
    def download(url: str):
        instance = Video()
        return instance._post("/api/video", {"url": url})
