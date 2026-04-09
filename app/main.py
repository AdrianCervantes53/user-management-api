from fastapi import FastAPI
from app.routers import note, note_share, user, auth

app = FastAPI(title="User Management API")

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(note.router)
app.include_router(note_share.router)

@app.get("/")
def root():
    return {"message": "API Running"}