from app.main import app
from app.routers import maintenance_results

app.include_router(maintenance_results.router)