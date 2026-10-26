from fastapi import FastAPI
from routes.products import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def home():
    return {"message": "Welcome to StockFlow API"}

@app.get("/about")
def about():
    return {"project": "StockFlow API",
            "developer": "Nythan John Rivera"}
