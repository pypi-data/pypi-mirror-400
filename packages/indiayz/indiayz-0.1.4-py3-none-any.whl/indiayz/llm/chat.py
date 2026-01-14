from indiayz.core.base import BaseModule

class Chat(BaseModule):
    @staticmethod
    def ask(prompt: str):
        instance = Chat()
        result = instance._post("/api/chat", {"prompt": prompt})
        return result.get("response", "")
