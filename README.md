## 문제에 대한 접근법 및 코드 결과물 설명

### 사용 항목과 그 이유

1. **임베딩** : `OpenAI`의 `text-embedding-3-small` 모델을 사용했습니다.
    - ada 모델보다 최근에 발표된 모델로 성능이 더욱 우수하며 비용은 `20%` 수준입니다.
    - large 모델보다 속도가 빠를 것으로 예상되어 사용했습니다.
2. **채팅** : `OpenAI`의 `gpt-4o-mini` 를 사용했습니다.
    - gpt-4o 모델에 비해 입출력토큰 비용은 `6%` 수준입니다.
    - 총 개발에 사용된 비용은 $0.1 미만입니다.
    - 출처 : [https://openai.com/api/pricing/](https://openai.com/api/pricing/)
3. **VectorDB** : `Milvus` 를 사용했습니다.
    - Chroma에 비해 빠른 검색이 가능하다고 알려져 있습니다.
    [단일 쿼리 실행 속도에 대해 직접 테스트 해본 실제 결과는 미미한 성능이었습니다.](https://github.com/kooqooo/mirae-asset-ai-data-festa/blob/af89c5b35f25f1accc699b2f7a120885d86843b9/data/vectorstores.py#L68C3-L95C58)
    - FAISS도 GPU 가속을 지원하고 빠른 검색이 가능하지만, Milvus의 문서가 상대적으로 풍부하여 개발의 용이성측면에서 이점이 있었습니다.
    - 인덱싱 방식과 거리 방식에 대한 설명과 간단한 검색 테스트의 결과는 아래의 PR링크에서 확인이 가능합니다.
     [벡터 데이터베이스로 Milvus 사용하기 #9](https://github.com/kooqooo/naver-smartstore-faq-chatbot/pull/9)
4. **BE** : `FastAPI` 를 사용했습니다. 
    - 초기 설정이 복잡한 Django에 비해 쉽게 구현할 수 있습니다.
    - FastAPI는 ASGI 프레임워크로 비동기 처리가 용이하여 다른 파이썬 웹 프레임워크와 비교해서 성능이 좋다고 알려져 있습니다.
5. **FE** : `Streamilt`을 사용했습니다. 
    - 파이썬을 사용하여 러닝 커브가 낮습니다.
    - 스트림 방식의 출력을 직관적으로 확인할 수 있어서 편리했습니다.
6. 패키지 관리 도구 : `uv`를 사용했습니다.
    - Rust로 개발되어 Pip, Poetry 보다 빠른 속도가 주요 특징입니다.
    - 기존에 Pip, Poetry, Anaconda 방식을 선호했지만, 속도를 경험하고 uv만 사용하게 되었습니다.
    - 그럼에도 아직 베타버전으로 버그가 있고 잦은 업데이트로 사용 방법이 바뀌는 경우가 있어서 프로덕션 환경에서는 부적합합니다.

## 문제 접근 방법

### 데이터 전처리

- FAQ 관련 `.pkl` 파일을 사용하기 편한 형태로 전처리 하였습니다.
- 전처리 과정 설명 : [pickle 데이터 전처리 #2](https://github.com/kooqooo/naver-smartstore-faq-chatbot/pull/2)

### 임베딩 과정에서 400 Bad Request 에러

이슈 링크 : [[BUG] OpenAI 임베딩에서 400 Error #8](https://github.com/kooqooo/naver-smartstore-faq-chatbot/issues/8)

- 해당 에러는 전체 문서 임베딩을 하나의 요청에 시도해서 발생한 문제로 예상됩니다.
- 어느 부분에서 문제가 발생하는지 한 문장씩 임베딩을 시도하고 문제가 발생하면 예외처리로 확인하고자 한 결과, 정상적으로 처리되었습니다.
- 만약 적당한 크기로 묶어서 요청을 보내면 훨씬 빠르게 임베딩이 가능할 것입니다.

### 문서 검색 과정

1. 사용자 질문과 유사한 FAQ 데이터에서 제목에 해당하는 부분을 벡터로 임베딩해서
2. 벡터 데이터베이스의 인덱스를 생성하였습니다.
3. 사용자의 질문을 임베딩 후 벡터 데이터베이스에서 유사도 검색을 하였습니다.

### 프롬프트

프롬프트와 대화 내역을 데이터 클래스와 객체로 관리하여 유연한 조작과 렌더링이 가능했습니다.
→ 해당 코드 : [message.py](https://github.com/kooqooo/naver-smartstore-faq-chatbot/blob/main/src/message_template.py)

프롬프트는 하드코딩이 아닌 별도의 텍스트로 저장하여 수정이 간편합니다.

기본적인 프롬프트 엔지니어링 기법을 사용했습니다.

1. 역할 부여
2. 지시 사항
3. ~~few-shot~~ 
→ 입력 토큰이 커질 것을 우려하여 해당 방법은 사용하지 않았습니다.
→ 추가적으로 적절한 예시를 주는 것이 쉽지 않았습니다.

관련 이슈 링크 : [[FEAT] 프롬프트 관리 #11](https://github.com/kooqooo/naver-smartstore-faq-chatbot/issues/11)

### 대화 맥락 이해

- 대화가 이어어지면 대화 내역에 계속 추가를 하여 새로운 요청에 보내주었습니다.
- 대화 내용은 서버에서 관리하는 것이 정석적인 방법으로 이해하고 있습니다. 그럼에도 우선 기능 구현을위해 악의적인 사용자는 없다고 가정하고 코드를 작성하였습니다. 따라서 현재 코드에서는 Front-end 부분인 Streamlit 페이지의 세션 상태로 관리[[1]](https://github.com/kooqooo/naver-smartstore-faq-chatbot/blob/1874cbcd1482312c7fbc545e9ea0bea126cc6da0/app.py#L25C1-L28C51)[[2]](https://github.com/kooqooo/naver-smartstore-faq-chatbot/blob/1874cbcd1482312c7fbc545e9ea0bea126cc6da0/src/front/utils.py#L84-L86)합니다.
관련 이슈 : [[FEAT] FastAPI로 간단한 API 만들기 #13](https://github.com/kooqooo/naver-smartstore-faq-chatbot/issues/13)
- 대화가 길어질 경우를 대비하여 요약이나 슬라이딩 윈도우 방식으로 토큰 수를 관리하려고 했으나 gpt-4o, gpt-4o-mini 모델 모두 context window는 128,000 토큰, max output tokens는 16,384 토큰만큼 처리가 가능합니다. 따라서 해당 부분은 넉넉하다고 판단하였고 다른 부분부터 처리하였습니다.
**관련 내용** : [https://platform.openai.com/docs/models#gpt-4o](https://platform.openai.com/docs/models#gpt-4o)

### 답변 품질 향상시키기 위한 노력

- 가끔 답변 품질이 떨어지는 문제가 있는데, 근본적인 원인은 검색된 데이터가 부적절하기 때문입니다.
- 처리 속도가 늦어지는 단점이 있지만, 해당 문제를 해결하기 위한 아이디어는 아래의 이슈 링크에서 더욱 자세하게 확인하실 수 있습니다.
[[FEAT] 채팅 품질 강화 #15](https://github.com/kooqooo/naver-smartstore-faq-chatbot/issues/15)

### 코드 결과물 설명

- `data/` : 저장될 데이터 및 데이터 처리 관련 스크립트
- `prompts/` : 프롬프트 모음 디렉토리
- `src/` : 기타 스크립트
- `app.py` : Streamlit
- `main.py` : FastAPI

```bash
📦naver-smartstore-faq-chatbot
 ┣ 📂data
 ┃ ┣ 📜db_manager.py # VectorDB 불러오기, 검색, 필터링
 ┃ ┣ 📜embeddings.py # 임베딩
 ┃ ┣ 📜milvus.db # VectorDB 인덱스 파일
 ┃ ┗ 📜preprocess_pickle.py # 피클 파일 전처리 및 저장
 ┣ 📂prompts
 ┃ ┗ 📜chat_system_prompt.txt # 프롬프트
 ┣ 📂src
 ┃ ┣ 📂front
 ┃ ┃ ┗ 📜utils.py # Streamlit에서 사용할 함수 모음
 ┃ ┣ 📜config.py # 환경변수 관리 등
 ┃ ┗ 📜message_template.py # 메시지 관련 클래스
 ┣ 📜app.py # Streamlit 
 ┣ 📜docker-compose.yml # 윈도우에서 실행시에 사용할 도커 컴포즈
 ┗ 📜main.py # FastAPI
```

## 3. 2가지 이상의 질의응답 데모

### 추가 질문 제안



### 맥락 기반의 답변



### 관련 없는 질문에 대한 처리



## 4. 코드 실행 방법

- `poetry` 대신 [astral/uv](https://docs.astral.sh/uv/) 패키지로 가상환경을 사용하였습니다.
- `venv` 으로도 사용이 가능하도록 `requirements.txt` 도 첨부하였습다.

### 환경변수 설정

`.env` 파일로 관리했습니다.

```bash
OPENAI_API_KEY=sk-....
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

## 가상환경

### 1. `uv` 사용

```bash
uv sync
source ./.venv/bin/activate # Linux/macOS 용
.\.venv\Scripts\Activate.ps1 # Windows 용
```

### 2. `venv` 사용

```bash
python -m venv .venv
source ./.venv/bin/activate # Linux/macOS 용
.\.venv\Scripts\Activate.ps1 # Windows 용
pip install -r requirements.txt
```

## 실행

### Linux/macOS

`uv` 패키지를 사용하면 실행시 앞에 `uv run` 을 붙여서 실행합니다.

```bash
python main.py

# 새 터미널에서
streamlit run app.py

# uv 사용시 아래 방식으로 실행합니다.
# uv run streamlit run app.py
```

### Windows

```powershell
docker-compose up -d # pymilvus_lite를 지원하지 않으므로 docker 사용

# .\data\에 final_result.pkl 추가 후
python .\data\preprocess_pickle.py # 임베딩 후, 인덱스 생성

python main.py

# 새 터미널에서
streamlit run app.py
```
