from fastapi import FastAPI
from app.routers import note, user, auth, note_shares

app = FastAPI(title="User Management API")

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(note.router)
app.include_router(note_shares.router)

@app.get("/")
def root():
    return {"message": "API Running"}