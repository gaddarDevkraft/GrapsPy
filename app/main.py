from typing import Union
from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException
from openai import OpenAI
import os

load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.environ.get("DEVKRAFT_OPENAI_API_KEY"))

@app.get("/chat")
def get_chatbot_response(q: str):
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user", "content": q
                }
            ]
        )
        return {"response": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# import uvicorn
# if __name__ == "__main__":
#     uvicorn.run(app, host = "0.0.0.0", port = 8000)
