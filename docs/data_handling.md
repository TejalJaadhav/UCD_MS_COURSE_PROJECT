# Data Handling Decisions

## Source Text

Models will receive the saved source title and source text.
The same input format will be used for each method.

Human-selected evidence will be kept out of model inputs because
it is part of the human annotation.

## Short Sources

A short source will not be removed only because it has few words.

Before using a short source, check whether its title and text
provide enough information to assess the claim. Mark records
with too little saved information for review.

Do not change the original dataset labels based on missing source text.

## Long Sources

Long sources may need to be divided into sections to fit the model.
We will choose the section size after choosing a model and checking
how much text it can read.

## Dataset Splits

Keep the official train, development, and test splits.

Use training data to develop methods, development data to compare
settings, and test data for final evaluation.