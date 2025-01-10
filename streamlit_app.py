import streamlit as st
import pandas as pd
from openai import OpenAI

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
            df = pd.read_csv(uploaded_file)
            document = df.to_csv(index=False)
            st.write("업로드한 CSV 데이터 미리보기:")
            st.dataframe(df)
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

    # 질문 입력
    st.write("### 질문 입력")
    max_tokens = 3000  # 최대 토큰 수
    question = st.text_area(
        "데이터에 대해 궁금한 점을 입력하세요:",
        placeholder="예: 이 데이터에서 주요 트렌드는 무엇인가요?",
        disabled=not document.strip(),  # 데이터가 없으면 비활성화
    )

    # 입력 토큰 수 계산 및 제한
    def count_tokens(text):
        """텍스트의 토큰 수를 계산합니다."""
        return len(text.split())

    total_tokens = count_tokens(document) + count_tokens(question)
    st.write(f"현재 입력 토큰 수: {total_tokens} / 최대 토큰 수: {max_tokens}")

    if total_tokens > max_tokens:
        st.error("입력 토큰 수가 최대 토큰 수를 초과했습니다. 입력 내용을 줄이세요.")


    def generate_prompt(use_case, document, question):
        """
        선택한 유스케이스에 따라 명령 프롬프트를 생성합니다.
        """
        base_instructions = (
            "당신은 데이터를 기반으로 마케팅 인사이트를 제공하는 전문적인 AI 도우미입니다. "
            "제공된 데이터를 분석하고, 사용자의 질문에 대해 정확하고 실용적인 답변을 제공합니다."
        )

        if use_case == "데이터 요약 및 분석":
            prompt = (
                f"{base_instructions}\n\n"
                "유스케이스: 데이터 요약 및 분석\n"
                "역할: 제공된 데이터를 분석하고, 주요 트렌드, 패턴, 이상치 등을 식별하여 요약해 주세요.\n"
                "요청 사항:\n"
                "- 주요 지표와 그 변화 추이를 설명해 주세요.\n"
                "- 데이터 내의 중요한 패턴이나 트렌드를 식별해 주세요.\n"
                "- 이상치나 주목할 만한 데이터 포인트가 있다면 언급해 주세요.\n"
                "- 가능한 경우, 데이터 시각화에 대한 제안을 포함해 주세요.\n\n"
                f"데이터:\n{document}\n\n"
                f"질문:\n{question}\n"
            )
        elif use_case == "마케팅 전략 제안":
            prompt = (
                f"{base_instructions}\n\n"
                "유스케이스: 마케팅 전략 제안\n"
                "역할: 제공된 데이터를 기반으로 효과적인 마케팅 전략과 액션 플랜을 제안해 주세요.\n"
                "요청 사항:\n"
                "- 데이터에서 도출된 인사이트를 바탕으로 구체적인 마케팅 전략을 제안해 주세요.\n"
                "- 타겟 고객 세그먼트, 추천 마케팅 채널, 캠페인 아이디어 등을 포함해 주세요.\n"
                "- 각 전략의 예상 효과와 실행 방법을 간략히 설명해 주세요.\n"
                "- 예산 고려 사항이나 우선 순위에 대한 제안이 있다면 포함해 주세요.\n\n"
                f"데이터:\n{document}\n\n"
                f"질문:\n{question}\n"
            )
        elif use_case == "데이터 비교 및 평가":
            prompt = (
                f"{base_instructions}\n\n"
                "유스케이스: 데이터 비교 및 평가\n"
                "역할: 제공된 데이터 세트를 비교 분석하고, 성과를 평가하며 개선점을 도출해 주세요.\n"
                "요청 사항:\n"
                "- 비교할 주요 지표와 그 변화 추이를 분석해 주세요.\n"
                "- 두 데이터 세트 간의 유사점과 차이점을 식별해 주세요.\n"
                "- 성과 평가를 기반으로 한 구체적인 개선 방안을 제안해 주세요.\n"
                "- 필요한 경우, 추가 데이터 수집이나 분석 방법에 대한 제안을 포함해 주세요.\n\n"
                f"데이터:\n{document}\n\n"
                f"질문:\n{question}\n"
            )
        else:
            # 기본 유스케이스: 데이터 요약 및 분석
            prompt = (
                f"{base_instructions}\n\n"
                "유스케이스: 데이터 요약 및 분석\n"
                "역할: 제공된 데이터를 분석하고, 주요 트렌드, 패턴, 이상치 등을 식별하여 요약해 주세요.\n"
                "요청 사항:\n"
                "- 주요 지표와 그 변화 추이를 설명해 주세요.\n"
                "- 데이터 내의 중요한 패턴이나 트렌드를 식별해 주세요.\n"
                "- 이상치나 주목할 만한 데이터 포인트가 있다면 언급해 주세요.\n"
                "- 가능한 경우, 데이터 시각화에 대한 제안을 포함해 주세요.\n\n"
                f"데이터:\n{document}\n\n"
                f"질문:\n{question}\n"
            )

        return prompt

    # 분석 실행
    if document.strip() and question.strip() and total_tokens <= max_tokens:
        st.write("### 분석 결과")
        try:
            # 명령 프롬프트 생성
            prompt = generate_prompt(use_case, document, question)

            # OpenAI API 호출
            st.write("GPT가 분석 중입니다...")
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            st.success("분석 완료!")
            st.write_stream(stream)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
