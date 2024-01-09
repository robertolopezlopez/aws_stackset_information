import uvicorn
from fastapi import FastAPI

from config import load_config
from resources.ping import router as ping_router
from resources.status import router as status_router

# Load configuration
try:
    _ = load_config()
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)

app = FastAPI(openapi_url="/api/v1/openapi.json", root_path='/api/v1')

app.include_router(ping_router, tags=["ping"])
app.include_router(status_router, prefix="/status", tags=["status"])

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
