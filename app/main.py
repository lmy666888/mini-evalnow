from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Mini EvalNow API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
