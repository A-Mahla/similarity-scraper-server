# API Reference

This section details the endpoints available in the Similarity Scraper Engine API, including request parameters and example responses.

## Routes Overview

The API consists of three primary routes:

1. **Scraper**: Manages webpage scraping.
2. **Embedding**: Handles embedding uniqueness.
3. **Sample**: Manages CRUD database operations for samples.

<br>

---

### Scraper Routes

#### POST `/api/scraper`
Scrapes a webpage to extract the one essential text or images.

- **Parameters**:
  - `url` (string): The URL of the webpage to scrape.
  - `image_search` (boolean): Set to `true` to scrape images, defaults to `false`.
  - `language` (string): The language of the page content, defaults to `en`.

- **Example Request**:

```bash
curl -X POST "http://localhost/api/scraper" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.hcompany.ai/",
    "image_search": false
  }'
```

- **Example Response**:

```json
{
  "metadata": {
    "url": "https://www.example.com/",
    "tag": "<p>",
    "language": "en",
    "type": "text",
    "content": "Extracted main content of the page."
  },
  "status": "success",
  "message": "Text content was successfully extracted from the page.",
  "database_log": "Sample created successfully"
}
```

> Languages supported: `ar`, `bg`, `ca`, `cs`, `da`, `de`, `el`, `en`, `es`, `et`, `fa`, `fi`, `fr`, `gu`, `he`, `hi`, `hr`, `hu`, `id`, `it`, `ja`, `ko`, `lt`, `lv`, `mk`, `mr`, `nl`, `pl`, `pt`, `ro`, `ru`, `sk`, `sl`, `sq`, `sv`, `th`, `tr`, `uk`, `ur`, `vi`, `zh-cn`, `zh-tw`.


<br>

---


### Embedding Routes

#### GET `/api/embedding/unique`
Retrieve embeddings, based on a specific type, to ensure each text or image is uniquely represented within the dataset. Remove any text or image that is too similar to another, retaining only one instance.


- **Parameters**:
  - `type` (string): Type of the sample, possible values include `text`, `image`.

- **Example Request**:

```bash
curl -X GET "http://localhost/api/embedding/unique?type=text" -H "accept: application/json"
```

- **Example Response**:

```json
{
  "embedding_samples": [
    {
      "samples_deleted": [
      {
        "sample": {
          "_id": "668be6cc6ad706dd089fc448",
          "metadata": {
            "url": "https://www.example1.com/",
            "image_url": null,
            "tag": "<p>",
            "language": "en",
            "type": "text",
            "content": "This is a sample text content for the labeled dataset."
          }
        },
        "vectors": [
          -0.009808141738176346,
          0.2825802266597748,
          -0.20362475514411926,
          -0.02926643192768097,
          0.1852894425392151,
          0.12326715141534805,
          ...
        }
      }
    }
  ],
  "status": "success",
  "message": "Vectors were successfully extracted."
}
```


<br>

---


### Sample Routes

#### POST `/api/sample`
Adds a new data sample to the database.

- **Parameters**:
  - `metadata` (object): The metadata describing the sample.

- **Example Request**:

```bash
curl -X POST "http://localhost/api/sample"  \
    -H "Content-Type: application/json"\
    -d '{
      "metadata": {
        "url": "https://www.example.com",        
        "tag": "<p>",
        "language": "en",
        "type": "text",
        "content": "This is a sample text content for the labeled dataset."
      }
    }'
```

- **Example Response**:

```json
{
  "id": "668be31b3654bd644338140a",
  "metadata": {
    "url": "https://www.example.com/",
    "image_url": null,
    "tag": "<p>",
    "language": "en",
    "type": "text",
    "content": "This is a sample text content for the labeled dataset."
  },
  "message": "Sample created successfully"
}
```

#### GET `/api/sample`
Retrieves samples from database based on the type specified.

- **Parameters**:
  - `type` (string): : Type of the samples to delete, possible values include `text`, `image` and `all`.

- **Example Request**:

```bash
curl -X GET "http://localhost/api/sample?type=text" -H "accept: application/json"
```

- **Example Response**:

```json
{
  "samples": [
    {
      "id": "67890",
      "metadata": {
        "url": "https://www.exampletextpage.com",
        "tag": "<p>",
        "language": "en",
        "type": "text",
        "content": "This is a sample text content for the labeled dataset."
      }
    }
  ],
  "message": "Samples retrieved successfully"
}
```

#### DELETE `/api/sample`
Deletes samples from database based on the type specified.

- **Parameters**:
  - `type` (string): Type of the samples to delete, possible values include `text`, `image` and `all`.

- **Example Request**:

```bash
curl -X DELETE "http://localhost/api/sample?type=text" -H "accept: application/json"
```

- **Example Response**:

```json
{
  "count": 1,
  "message": "1 samples of type 'text' deleted successfully"
}
```

For additional details and advanced usage, refer to the Usage Examples section.