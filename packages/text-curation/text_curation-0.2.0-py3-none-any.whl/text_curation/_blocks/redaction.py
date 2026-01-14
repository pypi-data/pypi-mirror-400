import re

_EMAIL = re.compile(
    r"\b[a-zA-Z0-9._%+-]+"
    r"@"
    r"[a-zA-Z0-9.-]+"
    r"\.[a-zA-Z]{2,}\b"
)

_API_TOKEN = re.compile(
    r"""
    \b(
        # Common known prefixes
        sk-[A-Za-z0-9_-]{16,} |
        hf_[A-Za-z0-9_-]{16,} |
        ghp_[A-Za-z0-9_-]{16,} |
        api_[A-Za-z0-9_-]{16,} |
        key_[A-Za-z0-9_-]{16,} |

        # Generic high-entropy tokens (fallback)
        [A-Za-z0-9_-]{32,}
    )\b
    """,
    re.VERBOSE
)


_URL_CREDENTIAL = re.compile(
    r"(https?://)"
    r"[^/\s:@]+"
    r":"
    r"[^@\s]+"
    r"@"
)


class RedactionBlock:
    def apply(self, document):
        text = document.text

        text = self._redact_url_credentials(text)
        text = self._redact_emails(text)
        text = self._redact_api_tokens(text)

        document.set_text(text)
    
    def _redact_emails(self, text):
        return _EMAIL.sub("<EMAIL>", text)
    
    def _redact_api_tokens(self, text):
        return _API_TOKEN.sub("<TOKEN>", text)
    
    def _redact_url_credentials(self, text):
        return _URL_CREDENTIAL.sub(r"\1<REDACTED>@", text)