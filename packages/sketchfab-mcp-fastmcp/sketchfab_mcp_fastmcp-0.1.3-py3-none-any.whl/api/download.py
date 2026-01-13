import requests
import shutil
import os
import tempfile
from pathlib import Path

from . import auth

DOWNLOAD_URL = "https://api.sketchfab.com/v3/models/{}/download"


def get_download_url(uid):
    """Get download url for a model.

    Keyword arguments:
    uid -- The unique identifier of the model.
    """

    print(f"Getting download url for uid {uid}")
    r = requests.get(
        DOWNLOAD_URL.format(uid),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Token {auth.__API_TOKEN}",
        },
    )

    data = None
    try:
        data = r.json()
    except ValueError:
        pass

    assert r.ok, f"Failed to get download url for model {uid}: {r.status_code} - {data}"

    assert "gltf" in data, f"'gltf' field not found in response: {data}"
    gltf = data.get("gltf")

    assert "url" in gltf, f"'url' field not found in response: {data}"
    url = gltf.get("url")

    assert "size" in gltf, f"'size' field not found in response: {data}"
    size = gltf.get("size")

    return {"url": url, "size": size}


def download_model(model_uid, file_path):
    """Download a model.

    Keyword arguments:
    model_uid -- The unique identifier of the model.
    file_path -- The absolute path to the folder where the model will be stored.
    """
    # Convert to absolute path if not already
    file_path = os.path.abspath(file_path)
    data = get_download_url(model_uid) 

    # Ensure the target directory exists
    directory = os.path.dirname(file_path)
    assert os.path.exists(directory), f"Download directory '{directory}' doesn't exist"

    download_path = os.path.join(directory, f"{model_uid}.zip")

    print(f"Downloading model, size {(data['size'] / (1024 * 1024)):.1f}MB")
    with requests.get(data["url"], stream=True) as r:
        with open(download_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    shutil.unpack_archive(download_path, file_path, "zip")
    os.unlink(download_path)

    print(f"Finished downloading to {file_path}")

    return file_path