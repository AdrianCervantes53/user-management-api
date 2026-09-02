from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import note, note_share, user, auth

app = FastAPI(
    title="User Management API",
    description="User management api proyect",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ]
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(note.router)
app.include_router(note_share.router)

@app.get("/")
def root():
    return {"message": "API Running"}