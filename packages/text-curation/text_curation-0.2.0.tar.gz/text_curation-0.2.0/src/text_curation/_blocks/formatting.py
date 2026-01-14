import re
_CODE_INDENT = re.compile(r"^[ \t]+")

_URL = re.compile(r"https?://\S+")
_EMAIL = re.compile(r"\b\S+@\S+\b")
_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

class FormattingBlock:
    def apply(self, document):
        text = document.text

        text = self._normalize_line_endings(text)
        text = self._trim_trailing_white_spaces(text)
        text = self._collapse_blank_lines(text)
        text = self._normalize_paragraph_boundries(text)
        text = self._normalize_punctuation_spacing(text)

        document.set_text(text)
        return document

    def _normalize_line_endings(self, text):
        return text.replace("\r\n", "\n").replace("\r", "\n")
    
    def _trim_trailing_white_spaces(self, text):
        return "\n".join(line.rstrip() for line in text.split("\n"))
    
    def _collapse_blank_lines(self, text):
        return re.sub(r"\n{3,}", "\n\n", text)
    
    def _normalize_paragraph_boundries(self, text):
        lines = text.split("\n")
        out = []
        buffer = []

        for line in lines:
            # Code / indented lines: flush buffer, preserve exactly
            if _CODE_INDENT.match(line):
                if buffer:
                    out.extend(buffer)   # ❌ do NOT merge
                    buffer = []
                out.append(line)
                continue

            # Blank line: paragraph terminator → merge
            if not line.strip():
                if buffer:
                    out.append(" ".join(buffer))  # ✅ merge ONLY here
                    buffer = []
                out.append("")
                continue

            # Normal line → buffer it
            buffer.append(line.strip())

        # EOF: no blank line → do NOT merge
        if buffer:
            out.extend(buffer)

        return "\n".join(out)
    
    # def _normalize_punctuation_spacing(self, text):
    #     text = re.sub(r"\s+([,;:!?])", r"\1", text)
    #     text = re.sub(r"([,;:!?])([^\s])", r"\1 \2", text)

    #     return text

    def _normalize_punctuation_spacing(self, text):
        # 1️⃣ Collapse repeated punctuation
        text = re.sub(r"([!?]){2,}", r"\1", text)
        text = re.sub(r"\.{4,}", "...", text)

        # 2️⃣ Protect structured tokens
        placeholders = {}

        def stash(match):
            key = f"__TOK{len(placeholders)}__"
            placeholders[key] = match.group(0)
            return key

        text = _URL.sub(stash, text)
        text = _EMAIL.sub(stash, text)
        text = _IP.sub(stash, text)

        # 3️⃣ Safe spacing (NO DOTS!)
        text = re.sub(r"\s+([,!?;:])", r"\1", text)
        text = re.sub(r"([,!?;:])([^\s])", r"\1 \2", text)

        # 4️⃣ Restore tokens
        for k, v in placeholders.items():
            text = text.replace(k, v)

        return text