from fastapi import FastAPI
from pydantic import BaseModel
from backend.LLM_connection import get_hotel_recommendations

app = FastAPI()

class UserInput(BaseModel):
    user_prompt: str

@app.post("/api/hotel")
async def get_hotels(input: UserInput):
    print("Received user prompt:", input.user_prompt)
    hotels = get_hotel_recommendations(input.user_prompt)
    print("Generated hotel recommendations:", hotels)
    return {"answer": hotels }
