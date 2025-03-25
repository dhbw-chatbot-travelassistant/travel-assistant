from fastapi import FastAPI
from pydantic import BaseModel
import services.data.LLM_connection as llm_connection

app = FastAPI()

class UserInput(BaseModel):
    user_prompt: str

@app.post("/api/hotel")
async def get_hotels(input: UserInput):

    hotels = llm_connection.get_hotel_recommendations(input.user_prompt)

    return {"hotels":  "{hotels}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)