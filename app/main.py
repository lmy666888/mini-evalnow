from fastapi import FastAPI

from app.auth import router as auth_router
from app.rbac import router as rbac_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(rbac_router)


@app.get("/")
def read_root():
    return {"message": "Mini EvalNow API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
