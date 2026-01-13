import os
from typing import Any
from mcp.server.fastmcp import FastMCP
from api import set_api_token, search_results
from api import download_model as download_model_api

API_TOKEN = os.getenv("SKETCHFAB_API_TOKEN")

if not API_TOKEN:
    raise ValueError("SKETCHFAB_API_TOKEN is not set")

mcp = FastMCP("sketchfab")
set_api_token(API_TOKEN)

@mcp.tool()
async def search_models(query: str, animated: bool = False, rigged: bool = False, count: int = 5) -> str:
    """Search for downloadable models on Sketchfab

    Args:
        query: The search term to use for the query (keep it to a single word or two words at most)
        animated: Whether to search for animated models only
        rigged: Whether to search for rigged models only
        count: The number of results to return
    """
    params = {
        "type": "models",
        "q": query,
        "downloadable": True,
        "animated": animated,
        "rigged": rigged,
        "count": count
    }
    results = search_results(params)

    results = [
        {
            "uid": model["uid"],
            "name": model["name"],
            "description": model["description"],
            "tags": [tag['name'] for tag in model["tags"]],
            "likes": model["likeCount"],
            "views": model["viewCount"],
            "license": model["license"]["label"],
            "faceCount": model["faceCount"],
            "vertexCount": model["vertexCount"],
            "animationCount": model["animationCount"],
            "isAgeRestricted": model["isAgeRestricted"]
        }
        for model in results
    ]

    return results

@mcp.tool()
async def download_model(uid: str, path: str) -> str:
    """Downloads a model from Sketchfab to the specified path

    Args:
        uid: The unique identifier of the model to download
        path: The absolute path where the model will be extracted to (should be an empty directory)
    """
    download_model_api(uid, path)

if __name__ == "__main__":
    mcp.run(transport='stdio')
