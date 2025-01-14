# Confluence RAG Chatbot

![Project Logo](path/to/logo.png) <!-- Optional: Add a project logo -->

## 📝 Table of Contents

- [📖 Introduction](#-introduction)
- [🚀 Features](#-features)
- [📂 Project Structure](#-project-structure)
- [🛠️ Installation](#️-installation)
- [🔧 Configuration](#-configuration)
- [🐳 Docker Setup](#-docker-setup)
- [☁️ Deployment on AWS](#️-deployment-on-aws)
- [💬 Usage](#-usage)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📫 Contact](#-contact)

## 📖 Introduction

The **Confluence RAG (Retrieval-Augmented Generation) Chatbot** is an intelligent chatbot designed to interact with your organization's Confluence documentation. It scrapes content from Confluence pages, stores the data in AWS S3 and Amazon OpenSearch, and provides an interactive Streamlit-based UI for users to query the knowledge base seamlessly.

## 🚀 Features

- **Confluence Scraping**: Extracts text, tables, and images from Confluence pages up to a specified depth.
- **AWS Integration**: Stores scraped data and images in Amazon S3 and utilizes Amazon OpenSearch for efficient querying.
- **Knowledge Base**: Leverages vector embeddings for semantic search using Sentence Transformers.
- **Interactive UI**: User-friendly Streamlit interface for querying and interacting with the chatbot.
- **Containerization**: Dockerized application for easy deployment and scalability.
- **AWS Deployment**: Deployable on AWS ECS Fargate for a serverless and scalable infrastructure.

## 📂 Project Structure

confluence-rag-chatbot/ ├── app.py # Streamlit app entry point ├── confluence_scraper │ ├── init.py │ └── scraper.py # Logic to scrape Confluence pages ├── knowledge_base │ ├── init.py │ └── opensearch_kb.py # OpenSearch integration ├── s3_storage │ ├── init.py │ └── upload.py # AWS S3 upload logic ├── requirements.txt # Python dependencies ├── Dockerfile # Docker configuration ├── .env.example # Sample environment variables └── README.md # Project documentation

## 🛠️ Installation

### Prerequisites

- **Python 3.9+**
- **Docker** (for containerization)
- **AWS Account** with permissions to use S3, OpenSearch, and ECS
- **AWS CLI** configured with your credentials

### Clone the Repository

```bash
git clone https://github.com/yourusername/confluence-rag-chatbot.git
cd confluence-rag-chatbot
```
