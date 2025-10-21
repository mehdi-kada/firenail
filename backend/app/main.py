from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.validate import get_current_user
from app.api.routes import tasks, thumbnails
from app.api.subscription import checkout, customer_portal, polar_hooks

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
app.include_router(thumbnails.router, prefix="/api/thumbnails", tags=["thumbnails"])
app.include_router(checkout.router, prefix="/api", tags=["subscriptions"])
app.include_router(customer_portal.router, prefix="/api", tags=["subscriptions"])
app.include_router(polar_hooks.router, prefix="/api", tags=["webhooks"])

@app.get("/")
async def read_root(user = Depends(get_current_user)):
    return {"Hello": "World", "user": user}