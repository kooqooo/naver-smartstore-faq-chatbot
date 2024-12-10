import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.front.utils import (delete_session_state,
                            get_response_stream,
                            write_message,
                            write_messages,
                            add_messages_to_session_state,)
                            # add_backend_messages_to_session_state,)
from src.message_template import Message, Messages
from data.db_manager import client as milvus_client

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
if "backend_messages" not in st.session_state:  # 백엔드에 전달할 메시지
    st.session_state.backend_messages = Messages()
if "system_prompt_messages" not in st.session_state:  # 프롬프트를 담은 메시지
    chat_system_prompt_path = "prompts/chat_system_prompt.txt"
    st.session_state.system_prompt_messages = Messages.from_prompt_file(chat_system_prompt_path)
if "milvus" not in st.session_state:  # Milvus 클라이언트
    st.session_state.milvus = milvus_client
if "client" not in st.session_state:  # OpenAI 클라이언트
    load_dotenv()
    st.session_state.client = OpenAI()


# 채팅 내용 표시
write_messages(st.session_state.messages)

if not st.session_state.chat_started:
    init_assistant_message = Messages()
    init_assistant_message.add_message(
        role="assistant",
        content="안녕하세요. 네이버 스마트스토어 질의응답 챗봇입니다. 무엇을 도와드릴까요?",
    )
    write_messages(init_assistant_message)
    add_messages_to_session_state(init_assistant_message)
    st.session_state.chat_started = True

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
    user_message = Messages()
    user_message.add_message(role="user", content=user_input) # 구매 확정에 대해서 알려주세요
    write_messages(user_message)
    add_messages_to_session_state(user_message)

    # reference 넣어주기
    reference = """
    ### question: 구매확정은 무엇인가요?
    ### answer:
구매자가 판매자에게 상품 주문 또는 서비스를 제공받은 후 해당 상품을 정상 수령하였거나 서비스에 대해 만족한 경우 "구매확정" 처리를 하게 됩니다.
이처럼 구매확정 처리는 판매자에게 구매대금을 정산 해도 된다는 구매자의 의사표시이기 때문에 구매확정된 이후 판매자에게 정산이 진행됩니다. 

※ 참고. 구매자가 구매확정을 지연시킬 경우를 대비하여,  일정 기간이 지나면 자동으로 구매확정 처리됩니다. 

자동 구매확정 도움말 바로 가기》"""

    st.session_state.backend_messages = st.session_state.system_prompt_messages.render_all({"reference": reference})
    st.session_state.backend_messages += st.session_state.messages

    # 챗봇 대답
    with st.chat_message("assistant"):
        st.write_stream(get_response_stream(st.session_state.backend_messages))

