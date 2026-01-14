from collections import defaultdict

class FilteringBlock:
    def apply(self, document):
        text = document.text
        if not text.strip():
            document.set_text("")
            return document
        
        paragraphs = text.split("\n\n")
        signals = document.signals

        para_signals = self._group_paragraph_signals(signals)
        kept_paragraphs = []

        for idx, para in enumerate(paragraphs):
            sigs = para_signals.get(idx, {})

            if self._should_drop_paragraph(para, sigs):
                continue

            kept_paragraphs.append(para)

        document.set_text("\n\n".join(kept_paragraphs))
        return document

    def _should_drop_paragraph(self, paragraph: str, sigs: dict) -> bool:
        stripped = paragraph.strip()
        if not stripped:
            return True
        
        if (
            sigs.get("is_boilerplate_candidate")
            and sigs.get("repetition_count", 0) >=2
            and len(stripped) < 200
        ):
            return True
        
        if sigs.get("is_list_blocks"):
            avg_line_len = sum(len(l) for l in stripped.split("\n")) / max(1, len(stripped.split("\n")))
            if avg_line_len < 40:
                return True
            
        return False
    

    def _group_paragraph_signals(self, signals):
        grouped = defaultdict(dict)

        for sig in signals:
            if not sig.name.startswith("paragraph["):
                continue

            prefix, key = sig.name.split("].", 1)
            idx = int(prefix[len("paragraph[") :])

            grouped[idx][key] = sig.value

        return grouped
    