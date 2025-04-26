from fastapi import FastAPI, status

app = FastAPI()


@app.get("/")
def hello():
    return {"data": {"status", "hello server"}}


import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 8000)
