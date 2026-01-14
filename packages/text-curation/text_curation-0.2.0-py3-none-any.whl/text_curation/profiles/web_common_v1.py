from text_curation._blocks import (
    NormalizationBlock,
    FilteringBlock,
    FormattingBlock,
    StructureBlock,
    RedactionBlock,
    DeduplicationBlock
)

from text_curation._core.pipeline import Pipeline

PIPELINE = Pipeline(
    blocks = [
        RedactionBlock(),
        NormalizationBlock(),
        FormattingBlock(),
        StructureBlock(),
        FilteringBlock(),
        DeduplicationBlock(),
    ]
)