Got it, I’ll keep your original structure and tone, just:

* Add Docker setup
* Remove *Development Notes* and *Future Improvements*
* Add `curl` examples
* Lightly tighten wording (but not brutally)

Here’s the updated README:

````md
# Image Analysis API

FastAPI service that wraps **Azure AI Vision – Image Analysis** to provide:

- General image analysis (tags, captions, etc.)
- Smart cropping with aspect ratios (areas of interest)
- Batch categorization of images by their highest-confidence tag
- Clean, fully-documented OpenAPI/Swagger UI with real example responses
- Consistent, typed error responses

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Tech Stack](#tech-stack)  
4. [Project Structure](#project-structure)  
5. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Clone the repo](#clone-the-repo)  
   - [Create and configure your `.env`](#create-and-configure-your-env)  
   - [Install dependencies](#install-dependencies)  
   - [Run the API](#run-the-api)  
6. [Running with Docker](#running-with-docker)  
7. [Environment Variables](#environment-variables)  
8. [API Documentation](#api-documentation)  
   - [Global response format](#global-response-format)  
   - [System endpoints](#system-endpoints)  
   - [Image analysis endpoints](#image-analysis-endpoints)  
   - [Curl examples](#curl-examples)  
9. [Error Handling](#error-handling)  
10. [Swagger Examples](#swagger-examples)

---

## Overview

This project exposes a small but well-structured REST API on top of **Azure AI Vision’s Image Analysis** capabilities.

Goals:

- Make it easy to experiment with Azure Image Analysis from any client (web, mobile, backend).
- Provide **useful Swagger UI** by:
  - Defining enums for valid visual features.
  - Using Pydantic models for request/response shapes.
  - Supplying **real example payloads** for 200 responses and common errors.
- Keep secrets out of source control via `.env` and `.env.example`.

---

## Features

- ✅ **Health & status endpoints**
- ✅ **Analyze a single image**  
  - Select visual features such as `TAGS`, `CAPTION`, `OBJECTS`, etc.
- ✅ **Smart cropping (area of interest)**
  - Accepts a list of aspect ratios.
  - Validates they’re in Azure’s supported range `[0.75, 1.8]`.
  - Returns a clean list of bounding boxes.
- ✅ **Batch categorization**
  - Takes multiple image URLs.
  - Gets tags from Azure.
  - Groups images by their **highest-confidence tag**.
- ✅ **Consistent error model**
  - `ErrorResponse` with `detail` and optional `error_code`.
  - Typed errors documented in Swagger.
- ✅ **Swagger examples stored in separate files**
  - `docs_http200_examples.py` – success examples.
  - `docs_error_examples.py` – error examples.

---

## Tech Stack

- **Python** 3.10+ (recommended)
- **FastAPI** – web framework and OpenAPI generation
- **Uvicorn** – ASGI server
- **python-dotenv** – `.env` loading
- **Azure AI Vision – Image Analysis** SDK:
  - `azure-ai-vision-imageanalysis`
  - `azure-core` (dependency)

---

## Project Structure

Suggested repo layout:

```text
.
├── main.py                     # FastAPI app + endpoints
├── docs_http200_examples.py    # Example 200 OK responses for Swagger
├── docs_error_examples.py      # Example error responses for Swagger
├── .env.example                # Template for environment variables (no secrets)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── deploy_docker.sh            # Optional helper script for Docker
└── README.md                   # This file
````

---

## Getting Started

### Prerequisites

* Python 3.10+
* A working Azure AI Vision resource:

  * Azure **Endpoint**
  * Azure **Key**

### Clone the repo

```bash
git clone <your-repo-url>.git
cd <your-repo-folder>
```

### Create and configure your `.env`

The real `.env` **should not be committed**. It is ignored via `.gitignore`.

1. Copy the template:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in your real values:

   ```dotenv
   AZURE_ENDPOINT="https://<your-azure-endpoint>.cognitiveservices.azure.com/"
   AZURE_KEY="YOUR_REAL_AZURE_KEY_HERE"
   ```

### Install dependencies

If you’re using a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

Install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Typical `requirements.txt`:

```txt
fastapi
uvicorn[standard]
python-dotenv
azure-ai-vision-imageanalysis
```

### Run the API

From the project root:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

By default, the API will be available at:

* App: `http://localhost:8000/`
* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## Running with Docker

From the project root (where `Dockerfile` and `.env` live):

### Build

```bash
sudo docker build -t image-analysis-api:latest .
```

### Run

```bash
sudo docker run -d \
  --name image-analysis-api \
  -p 8000:8000 \
  --env-file .env \
  image-analysis-api:latest
```

Now reachable at:

* `http://localhost:8000` (local)
* `http://YOUR_DROPLET_IP:8000` (remote)

If you use `deploy_docker.sh`:

```bash
chmod +x deploy_docker.sh
./deploy_docker.sh
```

This script builds the image and runs the container with `.env` automatically.

---

## Environment Variables

Loaded via `python-dotenv`:

```python
from dotenv import load_dotenv

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY")
```

### Required

* `AZURE_ENDPOINT`
  Example:
  `https://<your-resource-name>.cognitiveservices.azure.com/`

* `AZURE_KEY`
  The API key for that Vision resource.

If these are missing, the app prints a warning and `client` remains `None`. Any endpoint that needs Azure will return a 500 with:

```json
{
  "detail": "Azure client not initialized. Check AZURE_ENDPOINT and AZURE_KEY configuration.",
  "error_code": null
}
```

---

## API Documentation

### Global response format

Most “business” endpoints use a common wrapper:

```python
class AnalysisResult(BaseModel):
    result: Dict
```

The exact shape inside `result` depends on the endpoint/Azure response, but real examples for each are wired into Swagger via `docs_http200_examples.py`.

---

### System endpoints

#### `GET /`

Simple API status endpoint.

* **Response model**: `RootResponse`

```python
class RootResponse(BaseModel):
    status: str
    message: str
```

* **Typical response:**

```json
{
  "status": "ok",
  "message": "Image Intelligence API is running. Check /docs for endpoints."
}
```

#### `GET /health`

Returns the health of the service and whether Azure is configured.

* **Response model**: `HealthResponse`

```python
class HealthResponse(BaseModel):
    status: str
    azure_configured: bool
```

* **Typical response:**

```json
{
  "status": "healthy",
  "azure_configured": true
}
```

`azure_configured` is `true` only if:

* `AZURE_ENDPOINT` is set
* `AZURE_KEY` is set
* Azure client initialized successfully

---

### Image analysis endpoints

#### `POST /analyze_image`

Performs general image analysis with selected visual features.

* **Request model**: `AnalyzeFeatures`

```python
class VisualFeatureName(str, Enum):
    TAGS = "TAGS"
    CAPTION = "CAPTION"
    OBJECTS = "OBJECTS"
    DENSE_CAPTIONS = "DENSE_CAPTIONS"
    PEOPLE = "PEOPLE"
    SMART_CROPS = "SMART_CROPS"
    READ = "READ"

class AnalyzeFeatures(BaseModel):
    image_url: HttpUrl
    features: List[VisualFeatureName]
}
```

* **Example request:**

```json
{
  "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Tyrannosaurus_Rex_Holotype.jpg/2560px-Tyrannosaurus_Rex_Holotype.jpg",
  "features": ["TAGS", "CAPTION"]
}
```

* **Example response (truncated):**

```json
{
  "result": {
    "modelVersion": "2023-10-01",
    "captionResult": {
      "text": "a dinosaur skeleton in a museum",
      "confidence": 0.7875
    },
    "metadata": {
      "width": 2560,
      "height": 1696
    },
    "tagsResult": {
      "values": [
        { "name": "mammal", "confidence": 0.9998923540115356 },
        { "name": "animal", "confidence": 0.9998763799667358 },
        { "name": "reptile", "confidence": 0.9995557069778442 }
      ]
    }
  }
}
```

---

#### `POST /crop_area_of_interest`

Uses Azure Smart Crops to recommend crop regions for given aspect ratios.

* **Request model**: `CroppingRequest`

```python
class CroppingRequest(BaseModel):
    image_url: HttpUrl
    aspect_ratios: List[float]  # must be between 0.75 and 1.8
```

Aspect ratios are validated:

```python
aspect_ratios_float = [float(ar) for ar in request.aspect_ratios]
invalid = [ar for ar in aspect_ratios_float if ar < 0.75 or ar > 1.8]
if invalid:
    raise HTTPException(
        status_code=400,
        detail=(
            f"Invalid aspect ratios {invalid}. "
            "Each aspect ratio must be between 0.75 and 1.8 inclusive."
        ),
    )
```

* **Example request:**

```json
{
  "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Tyrannosaurus_Rex_Holotype.jpg/2560px-Tyrannosaurus_Rex_Holotype.jpg",
  "aspect_ratios": [0.9, 1.33, 1.0]
}
```

* **Example response:**

```json
{
  "result": {
    "crop_regions": [
      {
        "aspect_ratio": 0.9,
        "bounding_box": { "x": 40, "y": 0, "width": 1360, "height": 1512 }
      },
      {
        "aspect_ratio": 1.33,
        "bounding_box": { "x": 0, "y": 0, "width": 2249, "height": 1689 }
      },
      {
        "aspect_ratio": 1,
        "bounding_box": { "x": 120, "y": 0, "width": 1689, "height": 1689 }
      }
    ]
  }
}
```

---

#### `POST /categorize_batch`

Analyzes a list of image URLs, finds each image’s **highest-confidence tag**, and groups URLs by that tag.

* **Request model**: `BatchCategorizeRequest`

```python
class BatchCategorizeRequest(BaseModel):
    image_urls: List[HttpUrl]
```

* **Example request:**

```json
{
  "image_urls": [
    "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia.australian.museum%2Fmedia%2Fdd%2Fimages%2Fyellow-billed_spoonbill.e943278.width-800.212677d.jpg&f=1&nofb=1&ipt=f13fcb0aea2ca95a792e5e22e20bb7bf99defee9da609d3048e1f23f9521d209",
    "https://content.eol.org/data/media/be/38/0e/30.6bf2d9f80954fa23e430abb549403f2c.jpg",
    "https://content.eol.org/data/media/be/2e/10/30.324afcc0ad71720c4346a9b46bbaa7e0.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/015_Chimpanzee_at_Kibale_forest_National_Park_Photo_by_Giles_Laurent.jpg/250px-015_Chimpanzee_at_Kibale_forest_National_Park_Photo_by_Giles_Laurent.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/68/Akha_cropped_hires.JPG"
  ]
}
```

* **Example response:**

```json
{
  "result": {
    "category_map": {
      "animal": {
        "top_tag": {
          "name": "animal",
          "confidence": 0.9999960064888
        },
        "urls": [
          "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia.australian.museum%2Fmedia%2Fdd%2Fimages%2Fyellow-billed_spoonbill.e943278.width-800.212677d.jpg&f=1&nofb=1&ipt=f13fcb0aea2ca95a792e5e22e20bb7bf99defee9da609d3048e1f23f9521d209",
          "https://content.eol.org/data/media/be/38/0e/30.6bf2d9f80954fa23e430abb549403f2c.jpg",
          "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/015_Chimpanzee_at_Kibale_forest_National_Park_Photo_by_Giles_Laurent.jpg/250px-015_Chimpanzee_at_Kibale_forest_National_Park_Photo_by_Giles_Laurent.jpg"
        ]
      },
      "mammal": {
        "top_tag": {
          "name": "mammal",
          "confidence": 0.9992899894714355
        },
        "urls": [
          "https://content.eol.org/data/media/be/2e/10/30.324afcc0ad71720c4346a9b46bbaa7e0.jpg"
        ]
      },
      "clothing": {
        "top_tag": {
          "name": "clothing",
          "confidence": 0.9988645315170288
        },
        "urls": [
          "https://upload.wikimedia.org/wikipedia/commons/6/68/Akha_cropped_hires.JPG"
        ]
      }
    },
    "failed_images": {}
  }
}
```

---

### Curl examples

Replace `localhost` with `YOUR_DROPLET_IP` if needed.

**Root**

```bash
curl http://localhost:8000/
```

**Health**

```bash
curl http://localhost:8000/health
```

**Analyze Image**

```bash
curl -X POST "http://localhost:8000/analyze_image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Tyrannosaurus_Rex_Holotype.jpg/2560px-Tyrannosaurus_Rex_Holotype.jpg",
    "features": ["TAGS", "CAPTION"]
  }'
```

**Smart Crop**

```bash
curl -X POST "http://localhost:8000/crop_area_of_interest" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Tyrannosaurus_Rex_Holotype.jpg/2560px-Tyrannosaurus_Rex_Holotype.jpg",
    "aspect_ratios": [0.9, 1.33, 1.0]
  }'
```

**Batch Categorize**

```bash
curl -X POST "http://localhost:8000/categorize_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "image_urls": [
      "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia.australian.museum%2Fmedia%2Fdd%2Fimages%2Fyellow-billed_spoonbill.e943278.width-800.212677d.jpg&f=1&nofb=1&ipt=f13fcb0aea2ca95a792e5e22e20bb7bf99defee9da609d3048e1f23f9521d209",
      "https://content.eol.org/data/media/be/38/0e/30.6bf2d9f80954fa23e430abb549403f2c.jpg",
      "https://content.eol.org/data/media/be/2e/10/30.324afcc0ad71720c4346a9b46bbaa7e0.jpg",
      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/015_Chimpanzee_at_Kibale_forest_National_Park_Photo_by_Giles_Laurent.jpg/250px-015_Chimpanzee_at_Kibale_forest_National_Park_Photo_by_Giles_Laurent.jpg",
      "https://upload.wikimedia.org/wikipedia/commons/6/68/Akha_cropped_hires.JPG"
    ]
  }'
```

---

## Error Handling

All custom errors use:

```python
class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None

```

Common patterns:

* `400` – invalid input (bad features, bad aspect ratios, etc.)
* `500` – misconfiguration or unexpected server error
* `503` – Azure service issues (network, invalid URL, Azure-side errors)

Examples are defined in `docs_error_examples.py` and referenced in each route’s `responses={...}` parameter so Swagger shows expected error payloads.

---

## Swagger Examples

Success examples (HTTP 200) are kept in:

* `docs_http200_examples.py`

Error examples are kept in:

* `docs_error_examples.py`

These are plugged into FastAPI route definitions using the `responses` argument, so the docs show realistic sample payloads for both success and failure cases.

Accessing the Swagger UI:
```
http://localhost:8000/docs
```
