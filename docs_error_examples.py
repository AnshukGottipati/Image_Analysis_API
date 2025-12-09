# docs_error_examples.py

# --- Analyze image errors ---

# docs_error_examples.py

ROOT_500 = {
    "description": "Unexpected server error while fetching API status.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Internal server error.",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        }
    },
}

HEALTH_500 = {
    "description": "Unexpected server error while performing health check.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Internal server error.",
                "error_code": "INTERNAL_SERVER_ERROR"
            }
        }
    },
}

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

ANALYZE_IMAGE_500 = {
    "description": "Unexpected server error while analyzing image.",
    "content": {
        "application/json": {
            "example": {
                "detail": "An unexpected server error occurred: <details>."
            }
        }
    },
}

ANALYZE_IMAGE_503 = {
    "description": "Azure Image Analysis service is unavailable.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Azure Image Analysis service call failed: <details>. Check URL and feature validity."
            }
        }
    },
}

# --- Crop area of interest errors ---

CROP_AREA_OF_INTEREST_400 = {
    "description": "Aspect ratio out of range for Azure Smart Crops.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Invalid aspect ratios [0.5, 2.0]. Each aspect ratio must be between 0.75 and 1.8 inclusive."
            }
        }
    },
}

CROP_AREA_OF_INTEREST_500 = {
    "description": "Azure client configuration error.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Azure client not initialized. Check AZURE_ENDPOINT and AZURE_KEY configuration."
            }
        }
    },
}

CROP_AREA_OF_INTEREST_503 = {
    "description": "Azure Smart Cropping service call failed.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Azure Smart Cropping service call failed: <details>."
            }
        }
    },
}

# --- Categorize batch errors ---

CATEGORIZE_BATCH_500 = {
    "description": "Azure client configuration error.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Azure client not initialized. Check AZURE_ENDPOINT and AZURE_KEY configuration."
            }
        }
    },
}

CATEGORIZE_BATCH_503 = {
    "description": "Azure service unavailable while categorizing batch.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Azure Image Analysis service call failed: <details>."
            }
        }
    },
}
