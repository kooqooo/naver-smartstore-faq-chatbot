import streamlit as st
import requests

from src.message_template import Message, Messages


def write_message(message: Message):
    with st.chat_message(message.role):
        st.write(message.content)


def write_messages(messages: Messages):
    for message in messages:
        write_message(message)


def write_stream_message(message: Message):
    with st.chat_message("assistant"):
        st.write_stream(message.content)

def add_messages_to_session_state(messages: Messages):
    st.session_state.messages += messages


def delete_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]


def get_response_stream(messages: Messages):
    """
    OpenAI API의 스트리밍 응답을 직접 제너레이터로 변환
    """
    try:
        # OpenAI API 호출
        stream = st.session_state.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages.to_dict(),
            stream=True,
        )

        full_response = ""

        # 스트리밍 응답을 처리
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        # # 전체 응답을 세션 스테이트에 저장
        # st.session_state.messages += Message(role="assistant", content=full_response)
        response_message = Messages()
        response_message.add_message(role="assistant", content=full_response)
        add_messages_to_session_state(response_message)

    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")


def get_response_stream_from_fastapi(messages: Messages):
    # TODO: url과 port 번호를 환경 변수로 관리
    url = "http://localhost:8000/chat"
    headers = {"Content-Type": "application/json"}
    data = {"messages": messages.to_dict()}
    response = requests.post(url=url, headers=headers, json=data, stream=True)
    response.raise_for_status()

    full_response = ""
    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                content = line[6:]  # "data: " prefix 제거
                if content == "[DONE]":
                    break
                full_response += content
                yield content
    
    response_message = Messages()
    response_message.add_message(role="assistant", content=full_response)
    add_messages_to_session_state(response_message)