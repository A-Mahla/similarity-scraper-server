
# Similarity Scraper Engine

The Similarity Scraper Engine is a tool designed to extract and manage text and image data from webpages efficiently. It leverages web scraping techniques, data embeddings, and sample database management through a REST API built with FastAPI and served over Nginx. It is production ready for deployment and managed by docker compose.

## Features

- **Web Scraping**: Scrape most important text and images based on attributes such as depth, child element count, text density and tag matching.
- **Data Embeddings**: Generates embeddings using the [clip-ViT-B-32-multilingual-v1](https://huggingface.co/sentence-transformers/clip-ViT-B-32-multilingual-v1) model to measure cosine similarity and manage dataset redundancy.
- **Sample Management**: CRUD operations on a MongoDB database to handle data samples efficiently.

### Technologies

- **[FastAPI](https://fastapi.tiangolo.com/)**: For creating the REST API.
- **[Nginx](https://nginx.org/)**: Used as a reverse proxy to FastAPI and serves frontend documentation.
- **[MKDocs](https://www.mkdocs.org/)**: For creating project frontend documentation.
- **[MongoDB](https://www.mongodb.com/)**: Database
- **[Docker Compose](https://docs.docker.com/compose/)**: containers management

## Getting Started

### Environment Variables

Ensure the following environment variables are set in your `.env` file at the project root before starting the Docker containers:

```
# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME = "root_username"
MONGO_INITDB_ROOT_PASSWORD = "password"
MONGO_INITDB_DATABASE = "database_name"

# api server env
MONGO_URL = "mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@mongodb:27017" # keep it as is.

# Multi Modal Model inference
CLIP_INFERENCE_API = "http://multi2vec-clip:8080" # keep it as is.
```

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/A-Mahla/similarity-scraper-server.git
   ```
2. Navigate to the project directory:
   ```bash
   cd similarity-scraper-engine
   ```

3. Build and run the Docker containers:
   ```bash
   docker compose up --build
   ```

This will start the services defined in your `docker-compose.yml` file, including FastAPI, Nginx, and any necessary databases.

### API Access

- **Documentation**: Once Docker is up, access the [API documentation](https://github.com/A-Mahla/similarity-scraper-server/blob/main/app/frontend/mkdocs/docs/reference.md) at: [http://localhost](http://localhost)
- **API Base URL**: [http://localhost/api](http://localhost/api)

### Example Usage

#### Scrape a Webpage

To scrape text from a webpage:

```bash
curl -X POST "http://localhost/api/scraper" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com/",
    "image_search": false,
  }'
```

## Contributing

Contributions are welcome! Please open an issue to discuss your ideas or submit a Pull Request.
