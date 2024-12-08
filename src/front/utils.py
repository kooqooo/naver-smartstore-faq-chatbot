import streamlit as st

from src.message_template import Message


def write_message(message: Message):
    with st.chat_message(message.role):
        st.write(message.content)


def write_stream_message(message: Message):
    with st.chat_message("assistant"):
        st.write_stream(message.content)


def delete_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]


def get_response_stream(prompt):
    """
    OpenAI API의 스트리밍 응답을 직접 제너레이터로 변환
    """
    try:
        # OpenAI API 호출
        stream = st.session_state.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        full_response = ""

        # 스트리밍 응답을 처리
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        # 전체 응답을 세션 스테이트에 저장
        st.session_state.messages += Message(role="assistant", content=full_response)

    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
