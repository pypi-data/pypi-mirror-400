class Document:
    def __init__(self, text: str):
        self.text = text
        self.annotations = {}
        self.signals = {}

    def set_text(self, text: str):
        self.text = text