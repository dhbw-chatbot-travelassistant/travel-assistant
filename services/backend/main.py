from fastapi import FastAPI
from pydantic import BaseModel
from data.LLM_connection import get_hotel_recommendations

app = FastAPI()

class UserInput(BaseModel):
    user_prompt: str

@app.post("/api/hotel")
async def get_hotels(input: UserInput):
    hotels = get_hotel_recommendations(input.user_prompt)
    return {"hotels": hotels }
