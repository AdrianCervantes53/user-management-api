from fastapi import FastAPI

app = FastAPI(title="User Management API")

@app.get("/")
def root():
    return {"message": "API Running"}