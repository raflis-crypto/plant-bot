import os
import httpx

PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"
SCORE_THRESHOLD = 0.35


async def identify(image_bytes: bytes, filename: str = "photo.jpg") -> dict:
    api_key = os.environ["PLANTNET_API_KEY"]
    params = {
        "api-key": api_key,
        "include-related-images": "false",
    }
    # organs передаётся как поле multipart-формы, не query-параметр
    files = [
        ("images", (filename, image_bytes, "image/jpeg")),
        ("organs", (None, "auto")),
    ]

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(PLANTNET_URL, params=params, files=files)
        if not response.is_success:
            raise RuntimeError(f"PlantNet {response.status_code}: {response.text[:300]}")


    data = response.json()
    results = data.get("results", [])

    if not results:
        return {"name": None, "sci": None, "score": 0.0}

    top = results[0]
    score = top.get("score", 0.0)
    sci = top["species"]["scientificNameWithoutAuthor"]
    common = top["species"].get("commonNames", [])
    name = common[0] if common else sci

    if score < SCORE_THRESHOLD:
        return {"name": None, "sci": sci, "score": round(score, 3)}

    return {"name": name, "sci": sci, "score": round(score, 3)}
