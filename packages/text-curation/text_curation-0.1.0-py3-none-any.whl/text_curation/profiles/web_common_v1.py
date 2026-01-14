from text_curation.blocks import (
    NormalizationBlock,
    FilteringBlock,
    FormattingBlock,
    StrucutureBlock,
    RedactionBlock,
)

from text_curation.core.pipeline import Pipeline

PIPELINE = Pipeline(
    blocks = [
        RedactionBlock(),
        NormalizationBlock(),
        FormattingBlock(),
        StrucutureBlock(),
        FilteringBlock()
    ]
)