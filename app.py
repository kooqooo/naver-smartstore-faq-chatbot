import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.front.utils import delete_session_state, get_response_stream, write_message
from src.message_template import Message, Messages

# 페이지 설정
st.set_page_config(page_title="스마트스토어 FAQ 챗봇", layout="centered")
st.markdown(
    "<h2 style='text-align: center;'>💬 네이버 스마트스토어 FAQ기반 질의응답</h1>",
    unsafe_allow_html=True,
)


# 세션 상태 초기화
if "chat_started" not in st.session_state:  # 채팅이 시작되었는지 여부
    st.session_state.chat_started = False
if "messages" not in st.session_state:  # 화면에 표시할 메시지
    st.session_state.messages = Messages()
if "client" not in st.session_state:  # OpenAI 클라이언트
    load_dotenv()
    st.session_state.client = OpenAI()


# 채팅 내용 표시
for message in st.session_state.messages:
    write_message(message)

if not st.session_state.chat_started:
    init_assistant_message = Message(
        role="assistant",
        content="안녕하세요. 네이버 스마트스토어 질의응답 챗봇입니다. 무엇을 도와드릴까요?",
    )
    write_message(init_assistant_message)

# user_input = st.chat_input("텍스트를 입력하세요.")
if user_input := st.chat_input("텍스트를 입력하세요."):
    if user_input in [
        "exit",
        "quit",
        "종료",
        "그만",
        "나가기",
        "stop",
        "rmaks",
        "whdfy",
        "skrkrl",
    ]:
        delete_session_state()
        st.stop()
    user_message = Message(role="user", content=user_input)
    st.session_state.messages += user_message
    write_message(user_message)

    # 챗봇 대답
    with st.chat_message("assistant"):
        st.write_stream(get_response_stream(user_input))

    # 채팅 시작
    st.session_state.chat_started = True
