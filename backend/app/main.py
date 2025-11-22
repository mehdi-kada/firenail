from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder

from app.auth.validate import get_current_user
from app.api.routes import tasks, thumbnails
from app.api.subscription import checkout, customer_portal, polar_hooks, status

app = FastAPI(
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)

main_app = app

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "https://firenail.tech",
        "https://www.firenail.tech",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Exception handlers to ensure CORS headers on errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(exc.errors())},
    )

app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(thumbnails.router, prefix="/api/thumbnails", tags=["thumbnails"])
app.include_router(checkout.router, prefix="/api", tags=["subscriptions"])
app.include_router(customer_portal.router, prefix="/api", tags=["subscriptions"])
app.include_router(status.router, prefix="/api", tags=["subscriptions"])
app.include_router(polar_hooks.router, prefix="/api", tags=["webhooks"])

@app.get("/")
async def read_root(user = Depends(get_current_user)):
    return {"Hello": "World", "user": user}
