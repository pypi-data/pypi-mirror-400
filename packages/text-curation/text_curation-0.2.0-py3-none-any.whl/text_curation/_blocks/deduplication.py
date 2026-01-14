class DeduplicationBlock:
    def apply(self, document):
        text = document.text

        if not text.strip():
            return document
        
        paragraphs = text.split("\n\n")

        seen = set()
        kept = []

        for para in paragraphs:
            key = self._normalize_key(para)

            if not key:
                continue
            if key in seen:
                continue

            seen.add(key)
            kept.append(para)

        document.set_text("\n\n".join(kept))
        return document

    def _normalize_key(self, paragraph: str) -> str:
        return "".join(paragraph.split()).lower()