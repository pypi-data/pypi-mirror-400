class FilteringBlock:
    def apply(self, document):
        if not document.text.strip():
            document.set_text("")