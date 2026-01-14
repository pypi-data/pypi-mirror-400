class StrucutureBlock:
    def apply(self, document):
        text = document.text
        lines = text.split("\n")

        regions = []
        if lines:
            regions.append(("HEADLINE", 0, len(lines[0])))

        document.annotations["regions"] = regions