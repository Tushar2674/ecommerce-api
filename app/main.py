from fastapi import FastAPI

app = FastAPI(title="E-commerce API")


@app.get("/health")
def health():
    return {"status": "ok"}