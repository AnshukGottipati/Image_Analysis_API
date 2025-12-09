
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
6. [Environment Variables](#environment-variables)  
7. [API Documentation](#api-documentation)  
   - [Global response format](#global-response-format)  
   - [System endpoints](#system-endpoints)  
   - [Image analysis endpoints](#image-analysis-endpoints)  
8. [Error Handling](#error-handling)  
9. [Swagger Examples](#swagger-examples)  
10. [Development Notes](#development-notes)  
11. [Future Improvements](#future-improvements)

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
  - Direct wrapper around Azure’s `ImageAnalysisClient.analyze_from_url`.
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

   Make sure the endpoint matches the one from the Azure portal for your Vision resource.

### Install dependencies

If you’re using a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

Install from `requirements.txt` (example):

```bash
pip install -r requirements.txt
```

If you don’t have `requirements.txt` yet, it might look like:

```txt
fastapi
uvicorn[standard]
python-dotenv
azure-ai-vision-imageanalysis
```

### Run the API

From the project root:

```bash
uvicorn main:app --reload
```

Or rely on the `if __name__ == "__main__"` block in `main.py`:

```bash
python main.py
```

By default, the API will be available at:

* App: `http://localhost:8000/`
* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

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
  Your Azure AI Vision endpoint, for example:
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

The exact shape inside `result` depends on the endpoint/Azure response, but a **real example** for each is wired into Swagger via `docs_http200_examples.py`.

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

* **Errors**:

  * `500` – unexpected server error
    Example (documented in Swagger):

    ```json
    {
      "detail": "Internal server error.",
      "error_code": "INTERNAL_SERVER_ERROR"
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

* **Errors**:

  * `500` – unexpected server error (same shape as above)

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
```

* Example request:

```json
{
  "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Tyrannosaurus_Rex_Holotype.jpg/2560px-Tyrannosaurus_Rex_Holotype.jpg",
  "features": ["TAGS", "CAPTION"]
}
```

Internally, the enum values are mapped to Azure’s `VisualFeatures`:

```python
features_to_use = [VisualFeatures[f.value] for f in request.features]
```

* **Success response** (`200` – wrapped in `AnalysisResult`):
  Example (from a real Azure call) is defined in `ANALYZE_IMAGE_200`:

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
        { "name": "mammal", "confidence": 0.9999 },
        { "name": "animal", "confidence": 0.9998 },
        { "name": "dinosaur", "confidence": 0.9979 }
        // ...
      ]
    }
  }
}
```

* **Errors**:

  * `400` – invalid features (e.g., unsupported visual feature)
  * `500` – unexpected server error
  * `503` – Azure Image Analysis failure (network, invalid URL, Azure-side error)

All errors share the `ErrorResponse` model:

```python
class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
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

* Aspect ratio validation:

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
  "image_url": "https://example.com/image.jpg",
  "aspect_ratios": [0.9, 1.33, 1.0]
}
```

* **Success response** (`200`, from `CROP_AREA_OF_INTEREST_200` example):

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
        "aspect_ratio": 1.0,
        "bounding_box": { "x": 120, "y": 0, "width": 1689, "height": 1689 }
      }
    ]
  }
}
```

* **Errors**:

  * `400` – invalid aspect ratio (outside `[0.75, 1.8]`)
  * `500` – Azure client not initialized
  * `503` – Smart Crops call to Azure failed

---

#### `POST /categorize_batch`

Analyzes a list of image URLs, finds each image’s **highest-confidence tag**, and groups URLs by that tag.

* **Request model**: `BatchCategorizeRequest`

```python
class BatchCategorizeRequest(BaseModel):
    image_urls: List[HttpUrl]
```

* **Behavior**:

  * For each image:

    * Calls `analyze_from_url(..., visual_features=[VisualFeatures.TAGS])`
    * Picks `max(analysis.tags.list, key=lambda t: t.confidence)`
    * Adds the URL to `category_map[tag_name]["urls"]`
  * If there are no tags or Azure fails for that image, the URL is added to `failed_images`.

* **Response shape** (`200`):

```json
{
  "result": {
    "category_map": {
      "bird": {
        "top_tag": { "name": "bird", "confidence": 0.987 },
        "urls": ["https://example.com/bird1.jpg", "https://example.com/bird2.jpg"]
      },
      "person": {
        "top_tag": { "name": "person", "confidence": 0.954 },
        "urls": ["https://example.com/human1.jpg"]
      }
    },
    "failed_images": {
      "https://example.com/broken.jpg": "Analysis failed: <azure-error>"
    }
  }
}
```

* **Errors**:

  * `500` – Azure client not initialized
  * `503` – (reserved/documented for use if you ever decide to fail the whole batch on Azure issues; currently per-image errors are captured in `failed_images`)

---

## Error Handling

All custom errors surface through `HTTPException` with a consistent body:

```python
class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
```

Common patterns:

* Invalid input → `400`
* Misconfiguration / unexpected bugs → `500`
* Azure service issues → `503`

Examples are defined in `docs_error_examples.py` and wired into the `responses={...}` parameter on each route, so Swagger clearly shows:

* Expected status codes
* Example error payloads
* The shared `ErrorResponse` schema

---

## Swagger Examples

Success examples (HTTP 200) are kept in:

* `docs_http200_examples.py`

For example:

```python
ANALYZE_IMAGE_200 = {
    "description": "Image analyzed successfully",
    "content": {
        "application/json": {
            "example": {
                "result": {
                    "modelVersion": "2023-10-01",
                    "captionResult": { ... },
                    "metadata": { ... },
                    "tagsResult": { ... }
                }
            }
        }
    },
}
```

Error examples are kept in:

* `docs_error_examples.py`

For example:

```python
ANALYZE_IMAGE_400 = {
    "description": "Bad request – invalid features or input.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Invalid visual feature name provided: 'FOO'."
            }
        }
    },
}
```

This keeps your `main.py` clean while still having rich Swagger docs.

---

## Development Notes

* The Azure client is created once at startup if `AZURE_ENDPOINT` and `AZURE_KEY` are set.
  If initialization fails, the client is left as `None` and endpoints will respond with a 500 error.
* Logging is currently via simple `print(...)` statements. You may want to replace these with Python’s `logging` module for production usage.

---

## Future Improvements

Some potential enhancements:

* Add authentication / API keys for clients.
* Add proper rate limiting (per IP or per API key) in front of the app or via middleware.
* Add more detailed domain-specific `error_code` values per error.
* Add unit / integration tests (e.g., using `httpx` and `pytest`).
* Add Dockerfile and containerization instructions.
