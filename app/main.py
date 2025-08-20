from fastapi import FastAPI
from app.Scripts.create_admin import create_initial_admin
from app.api.v1.users import router as users_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.interviews import router as interviews_router
from app.api.v1 import applications
from fastapi.openapi.utils import get_openapi
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings  

app = FastAPI()

@app.on_event("startup")
async def startup_db_client():
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        await client.server_info()  # Ping the server
        print("✅ MongoDB connected")
    except Exception as e:
        print("❌ MongoDB connection failed:", e)

    await create_initial_admin()

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Recruitment System"}

app.include_router(users_router, prefix="/api/v1/users", tags=["Authentication"])
# Note: The admin router is included here for backward compatibility, but you may want to separate
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(resumes_router, prefix="/api/v1/resumes", tags=["Resumes"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(interviews_router, prefix="/api/v1/interviews", tags=["Interviews"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["Applications"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI Recruitment System API",
        version="1.0.0",
        description="API for managing users, resumes, jobs, applications, and dashboard.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
