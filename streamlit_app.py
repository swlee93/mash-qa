import streamlit as st
import pandas as pd
from openai import OpenAI
import tiktoken

# 토큰 수 계산 함수


def count_tokens(text, model="gpt-3.5-turbo"):
    """텍스트의 토큰 수를 정확하게 계산합니다."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# 명령어 프롬프트 생성 함수


def generate_prompt(use_case, document, question):
    """
    Create a prompt based on the selected use case. 
    Focus on providing deep insights, numerical evidence (if relevant), 
    and clear, actionable recommendations.
    """

    base_instructions = (
        "You are a professional AI assistant specializing in data-driven marketing insights. "
        "Analyze the provided data from multiple perspectives, offering deeper insights "
        "and evidence that basic charts or tables might not reveal."
    )

    if use_case == "데이터 요약 및 분석":
        prompt = (
            f"{base_instructions}\n\n"
            "Use Case: Data Summary and Analysis\n"
            "Task: Provide a comprehensive analysis of the given data, including trends, patterns, and anomalies.\n"
            "Requirements:\n"
            "1. Explain the meaning and relevance of each field.\n"
            "2. Where possible, Cross-examine multiple metrics to uncover insights beyond simple charts or tables.\n"
            f"Data:\n{document}\n\n"
            f"Question:\n{question}\n"
        )

    elif use_case == "마케팅 전략 제안":
        prompt = (
            f"{base_instructions}\n\n"
            "Use Case: Marketing Strategy Recommendations\n"
            "Task: Propose effective marketing strategies (channels, targeting, budget, etc.) "
            "based on the data.\n"
            "Requirements:\n"
            "1. Leverage data-driven insights to form detailed action plans.\n"
            "2. Provide numerical or factual evidence to support each recommendation.\n"
            "3. If possible, outline expected KPIs or success metrics.\n\n"
            f"Data:\n{document}\n\n"
            f"Question:\n{question}\n"
        )

    elif use_case == "데이터 비교 및 평가":
        prompt = (
            f"{base_instructions}\n\n"
            "Use Case: Data Comparison and Evaluation\n"
            "Task: Compare the given datasets, identify key differences and similarities, "
            "and propose improvements.\n"
            "Requirements:\n"
            "1. Compare key metrics or trends across the datasets.\n"
            "2. Identify correlations or disparities and highlight potential causes.\n"
            "3. Suggest follow-up analyses or data to gather, if needed.\n\n"
            f"Data:\n{document}\n\n"
            f"Question:\n{question}\n"
        )

    else:
        # Default: Data Summary and Analysis
        prompt = (
            f"{base_instructions}\n\n"
            "Use Case: Data Summary and Analysis\n"
            "Task: Provide a comprehensive analysis of the given data, including trends, patterns, and anomalies.\n"
            "Requirements:\n"
            "1. Explain the meaning and relevance of each field.\n"
            "2. Cross-examine multiple metrics to uncover insights beyond simple charts or tables.\n"
            "3. Where possible, suggest data visualizations or additional interpretation tips.\n\n"
            f"Data:\n{document}\n\n"
            f"Question:\n{question}\n"
        )

    return prompt


# 기본 안내 메시지
st.title("📊 마케팅 데이터 분석 도우미")
st.write(
    """
    데이터를 업로드하거나 직접 입력한 후, 분석 목적(유스케이스)을 선택하고 질문을 입력하세요.
    선택한 유스케이스에 따라 GPT가 데이터를 해석하고 적절한 마케팅 액션을 제안합니다.
    OpenAI API 키를 입력하여 서비스를 사용할 수 있습니다.
    """
)

# OpenAI API 키 입력
openai_api_key = st.text_input("OpenAI API 키 입력", type="password")

if not openai_api_key:
    st.info("OpenAI API 키를 입력해야 사용이 가능합니다.", icon="🗝️")
else:
    # OpenAI 클라이언트 설정
    client = OpenAI(api_key=openai_api_key)

    # 데이터 입력 방식 선택
    st.write("### 데이터 입력 방식 선택")
    input_method = st.radio(
        "데이터를 어떻게 입력하시겠습니까?",
        ("CSV 파일 업로드", "텍스트 직접 입력"),
    )

    # 데이터 업로드 또는 입력
    document = ""
    if input_method == "CSV 파일 업로드":
        uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=("csv",))
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                document = df.to_csv(index=False)
                st.write("업로드한 CSV 데이터 미리보기:")
                st.dataframe(df)
            except Exception as e:
                st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
    elif input_method == "텍스트 직접 입력":
        document = st.text_area(
            "텍스트를 입력하세요:",
            placeholder="분석할 데이터를 여기에 입력하세요.",
        )

    # 유스케이스 선택
    st.write("### 분석 목적(유스케이스) 선택")
    use_case = st.selectbox(
        "원하는 분석 목적을 선택하세요:",
        [
            "데이터 요약 및 분석",
            "마케팅 전략 제안",
            "데이터 비교 및 평가",
        ],
    )

    # 모델 선택
    st.write("### 모델 선택")
    model = st.selectbox(
        "사용할 모델을 선택하세요:",
        [
            "o1-mini-2024-09-12",
            "o1-preview-2024-09-12",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
        index=0  # 기본 선택값
    )

    # 질문 입력
    st.write("### 질문 입력")
    max_tokens = 5000  # 최대 토큰 수
    question = st.text_area(
        "데이터에 대해 궁금한 점을 입력하세요:",
        placeholder="예: 이 데이터에서 주요 트렌드는 무엇인가요?",
        disabled=not document.strip(),  # 데이터가 없으면 비활성화
    )

    # 입력 토큰 수 계산 및 제한
    total_tokens = count_tokens(
        document, model=model) + count_tokens(question, model=model)
    st.caption(f"사용한 입력 토큰 수: **{total_tokens}**/{max_tokens}")

    if total_tokens > max_tokens:
        st.error("입력 토큰 수가 최대 토큰 수를 초과했습니다. 입력 내용을 줄이세요.")

    # 분석 실행 버튼
    if document.strip() and question.strip() and total_tokens <= max_tokens:
        try:
            # 명령 프롬프트 생성
            prompt = generate_prompt(use_case, document, question)

            # 로딩 상태 표시
            with st.spinner("GPT가 분석 중입니다..."):
                stream = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )

            # 답변 표시
            st.write_stream(stream)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
