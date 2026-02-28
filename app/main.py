from fastapi import FastAPI
from app.routers import user
from app.routers import auth


app = FastAPI(title="User Management API")

app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "API Running"}