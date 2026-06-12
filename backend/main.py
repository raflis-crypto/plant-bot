from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from services import plantnet, llm

app = FastAPI(title="Plant Bot Backend")


class PlantName(BaseModel):
    name: str


class RecipeRequest(BaseModel):
    name: str
    condition: str


@app.post("/identify")
async def identify(file: UploadFile = File(...)):
    image_bytes = await file.read()
    print(f"[identify] received {len(image_bytes)} bytes, filename={file.filename}", flush=True)
    try:
        result = await plantnet.identify(image_bytes, filename=file.filename or "photo.jpg")
        print(f"[identify] result={result}", flush=True)
    except Exception as e:
        print(f"[identify] ERROR: {e}", flush=True)
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
