from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import database as db

app = FastAPI()

# Allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/counts")
def get_counts():
    """Get latest counts in last 5 minutes"""
    return db.get_latest_counts()

@app.get("/history")
def get_history(limit: int = 50):
    """Get historical records"""
    return db.get_history(limit)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
