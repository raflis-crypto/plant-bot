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
    }



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
