from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.validate import get_current_user
from app.api.routes import tasks

app = FastAPI()

main_app = app

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api", tags=["tasks"])

@app.get("/")
async def read_root(user = Depends(get_current_user)):
    return {"Hello": "World", "user": user}