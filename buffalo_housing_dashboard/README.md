# Buffalo Housing Data: RAG Retrieval Pipeline 🏘️

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-FF6F00.svg)
![LLaMA3](https://img.shields.io/badge/LLM-LLaMA_3-0466C8.svg)

## 📌 Project Overview
This repository contains a **Retrieval-Augmented Generation (RAG)** pipeline developed to process and search unstructured housing data. Originally designed during my tenure as a Research Assistant & Data Engineer at the University at Buffalo, this system ingests complex, unstructured data sources (such as video transcripts and OCR text) and makes them semantically searchable. 

The pipeline leverages localized LLM generation via **LLaMA 3** and utilizes **ChromaDB** for efficient vector storage and retrieval.

![RAG Pipeline Architecture](link-to-your-uploaded-image-here.png)
*(Note: Upload the pipeline image to your repo and replace this link with the relative path, e.g., `./images/pipeline.png`)*

## 🚀 Key Engineering Features
* **Unstructured Data Ingestion:** Designed a robust pipeline to ingest, clean, and vectorize raw video transcripts and OCR-extracted text.
* **Vector Search Optimization:** Refreshed vector indexes and optimized metadata schemas within **ChromaDB** to ensure data consistency and fast retrieval times.
* **Semantic Retrieval:** Replaced traditional keyword search with similarity-based vector retrieval using `sentence-transformers`.
* **Local LLM Integration:** Wrapped the architecture to run completely locally using **Ollama** and **LLaMA 3**, allowing open-source contributors to run and modify the project without cloud compute costs.

## 🛠️ Technology Stack
* **Language:** Python 3.10+
* **Vector Database:** ChromaDB
* **Embeddings:** HuggingFace `sentence-transformers` (`all-MiniLM-L6-v2`)
* **LLM Engine:** LLaMA 3 (executed locally via Ollama)

## 💻 Getting Started (Local Development)

To run this pipeline on your local machine, follow these steps:

### 1. Clone the Repository
```bash
git clone [https://github.com/Pratyusha-Adibhatla99/buffalo-housing-rag.git](https://github.com/Pratyusha-Adibhatla99/buffalo-housing-rag.git)
cd buffalo-housing-rag
