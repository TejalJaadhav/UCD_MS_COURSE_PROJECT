# Evaluating Evidential Support of Citations in AI-Generated Content

**Author:** Tejal Jadhav  
**Course:** CSCI 6970 – MS Course Project  
**Term:** Fall 2026

## Overview

This project investigates whether cited sources support AI-generated
claims and which specific claim components are supported, unsupported,
or contradicted by the evidence.

## Research Questions

1. How accurately can NLP methods classify overall citation support?
2. Can claim decomposition and evidence alignment identify the specific
   components that are supported, unsupported, or contradicted?
3. Which types of evidential mismatch are most difficult to detect?

## Planned Methods

- Whole-claim Natural Language Inference (NLI) baseline
- Prompted Large Language Model (LLM) baseline
- Component-level claim decomposition and evidence alignment

## Dataset

The project uses the dataset accompanying Liu, Zhang, and Liang (2023),
“Evaluating Verifiability in Generative Search Engines.”

Dataset repository:
https://github.com/nelson-liu/evaluating-verifiability-in-generative-search-engines

Original dataset files are stored locally in data/raw/ and excluded
from Git. The official train, development, and test splits are preserved.

## Repository Structure

- data/: Dataset documentation and local data
- src/data/: Data loading and preprocessing
- src/baselines/: NLI and LLM baselines
- src/fine_grained/: Component-level support evaluation
- src/evaluation/: Metrics and error analysis
- annotation/: Manual annotation guidelines and labels
- configs/: Experiment settings
- notebooks/: Exploratory analysis
- docs/: Project documentation
- tests/: Code verification

Generated experiment artifacts will be stored locally in outputs/.

## Current Status

Repository setup and initial dataset inspection.
Model implementation and experiments have not started.
