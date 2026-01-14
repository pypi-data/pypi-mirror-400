class Pipeline:
    def __init__(self, blocks):
        self.blocks = blocks

    def run(self, text: str) -> str:
        from .document import Document

        document = Document(text)

        for block in self.blocks:
            block.apply(document)

        return document.text