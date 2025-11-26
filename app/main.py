from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.core.database import engine, Base
from app.routers import users, posts, test, auth
from app.core.auth import get_current_user
from app.models.models import User
from app.routers.attendance import router as attendance_router
from app.routers.situational import router as situational_router
from app.routers.chat import router as chat_router

# Create database tables
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
#          FIX SWAGGER + OPENAPI URL
# ---------------------------------------------------------
app = FastAPI(
    title="Psychology API",
    description="API for Psychology Application.",
    version="1.0.0",
    docs_url=None,  # disable default
    redoc_url=None,  # disable default
    openapi_url="/openapi.json"
)

# ---------------------------------------------------------
#          CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
#          ROUTERS
# ---------------------------------------------------------
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(posts, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(test, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(attendance_router, prefix="/api/v1", dependencies=[Depends(get_current_user)])
app.include_router(situational_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


# ---------------------------------------------------------
#          OPENAPI CUSTOM
# ---------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema.setdefault("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"Bearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ---------------------------------------------------------
#          CUSTOM SWAGGER UI
# ---------------------------------------------------------
@app.get("/swagger", include_in_schema=False)  # 👈 FIXED
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",  # 👈 FIXED
        title=app.title + " - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "none",
            "filter": True,
            "persistAuthorization": True,
            "displayRequestDuration": True,
            "tryItOutEnabled": True,
        },
    )


# ---------------------------------------------------------
#          ROOT
# ---------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to Psychology API"}


# ---------------------------------------------------------
#          PERMISSION HELPERS
# ---------------------------------------------------------
def admin_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user


def premium_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_premium:
        raise HTTPException(status_code=403, detail="Premium only")
    return current_user
