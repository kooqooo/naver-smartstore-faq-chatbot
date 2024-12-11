from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from src.config import *
from src.message_template import Messages


app = FastAPI()


class ChatRequest(BaseModel):
    messages: List[dict[str, str]]


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    TODO
    1. (추가 예정) context를 적용한 새로운 적절한 질문 생성
    2. 더 적절한 FAQ 데이터 찾기 (voting, ranking 등 후처리가 필요할 수도?)
    3. System prompt 추가
    4. render_all을 사용하여 불러온 데이터로 렌더링
    """
    messages = Messages()
    for message in request.messages:
        messages.add_message(message["role"], message["content"])

    async def generate():
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages.to_dict(),
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                yield f"data: {content}\n\n"
        
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)