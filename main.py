from fastapi import FastAPI
from app.routes import router

app = FastAPI()

# Include API routes
app.include_router(router)

@app.get("/")
def home():
    return {"message": "Hack the North Backend API is hard at work!"}
