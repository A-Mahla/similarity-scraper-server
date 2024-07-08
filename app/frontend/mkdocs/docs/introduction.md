# Introduction

## Overview

The Similarity Scraper Engine is designed to facilitate the extraction of critical information from webpages and manage data samples efficiently. It employs advanced techniques for scraping text and images, managing data samples, and assessing similarity.


### Main Features

- **Web Scraping**: Extract the most relevant text or images from HTML pages using sophisticated algorithms based on a tree graph and attributes like depth, child element count, text density, and tag matching.

- **Data Embeddings**: Utilize [clip-ViT-B-32-multilingual-v1](https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1) transformer model to produce embeddings, and so, apply cosine similarity metrics to remove texts with similar meanings from your dataset.

- **Sample Management**: Handle data operations on MongoDB, including adding, retrieving, and deleting data samples.

These features ensure that the engine not only scrapes web content but also maintains a high-quality, non-redundant dataset.