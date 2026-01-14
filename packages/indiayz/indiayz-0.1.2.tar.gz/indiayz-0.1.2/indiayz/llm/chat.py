from indiayz.core.base import BaseModule

class Chat(BaseModule):
    @staticmethod
    def ask(prompt: str):
        return Chat._post("/chat", {"prompt": prompt}).get("response", "")
