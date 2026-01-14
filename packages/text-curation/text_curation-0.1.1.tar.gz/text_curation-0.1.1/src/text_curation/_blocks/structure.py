import re
from collections import Counter

_HEADER_RE = re.compile(r"^(#{1,6}\s+.+|[A-Z][A-Z\s0-9:]{5,})$")

_BULLET_RE = re.compile(r"^\s*[-*.]\s+")

_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+")

_ALL_CAPS_RE = re.compile(r"^[A-Z\s0-9.,!?:;'\"-]+$")

class StructureBlock:
    def apply(self, document):
        lines = document.text.split("\n")
        paragraphs = self._split_paragraphs(lines)

        line_counts = Counter(l.strip() for l in lines if l.strip())

        para_counts = Counter(p.strip() for p in paragraphs if p.strip())

        for i, line in enumerate(lines):
            self._emit_line_signals(document, i, line, line_counts)

        for i, para, in enumerate(paragraphs):
            self._emit_paragraph_signals(document, i, para, para_counts)

        return document

    def _split_paragraphs(self, lines):
        paras = []
        buffer =  []

        for line in lines:
            if not line.strip():
                if buffer:
                    paras.append("\n".join(buffer))
                    buffer = []

            else:
                buffer.append(line)

        if buffer:
            paras.append("\n".join(buffer))

        return paras
    
    def _emit_line_signals(self, document, idx, line, counts):
        stripped = line.strip()

        document.add_signal(f"line[{idx}].is_blank", not stripped)
        document.add_signal(f"line[{idx}].is_header", bool(_HEADER_RE.match(stripped)))
        document.add_signal(f"line[{idx}].is_bullet", bool(_BULLET_RE.match(stripped)))
        document.add_signal(f"line[{idx}].is_numbered_item", bool(_NUMBERED_RE.match(stripped)))
        document.add_signal(f"line[{idx}].is_all_caps", bool(_ALL_CAPS_RE.match(stripped)) if stripped else False)
        document.add_signal(f"line[{idx}].is_short", len(stripped) < 20)
        document.add_signal(f"line[{idx}].repetition_count", counts.get(stripped, 0),)

    def _emit_paragraph_signals(self, document, idx, para, counts):
        stripped = para.strip()
        lines = stripped.split("\n") if stripped else []

        bullet_lines = sum(bool(_BULLET_RE.match(l)) for l in lines)
        numbered_lines = sum(bool(_NUMBERED_RE.match(l)) for l in lines)

        is_list_block = (
            (bullet_lines + numbered_lines) >= len(lines) / 2
            if lines
            else False
        )

        document.add_signal(f"paragraph[{idx}].is_list_block", is_list_block,)
        document.add_signal(f"paragraph[{idx}].is_boilerplate_candidate", counts.get(stripped, 0) >= 2,)
        document.add_signal(f"paragraph[{idx}].repetition_count", counts.get(stripped, 0),)