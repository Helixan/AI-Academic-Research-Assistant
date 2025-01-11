# AI Academic Research Assistant

Welcome to the AI Academic Research Assistant, an application designed to enhance academic research workflows. This tool enables users to manage, search, and analyze research papers using advanced AI models and vector search technologies. Below is a comprehensive guide to set up, configure, and use the application.

## Features
- **User and Paper Management**: RESTful APIs to manage users and papers.
- **PDF Parsing**: Extract text from PDF files and save them to a database.
- **Semantic Search**: Search for research papers using natural language queries.
- **Text Summarization**: Summarize research papers for quick insights.
- **Customizable Storage**: Support for in-memory or Pinecone-based vector storage.
- **Agents for Enhanced Functionality**:
  - **SummarizerAgent**: Provides concise summaries of academic papers.
  - **ResearchAgent**: Performs semantic search and retrieval of relevant papers.
  - **LitReviewAgent**: Facilitates comprehensive literature reviews by recommending local and external papers based on user-provided topics or existing papers.

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [API Endpoints](#api-endpoints)
5. [License](#license)

---

## Installation

### Prerequisites
- Python 3.8+
- MySQL or compatible database
- pip

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Helixan/AI-Academic-Research-Assistant.git
   cd ai-academic-research-assistant
   ```
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure the database and API keys (see [Configuration](#configuration)).
5. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

---

## Configuration

### `config/config.yaml`
Define environment variables and configurations in `config/config.yaml`.

```yaml
environment: development

openai_api_key: YOUR_KEY

database:
  url: YOUR_DB_URL

test_database:
  url: YOUR_TEST_DB_URL

vector_store:
  type: pinecone
  api_key: YOUR_PINECONE_KEY
  environment: "us-east-1"
  index_name: "my-index"
```

### Logging
Logging is configured via `config/logging.yaml`:
```yaml
version: 1
formatters:
  simple:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

handlers:
  console:
    class: logging.StreamHandler
    formatter: simple
    level: DEBUG
    stream: ext://sys.stdout

root:
  level: DEBUG
  handlers: [console]
```

---

## Usage

### Endpoints
Run the application and navigate to `http://127.0.0.1:8000/docs` to explore the API documentation.

- **GET /users**: Retrieve all users.
- **POST /users**: Create a new user.
- **GET /papers**: Retrieve all papers.
- **POST /papers**: Upload a paper.
- **GET /papers/search**: Search for papers.
- **POST /papers/summarize/{id}**: Summarize a specific paper.
- **POST /papers/literature_review/local**: Perform a local literature review by recommending top locally stored papers relevant to a user's topic.
- **POST /papers/literature_review/external**: Perform an external literature review by fetching references from external sources (e.g., Arxiv) related to a user's topic.
- **POST /papers/literature_review/full**: Perform a comprehensive literature review by combining both local and external paper recommendations.

### Adding Papers
Upload PDFs using the `/papers` endpoint. Extracted content is stored in the database, and embeddings are generated for semantic search.

---

## License
This project is licensed under the **Attribution-NonCommercial-ShareAlike 4.0 International** license. See the [LICENSE](LICENSE) file for details.
