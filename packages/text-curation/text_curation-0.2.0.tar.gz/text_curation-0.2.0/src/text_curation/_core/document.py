from text_curation._core.signals import Signal

class Document:
    def __init__(self, text: str):
        self.text = text
        self.annotations = {}
        self.signals: list[Signal] = []

    def set_text(self, text: str):
        self.text = text

    def add_signal(self, name: str, value):
        self.signals.append(Signal(name, value))