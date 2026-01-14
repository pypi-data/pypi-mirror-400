<!---
Copyright 2026 The text-curation Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

<h1 align="center">text-curation</h1>

<p align="center">
  <strong>Profile-based text curation pipelines for Hugging Face Datasets</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/text-curation/">
    <img alt="PyPI version" src="https://img.shields.io/pypi/v/text-curation.svg">
  </a>
  <a href="https://pypi.org/project/text-curation/">
    <img alt="PyPI downloads" src="https://img.shields.io/pypi/dm/text-curation">
  </a>
  <a href="https://github.com/Dhiraj309/text-curation/blob/main/LICENSE">
    <img alt="License" src="https://img.shields.io/github/license/Dhiraj309/text-curation.svg">
  </a>
  <a href="https://github.com/Dhiraj309/text-curation/releases">
    <img alt="GitHub release" src="https://img.shields.io/github/release/Dhiraj309/text-curation.svg">
  </a>
  <a href="https://pypi.org/project/text-curation/">
    <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/text-curation.svg">
  </a>
</p>

---

## Overview

**text-curation** is a Python library for building **structured, profile-driven text curation pipelines**
designed to integrate naturally with **Hugging Face Datasets**.

The library focuses on **deterministic, inspectable text transformations** for preparing large-scale corpora
used in NLP and LLM training workflows.

Rather than providing ad-hoc cleaning scripts, `text-curation` encourages **explicit curation profiles**
that describe *what transformations are applied and why*.

---

## Design Principles

- **Profile-driven pipelines**  
  Reusable, declarative profiles define how text is curated for a given domain
  (e.g. web, wiki, news).

- **Composable blocks**  
  Each transformation is implemented as an isolated block that can be enabled,
  disabled, or reordered.

- **Deterministic and non-destructive**  
  Transformations are conservative by default and designed to preserve semantic content.

- **Structure-aware**  
  Text is treated as structured data (paragraphs, lists, headers), not just strings.

- **Dataset-scale friendly**  
  Built to operate efficiently with Hugging Face Datasets.

---

## Current Scope (v0.1.x)

`text-curation` currently provides **foundational, structure-aware text curation**
for real-world, messy text data.

The focus is on **deterministic preprocessing** rather than semantic classification
or ML-based filtering.

### Implemented Blocks

- **Normalization**
  - Unicode normalization (NFKC)
  - Quote, dash, and ellipsis normalization
  - Control character and zero-width cleanup

- **Formatting**
  - Whitespace normalization
  - Paragraph reconstruction
  - Punctuation spacing fixes
  - Code and indentation preservation

- **Redaction**
  - Email redaction
  - API token and credential masking
  - URL credential stripping

- **Structure**
  - Header, bullet, and numbered list detection
  - Paragraph and line-level signals
  - Repetition and boilerplate indicators

- **Filtering**
  - Empty document removal
  - Boilerplate paragraph filtering
  - List block suppression (configurable)

- **Deduplication**
  - Paragraph-level exact deduplication
  - Conservative, non-destructive defaults

More aggressive semantic filtering and fuzzy deduplication are intentionally
out of scope for v0.1.x and will be introduced behind explicit opt-in mechanisms
in later releases.

---

## Installation

`text-curation` supports **Python ≥ 3.9**.

Install from PyPI:

```bash
pip install text-curation
````

Or install from source for development:

```bash
git clone https://github.com/Dhiraj309/text-curation.git
cd text-curation
pip install -e .
```

---

## Quickstart

### Curating a Hugging Face Dataset

```python
from datasets import load_dataset
from text_curation import TextCurator

dataset = load_dataset(
    "allenai/c4",
    "en.noclean",
    split="train",
)

curator = TextCurator.from_profiles(profile_name="web_common_v1")

cleaned = dataset.map(
    curator,
    batched=True,
    num_proc=4,
)
```

The curator is a pure function that takes a batch dictionary and returns
a dictionary with the same schema.

---

## Profiles

Profiles define **which blocks are applied and in what order**.

Example (conceptual, simplified):

```python
web_common_v1 = [
    NormalizationBlock(),
    FormattingBlock(),
    RedactionBlock(),
    StructureBlock(),
    FilteringBlock(),
    DeduplicationBlock(),
]
```

Profiles are versioned to ensure **reproducibility** and **auditability**.

---

## Designed For

* Web-scale datasets (C4-like, Common Crawl, scraped corpora)
* OCR and PDF-derived text
* Forums, blogs, and user-generated content
* Dataset preprocessing prior to LLM training or evaluation

The library is intentionally **model-agnostic** and does not depend on
tokenizers, embeddings, or classifiers.

---

## Why text-curation?

* Cleaning text is not just normalization — **structure and repetition matter**
* Ad-hoc scripts do not scale or reproduce
* Dataset curation deserves the same rigor as model training
* Explicit pipelines make data decisions inspectable

`text-curation` is designed to be the **data-side analogue**
of model-definition libraries in the Hugging Face ecosystem.

---

## When should you *not* use text-curation?

* If you only need a one-off regex cleanup
* If your data is already fully curated
* If you require ML-based content classification (not in scope)

---

## Versioning & Stability

This project follows **semantic versioning**.

* `0.x` releases may introduce breaking changes
* Profiles are versioned explicitly (e.g. `web_common_v1`)
* Stable APIs will be formalized before `1.0.0`

---

## Contributing

Contributions are welcome.

If you plan to add new blocks or profiles, please:

* Keep transformations deterministic
* Avoid destructive defaults
* Include before/after examples

See `CONTRIBUTING.md` for details.

---

## License

Apache 2.0. See [LICENSE](LICENSE).

---

## Acknowledgements

Inspired by large-scale dataset curation practices
in the Hugging Face ecosystem.