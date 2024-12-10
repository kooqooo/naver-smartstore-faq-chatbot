import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.front.utils import (delete_session_state,
                            get_response_stream,
                            write_messages,
                            add_messages_to_session_state,)
from src.message_template import Messages
from data.db_manager import search_from_faq, client as milvus_client
from data.embeddings import embed_question

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
if "client" not in st.session_state:  # OpenAI 클라이언트 # 여기에서 굳이 필요 없는 듯
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

    # TODO: 사용자 입력을 임베딩하여 가장 적절한 하나의 reference를 찾도록 수정
    embedded_user_input = embed_question(user_input)
    reference = search_from_faq(embedded_user_input)[:5] # 추후에 get_reference 함수로 변경

    st.session_state.backend_messages = st.session_state.system_prompt_messages.render_all({"reference": str(reference)})
    st.session_state.backend_messages += st.session_state.messages
    from pprint import pprint
    pprint(st.session_state.backend_messages.to_dict())
    # 챗봇 대답
    with st.chat_message("assistant"):
        st.write_stream(get_response_stream(st.session_state.backend_messages))

