import dotenv
dotenv.load_dotenv()

import pytest
from main import graph
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model

llm = init_chat_model("openai:gpt-4o-mini")

class SimilarityScoreOutput(BaseModel):
    similarity_socre: int = Field(description="How similar is the response to the examples?", gt=0, lt=100)

RESPONSE_EXAMPLES = {
    "urgent": [
        "Thank you for your urgent message. We are addressing this immediately and will respond as soon as possible.",
        "We've received your urgent request and are prioritizing it. Our team is on it right away.",
        "This urgent matter has our immediate attention. We'll respond promptly.",
    ],
    "normal": [
        "Thank you for your email. We'll review it and get back to you within 24-48 hours.",
        "We've received your message and will respond soon. Thank you for reaching out.",
        "Thank you for contacting us. We'll process your request and respond shortly.",
        "Thank you for the update. I will review the information and follow up as needed.",
        "Thank you for the update on the project status. I will review and follow up by the end of the week.",
        "Thanks for sharing this update. We'll review and respond accordingly.",
    ],
    "spam": [
        "This message has been flagged as spam and filtered.",
        "This email has been identified as promotional content.",
        "This message has been marked as spam.",
    ],
}

def judge_response(response: str, category: str):
    s_llm = llm.with_structured_output(SimilarityScoreOutput)

    examples = RESPONSE_EXAMPLES[category]
    result = s_llm.invoke(
        f"""
        Score how similar this response is to the examples.

        Category: {category}

        Examples:
        {"\n".join(examples)}

        Response to evaluate:
        {response}

        Scoring criteria:
        - 90-100: Very similar in tone, content, and intent
        - 70-89: Similar with minor differences
        - 50-69: Moderately similar, captures main idea
        - 30-49: Some similarity but missing key elements
        - 0-29: Very different or inappropriate

        """
    )
    return result.similarity_socre

# uv run pytest tests.py -vv

config = {"configurable": {"thread_id": "1"}}

# 하드코딩 된 graph 테스트 방법
"""
# graph 전체를 테스트
@pytest.mark.parametrize(
    "email, expected_category, expected_score",
    [
        ("this is urgent!", "urgent", 10),
        ("I wanna talk to you", "normal", 5),
        ("i have an offer for you", "spam", 1)
    ]
)
def test_full_graph(email, expected_category, expected_score):

    result = graph.invoke({"email": email}, config=config)

    # 조건을 적을 수 있고 조건이 참이면 넘어가고 아니면 오류가 발생함
    assert result['category'] == expected_category
    assert result['priority_score'] == expected_score

# 원하는 노드만 테스트
def test_individual_node():

    # nodes로 테스트를 원하는 노드를 가져와서 실행할 수 있다.
    result = graph.nodes["categorize_email"].invoke({"email": "check out this offer"})
    assert result["category"] == "spam"

    result = graph.nodes["assing_priority"].invoke({"category": "spam"})
    assert result["priority_score"] == 1

    result = graph.nodes["draft_response"].invoke({"category": "spam"})
    assert "Go away" in result["response"]

def test_partial_execution():

    # 이렇게 하면 categorize_email이 이미 실행된 것처럼 하고 나머지 노드를 실행할 수 있음
    graph.update_state(
        # DB 호출
        config=config,
        # 이미 categorize_email 노드가 실행이 됐다는 가정 하에 주어진 email이 spam이라는 것을 알려줌 (업데이트 하고 싶은 state를 넣어줌)
        values={"email": "please check out this offer", "category": "spam"},
        # categorize_email 노드와 같다고 표시
        as_node="categorize_email"
    )

    result = graph.invoke(
        None,
        config=config,
        interrupt_after="draft_response", # 해당 노드 다음에 중단을 할 수 있게 해줌 노드 이전에는 interrupt_before을 사용하면 됨
    )

    assert result["priority_score"] == 1
"""

# llm을 사용한 graph 테스트 
@pytest.mark.parametrize(
    "email, expected_category, min_score, max_score",
    [
        ("this is urgent!", "urgent", 8, 10),
        ("I wanna talk to you", "normal", 4, 7),
        ("i have an offer for you", "spam", 1, 3)
    ]
)
def test_full_graph(email, expected_category, min_score, max_score):

    result = graph.invoke({"email": email}, config=config)

    # 조건을 적을 수 있고 조건이 참이면 넘어가고 아니면 오류가 발생함
    assert result['category'] == expected_category
    assert min_score <= result['priority_score'] <= max_score

# 원하는 노드만 테스트
def test_individual_node():

    # nodes로 테스트를 원하는 노드를 가져와서 실행할 수 있다.
    result = graph.nodes["categorize_email"].invoke({"email": "check out this offer"})
    assert result["category"] == "spam"

    result = graph.nodes["assing_priority"].invoke({"category": "spam", "email": "buy this one"})
    assert 1 <= result['priority_score'] <= 3

    result = graph.nodes["draft_response"].invoke({
        "category": "spam",
        "email": "Get rich quick!!! I have a pyramid scheme for you!!",
        "priority_score": 1,
    })

    similarity_score = judge_response(result["response"], "spam")
    assert similarity_score >= 70

def test_partial_execution():

    # 이렇게 하면 categorize_email이 이미 실행된 것처럼 하고 나머지 노드를 실행할 수 있음
    graph.update_state(
        # DB 호출
        config=config,
        # 이미 categorize_email 노드가 실행이 됐다는 가정 하에 주어진 email이 spam이라는 것을 알려줌 (업데이트 하고 싶은 state를 넣어줌)
        values={"email": "please check out this offer", "category": "spam"},
        # categorize_email 노드와 같다고 표시
        as_node="categorize_email"
    )

    result = graph.invoke(
        None,
        config=config,
        interrupt_after="draft_response", # 해당 노드 다음에 중단을 할 수 있게 해줌 노드 이전에는 interrupt_before을 사용하면 됨
    )

    assert 1 <= result['priority_score'] <= 3