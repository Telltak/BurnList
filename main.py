from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/structures")
async def structure_index():
    return {"message": "Structure Index"}


@app.get("/structures/{structure_id}")
async def get_structure(structure_id:int):
    return {"structure_id": structure_id}
