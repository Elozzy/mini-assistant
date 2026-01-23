from fastapi import FastAPI

app = FastAPI(title="BlackOps")

@app.get("/health")
def health():
    return {"status": "ok"}
