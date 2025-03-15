from fastapi import FastAPI
from login import router as auth_router
from posts import router as posts_router
import uvicorn

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(posts_router, prefix="/posts", tags=["Posts"])

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)