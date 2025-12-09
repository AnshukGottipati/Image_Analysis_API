import os
from enum import Enum
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, Field
import uvicorn

# Azure AI Vision specific imports
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

from docs_http200_examples import *

from docs_error_examples import *

# --- Configuration & Initialization ---
load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_KEY")

if not AZURE_ENDPOINT or not AZURE_KEY:
    print("Warning: AZURE_ENDPOINT or AZURE_KEY not set. Image analysis calls will fail.")

# Initialize Azure Client - conditionally create if keys are available
client = None
if AZURE_ENDPOINT and AZURE_KEY:
    try:
        credential = AzureKeyCredential(AZURE_KEY)

        client = ImageAnalysisClient(
            endpoint=AZURE_ENDPOINT,
            credential=credential,
        )
        print("Azure client initialized successfully.")
    except Exception as e:
        print(f"Error initializing Azure client: {e}")
        client = None

app = FastAPI(
    title="Image Analysis API",
    description="FastAPI service for general image analysis and smart cropping using Azure AI Vision.",
    version="0.1.0",
)

# --- Enums and Models ---


class RootResponse(BaseModel):
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    azure_configured: bool


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


class VisualFeatureName(str, Enum):
    TAGS = "TAGS"
    CAPTION = "CAPTION"
    OBJECTS = "OBJECTS"
    DENSE_CAPTIONS = "DENSE_CAPTIONS"
    PEOPLE = "PEOPLE"
    SMART_CROPS = "SMART_CROPS"
    READ = "READ"
    # Add or remove based on what you actually support


class AnalyzeFeatures(BaseModel):
    """Model for specifying image URL and desired features."""
    image_url: HttpUrl = Field(
        ...,
        example=(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/"
            "Tyrannosaurus_Rex_Holotype.jpg/2560px-Tyrannosaurus_Rex_Holotype.jpg"
        ),
    )
    features: List[VisualFeatureName] = Field(
        default=[VisualFeatureName.TAGS, VisualFeatureName.CAPTION],
        description="Visual features to extract for this image.",
        example=[VisualFeatureName.TAGS, VisualFeatureName.CAPTION],
    )


class CroppingRequest(BaseModel):
    """Model for smart cropping request input."""
    image_url: HttpUrl = Field(
        ...,
        example=(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/"
            "Tyrannosaurus_Rex_Holotype.jpg/2560px-Tyrannosaurus_Rex_Holotype.jpg"
        ),
    )
    aspect_ratios: List[float] = Field(
        default=[0.9, 1.33, 1.0],
        description=(
            "List of desired aspect ratios between 0.75 and 1.8 inclusive. "
            "For example [0.9, 1.33] for portrait and 4:3."
        ),
        example=[0.9, 1.0, 1.33],
    )


class AnalysisResult(BaseModel):
    """Generic wrapper for raw analysis result."""
    result: Dict


class BatchCategorizeRequest(BaseModel):
    """Model for a batch request containing a list of image URLs."""
    image_urls: List[HttpUrl] = Field(
        ...,
        example=[
            "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia.australian.museum%2Fmedia%2Fdd%2Fimages%2Fyellow-billed_spoonbill.e943278.width-800.212677d.jpg&f=1&nofb=1&ipt=f13fcb0aea2ca95a792e5e22e20bb7bf99defee9da609d3048e1f23f9521d209",
            "https://content.eol.org/data/media/be/38/0e/30.6bf2d9f80954fa23e430abb549403f2c.jpg",
            "https://content.eol.org/data/media/be/2e/10/30.324afcc0ad71720c4346a9b46bbaa7e0.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/015_Chimpanzee_at_Kibale_forest_National_Park_Photo_by_Giles_Laurent.jpg/250px-015_Chimpanzee_at_Kibale_forest_National_Park_Photo_by_Giles_Laurent.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/6/68/Akha_cropped_hires.JPG",
        ],
    )


# --- Helper Function for Azure Call ---


def _call_azure_analysis(image_url: str, features: List[VisualFeatures]) -> dict:
    """Helper function to call the synchronous Azure Image Analysis service."""
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Azure client not initialized. Check AZURE_ENDPOINT and AZURE_KEY configuration.",
        )

    try:
        print(f"Analyzing {image_url} with features: {[f.name for f in features]}")

        analysis = client.analyze_from_url(
            image_url=image_url,
            visual_features=features,
        )

        return analysis.as_dict()

    except Exception as e:
        print(f"Azure Image Analysis Error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Azure Image Analysis service call failed: {e}. Check URL and feature validity.",
        )

# --- Core API Endpoints ---

@app.get(
    "/",
    response_model=RootResponse,
    tags=["System"],
    summary="API status",
    description="Basic status message confirming that the Image Intelligence API is running.",
    responses={
        200: ROOT_200,
        500: {"model": ErrorResponse, **ROOT_500},
    },
)
async def root():
    return RootResponse(
        status="ok",
        message="Image Intelligence API is running. Check /docs for endpoints.",
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description=(
        "Returns the overall health of this FastAPI service and whether Azure Vision "
        "is correctly configured and initialized."
    ),
    responses={
        200: HEALTH_200,
        500: {"model": ErrorResponse, **HEALTH_500},
    },
)
async def health_check():
    return HealthResponse(
        status="healthy",
        azure_configured=bool(AZURE_ENDPOINT and AZURE_KEY and client),
    )


@app.post(
    "/analyze_image",
    response_model=AnalysisResult,
    responses={
        200: ANALYZE_IMAGE_200,
        400: {"model": ErrorResponse, **ANALYZE_IMAGE_400},
        500: {"model": ErrorResponse, **ANALYZE_IMAGE_500},
        503: {"model": ErrorResponse, **ANALYZE_IMAGE_503},
    },
)
async def analyze_image(request: AnalyzeFeatures):
    """
    Analyzes an image with specified visual features (for example, TAGS, CAPTION, OBJECTS).
    """
    try:
        features_to_use = [VisualFeatures[f.value] for f in request.features]

        if not features_to_use:
            raise HTTPException(
                status_code=400,
                detail="No valid visual features specified. Must be one or more.",
            )

        analysis_result = _call_azure_analysis(
            image_url=str(request.image_url),
            features=features_to_use,
        )

        return {"result": analysis_result}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected server error occurred: {e}",
        )


@app.post(
    "/crop_area_of_interest",
    response_model=AnalysisResult,
    responses={
        200: CROP_AREA_OF_INTEREST_200,
        400: {"model": ErrorResponse, **CROP_AREA_OF_INTEREST_400},
        500: {"model": ErrorResponse, **CROP_AREA_OF_INTEREST_500},
        503: {"model": ErrorResponse, **CROP_AREA_OF_INTEREST_503},
    },
)
async def crop_area_of_interest(request: CroppingRequest):
    """
    Identifies the best crop regions for the specified aspect ratios (Smart Crop).
    Aspect ratios must be between 0.75 and 1.8 inclusive.
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Azure client not initialized. Check AZURE_ENDPOINT and AZURE_KEY configuration.",
        )

    try:
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

        analysis = client.analyze_from_url(
            image_url=str(request.image_url),
            visual_features=[VisualFeatures.SMART_CROPS],
            smart_crops_aspect_ratios=aspect_ratios_float,
        )

        crop_regions_data = []
        if analysis.smart_crops and analysis.smart_crops.list:
            for r in analysis.smart_crops.list:
                bbox = r.bounding_box
                crop_regions_data.append(
                    {
                        "aspect_ratio": r.aspect_ratio,
                        "bounding_box": {
                            "x": bbox.x,
                            "y": bbox.y,
                            "width": bbox.width,
                            "height": bbox.height,
                        },
                    }
                )

        return {"result": {"crop_regions": crop_regions_data}}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Azure Smart Cropping Error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Azure Smart Cropping service call failed: {e}",
        )


@app.post(
    "/categorize_batch",
    response_model=AnalysisResult,
    responses={
        200: CATEGORIZE_BATCH_200,
        500: {"model": ErrorResponse, **CATEGORIZE_BATCH_500},
        503: {"model": ErrorResponse, **CATEGORIZE_BATCH_503},
    },
)
async def categorize_batch(request: BatchCategorizeRequest):
    """
    Analyzes a list of image URLs, finds each image's highest-confidence tag,
    and groups URLs by that tag.
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Azure client not initialized. Check AZURE_ENDPOINT and AZURE_KEY configuration.",
        )

    category_map: Dict[str, Dict] = {}
    failed_images: Dict[str, str] = {}

    for image_url in request.image_urls:
        url_str = str(image_url)
        print(f"Analyzing tags for categorization: {url_str}")

        try:
            analysis = client.analyze_from_url(
                image_url=url_str,
                visual_features=[VisualFeatures.TAGS],
            )

            if not analysis.tags or not analysis.tags.list:
                failed_images[url_str] = "No tags returned by Azure."
                continue

            top_tag = max(analysis.tags.list, key=lambda t: t.confidence)
            tag_name = top_tag.name
            tag_conf = top_tag.confidence

            if tag_name not in category_map:
                category_map[tag_name] = {
                    "top_tag": {
                        "name": tag_name,
                        "confidence": tag_conf,
                    },
                    "urls": [url_str],
                }
            else:
                category_map[tag_name]["urls"].append(url_str)
                if tag_conf > category_map[tag_name]["top_tag"]["confidence"]:
                    category_map[tag_name]["top_tag"]["confidence"] = tag_conf

        except Exception as e:
            print(f"Error processing {url_str}: {e}")
            failed_images[url_str] = f"Analysis failed: {e}"

    return {
        "result": {
            "category_map": category_map,
            "failed_images": failed_images,
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
