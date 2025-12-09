
ROOT_200 = {
    "description": "API status",
    "content": {
        "application/json": {
            "example": {
                "status": "ok",
                "message": "Image Intelligence API is running. Check /docs for endpoints."
            }
        }
    },
}

HEALTH_200 = {
    "description": "Health check status",
    "content": {
        "application/json": {
            "example": {
                "status": "healthy",
                "azure_configured": True
            }
        }
    },
}


ANALYZE_IMAGE_200 = {
    "description": "Image analyzed successfully",
    "content": {
        "application/json": {
            "example": {
                "result": {
                    "modelVersion": "2023-10-01",
                    "captionResult": {
                        "text": "a dinosaur skeleton in a museum",
                        "confidence": 0.7875179648399353
                    },
                    "metadata": {
                        "width": 2560,
                        "height": 1696
                    },
                    "tagsResult": {
                        "values": [
                            {
                                "name": "mammal",
                                "confidence": 0.9998923540115356
                            },
                            {
                                "name": "animal",
                                "confidence": 0.9998763799667358
                            },
                            {
                                "name": "reptile",
                                "confidence": 0.9995557069778442
                            },
                            {
                                "name": "dinosaur",
                                "confidence": 0.9979144334793091
                            },
                            {
                                "name": "fossil",
                                "confidence": 0.9466491937637329
                            },
                            {
                                "name": "skeleton",
                                "confidence": 0.9339876174926758
                            },
                            {
                                "name": "skull",
                                "confidence": 0.91836017370224
                            },
                            {
                                "name": "tyrannosaurus",
                                "confidence": 0.9126546382904053
                            },
                            {
                                "name": "outdoor",
                                "confidence": 0.8944091796875
                            },
                            {
                                "name": "bone",
                                "confidence": 0.8858379125595093
                            },
                            {
                                "name": "museum",
                                "confidence": 0.8802951574325562
                            },
                            {
                                "name": "standing",
                                "confidence": 0.7645937204360962
                            }
                        ]
                    }
                }
            }
        }
    },
}


# docs_examples.py

CROP_AREA_OF_INTEREST_200 = {
    "description": "Smart crop regions computed successfully",
    "content": {
        "application/json": {
            "example": {
                "result": {
                    "crop_regions": [
                        {
                            "aspect_ratio": 0.9,
                            "bounding_box": {
                                "x": 40,
                                "y": 0,
                                "width": 1360,
                                "height": 1512
                            }
                        },
                        {
                            "aspect_ratio": 1.33,
                            "bounding_box": {
                                "x": 0,
                                "y": 0,
                                "width": 2249,
                                "height": 1689
                            }
                        },
                        {
                            "aspect_ratio": 1.0,
                            "bounding_box": {
                                "x": 120,
                                "y": 0,
                                "width": 1689,
                                "height": 1689
                            }
                        }
                    ]
                }
            }
        }
    },
}


CATEGORIZE_BATCH_200 = {
    "description": "Batch categorized by top tags",
    "content": {
        "application/json": {
            "example": {
                "result": {
                    "category_map": {
                        "bird": {
                            "top_tag": {
                                "name": "bird",
                                "confidence": 0.987
                            },
                            "urls": [
                                "https://example.com/bird1.jpg",
                                "https://example.com/bird2.jpg"
                            ]
                        },
                        "person": {
                            "top_tag": {
                                "name": "person",
                                "confidence": 0.954
                            },
                            "urls": [
                                "https://example.com/human1.jpg"
                            ]
                        }
                    },
                    "failed_images": {
                        "https://example.com/broken.jpg": "No tags returned by Azure."
                    }
                }
            }
        }
    },
}
