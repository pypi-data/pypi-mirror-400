from text_curation.profiles.web_common_v1 import PIPELINE

class TextCurator:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    @classmethod
    def from_profiles(cls, profile_name: str, dataset: str | None = None):
        if profile_name != "web_common_v1":
            raise ValueError(f"Unknown Profile: {profile_name}")
        return cls(PIPELINE)
    
    def __call__(self, batch):
        texts = batch["text"]
        cleaned = [self.pipeline.run(t) for t in texts]

        return {"text": cleaned}