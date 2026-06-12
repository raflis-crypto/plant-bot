import logging
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from services import plantnet, llm

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, force=True)

app = FastAPI(title="Plant Bot Backend")


class PlantName(BaseModel):
    name: str


class RecipeRequest(BaseModel):
    name: str
    condition: str


@app.get("/healthz")
async def healthz():
    import os
    return {
        "plantnet_key_set": bool(os.environ.get("PLANTNET_API_KEY")),
        "groq_key_set": bool(os.environ.get("GROQ_API_KEY")),
        "plantnet_key_prefix": os.environ.get("PLANTNET_API_KEY", "")[:8],
    }


@app.get("/test-groq")
async def test_groq():
    import os
    from groq import AsyncGroq
    api_key = os.environ.get("GROQ_API_KEY", "NOT SET")
    try:
        client = AsyncGroq(api_key=api_key)
        r = await client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5,
        )
        return {"ok": True, "reply": r.choices[0].message.content, "key_prefix": api_key[:8]}
    except Exception as e:
        return {"ok": False, "error": str(e), "key_prefix": api_key[:8]}


@app.get("/test-plantnet")
async def test_plantnet():
    import os, httpx
    api_key = os.environ.get("PLANTNET_API_KEY", "NOT SET")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://my-api.plantnet.org/v2/identify/all",
                params={"api-key": api_key}
            )
        return {"status": r.status_code, "body": r.text[:300], "key_prefix": api_key[:8]}
    except Exception as e:
        return {"error": str(e), "key_prefix": api_key[:8]}


@app.post("/identify")
async def identify(file: UploadFile = File(...)):
    image_bytes = await file.read()
    logging.error("[identify] received %d bytes, filename=%s", len(image_bytes), file.filename)
    try:
        result = await plantnet.identify(image_bytes, filename=file.filename or "photo.jpg")
        logging.error("[identify] result=%s", result)
    except Exception as e:
        logging.error("[identify] ERROR: %s", e)
        raise HTTPException(status_code=502, detail=str(e))
    return result


@app.post("/info")
async def info(body: PlantName):
    try:
        text = await llm.get_info(body.name)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")
    return {"text": text}


@app.post("/recipe")
async def recipe(body: RecipeRequest):
    try:
        text = await llm.get_recipe(body.name, body.condition)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")
    return {"text": text}
