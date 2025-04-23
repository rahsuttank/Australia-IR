# 🌐 Web Graph Search Engine

This project implements a web graph-based search engine using **Apache Solr** and **Flask**, featuring PageRank-based ranking and extensibility for HITS and clustering algorithms.

---

## 📑 Table of Contents

- [Overview](#overview)
- [File Formats](#file-formats)
- [Setup Instructions](#setup-instructions)
  - [Docker Compose Setup](#docker-compose-setup)
  - [Manual (Non-Docker) Setup](#manual-non-docker-setup)
- [Data Preparation](#data-preparation)
- [API Usage](#api-usage)
- [Current Status](#current-status)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🔍 Overview

This search engine is designed to work over a web graph dataset.

- **Solr** indexes and enables fielded document search.
- **Flask API** serves search and ranking endpoints.
- **Ranking**:
  - ✅ PageRank implemented and functional
  - 🚧 HITS and clustering in progress
- **Data Input**: JSON web graph (e.g., `australia_webgraph.json`) converted to Solr-ingestable format.

---

## 📁 File Formats

### 1. `australia_webgraph.json`
- **Format**: JSON (adjacency list)
- **Purpose**: Maps each URL to its outgoing links
- **Use**: Input for graph algorithms like PageRank/HITS

### 2. `solr_docs.json`
- **Format**: JSON array of objects
- **Purpose**: Solr-ingestable documents with fields:
  - `url`, `outgoing_links`, `title`, `content`
- **Use**: Core input for Solr indexing

**Tip**: Use `australia_webgraph.json` for computation, and `solr_docs.json` for indexing.

---

## ⚙️ Setup Instructions

### 🐳 Docker Compose Setup

1. **Project Structure**:
    ```plaintext
    .
    ├── docker-compose.yml
    ├── schema.json
    ├── convert_to_solr.py
    ├── flask_app.py
    ├── australia_webgraph.json
    ├── query_expansion/
    ├── clustering/
    └── HITS/
    ```

2. **Start Services**:
    ```bash
    docker-compose up -d --build
    ```

    - Solr starts with `countries` core and loads `schema.json`.
    - `convert_to_solr.py` converts and loads data into Solr.
    - Flask API connects to Solr and starts serving requests.

3. **Access Services**:
    - Solr Admin UI: [http://localhost:8983/solr/](http://localhost:8983/solr/)
    - Flask API: [http://localhost:5000/api/v1/indexer](http://localhost:5000/api/v1/indexer)

---

### ⚒️ Manual (Non-Docker) Setup

1. **Install Solr**:
    ```bash
    # Download Solr 8.11.2 and extract
    bin/solr start
    bin/solr create -c countries
    ```

2. **Add Solr Schema**:
    ```bash
    curl -X POST -H 'Content-type:application/json'     --data-binary @schema.json     http://localhost:8983/solr/countries/schema
    ```

3. **Convert and Ingest Data**:
    ```bash
    python convert_to_solr.py australia_webgraph.json solr_docs.json

    curl -X POST -H "Content-Type: application/json"     'http://localhost:8983/solr/countries/update?commit=true'     --data-binary @solr_docs.json
    ```

4. **Install Python Dependencies**:
    ```bash
    pip install flask flask-cors pysolr pyspellchecker numpy
    ```

5. **Run Flask API**:
    ```bash
    python flask_app.py
    ```

---

## 🛠️ Data Preparation

Convert raw graph data to Solr format:
```bash
python convert_to_solr.py australia_webgraph.json solr_docs.json
```

Solr fields required:
- `url`: string
- `outgoing_links`: array of strings
- `title`: text
- `content`: text

---

## 🚀 API Usage

**Basic Search:**
```http
GET /api/v1/indexer?query=url:australia&type=page_rank
```

**Supported `type` values:**
- `page_rank` ✅
- `hits` 🚧
- `clustering` 🚧
- `association_qe`, `metric_qe`, `scalar_qe` (Query Expansion)

**Example (Planned) HITS Query:**
```http
GET /api/v1/indexer?query=url:australia&type=hits
```

---

## 📌 Current Status

| Feature          | Status     | Notes                                       |
|------------------|------------|---------------------------------------------|
| PageRank         | ✅ Working | Returns results ranked by PageRank         |
| HITS             | ⚠️ In progress | Code exists, integration pending         |
| Clustering       | ⚠️ In progress | API output not finalized                 |
| Query Expansion  | ⚠️ Partial  | Basic features implemented                 |

---

## 🧰 Troubleshooting

- **No results returned?**  
  Try specific field queries, e.g., `url:*australia*`

- **Connection errors?**  
  Flask must connect to Solr using `solr:8983`, not `localhost`, when in Docker.

- **Module errors?**  
  Ensure all Python dependencies are installed.

- **Unhashable/list errors?**  
  Check that all `url` fields are strings in your JSON and indexing logic.

---

## 🤝 Contributing

Contributions to improve HITS or clustering features are welcome! Feel free to open issues or pull requests.

---

## 🪪 License

MIT License
