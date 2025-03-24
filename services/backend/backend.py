from fastapi import FastAPI

app = FastAPI()

# API-Route, die einen GET-Request erwartet
@app.get("/api/user")
async def user_input_eingeben():
    return {"message": "Hallo Welt"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)