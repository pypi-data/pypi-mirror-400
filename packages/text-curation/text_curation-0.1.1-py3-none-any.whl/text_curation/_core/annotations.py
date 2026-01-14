class Region:
    def __init__(self, kind: str, start: str, end: str, data: None):
        self.kind = kind
        self.start = start
        self.end = end
        self.data = data or {}