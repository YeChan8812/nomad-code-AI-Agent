from langgraph.graph import StateGraph, START, END
from langgraph.types import Send, interrupt, Command
from langchain.chat_models import init_chat_model
from typing import TypedDict
from openai import OpenAI
from typing_extensions import Annotated
import subprocess
import textwrap
import operator
import base64

llm = init_chat_model("openai:gpt-4o-mini")

class State(TypedDict):

    video_file: str
    audio_file: str
    transcription: str
    summaries: Annotated[list[str], operator.add]
    thumbnail_prompts: Annotated[list[str], operator.add]
    thumbnail_sketches: Annotated[list[str], operator.add]
    final_summary: str
    user_feedback: str
    chosen_prompt: str


def extract_audio(state: State):
    # 비디오 파일 이름으로 mp3 파일이름 명명
    output_file = state["video_file"].replace("mp4", "mp3")
    # 아래는 ffmpeg로 영상에서 오디오를 추출할 때 사용하는 명령어임
    command=[
        "ffmpeg", # 실행 모듈
        "-i", # input
        state["video_file"], #
        "-filter:a", # 오디오에 필터를 넣는 것
        "atempo=2.0", # 속도를 빠르게해서 토큰 값을 아끼기
        "-y", # 이렇게 설정하면 ffmpeg가 묻는 질문에 전부 Y로 답할 수 있음
        output_file # 결과 파일 이름
    ]
    # node의 childprocess와 동일한 역할인 듯
    subprocess.run(command)
    return { "audio_file": output_file }

def transcribe_audio(state: State):
    client = OpenAI()
    with open(state["audio_file"], "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file,
            language="ko",
            prompt="조선, 세종, 왕", # 여기서 오디오의 특정 단어들을 제공해주면 AI가 이해하기 더 쉬워진다
        )
        return {"transcription": transcription}
    
def dispatch_summarizers(state: State):
    transcription = state["transcription"]
    chunks = []
    # 이렇게 하면 긴 글자를 각 파트별로 나눌 수 있음 index는 각각의 아이디가 됨
    for i, chunk in enumerate(textwrap.wrap(transcription, 350)):
        chunks.append({"id": i+1, "chunk": chunk})
    return [Send("summarize_chunk", chunk) for chunk in chunks]

def summarize_chunk(chunk):
    chunk_id = chunk["id"]
    chunk = chunk["chunk"]

    response = llm.invoke(
        f"""
        Please summarize the following text in Korean.

        Text: {chunk}
        """
    )
    summary = f"[Chunk {chunk_id}] {response.content}"
    return {"summaries": [summary]}

def mega_summary(state: State):
    all_summaries = "\n".join(state["summaries"])

    prompt = f"""
        You are given multiple summaries of different chunks from a video transcription.

        Please create a comprehensive final summary that combines all the key points in Korean.

        Individual summaries: {all_summaries}
    """

    response = llm.invoke(prompt)

    return {"final_summary": response.content}

def dispatch_artists(state: State):
    return [
        # 뒤에서 주어지는 배열 만큼 generate_thumbnails를 실행
        Send("generate_thumbnails", {"id": i, "summary": state["final_summary"]}) for i in [1, 2, 3]
    ]

def generate_thumbnails(args):
    concept_id = args["id"]
    summary = args["summary"]
    
    prompt = f"""
    Based on this video summary, create a detailed visual prompt for a YouTube thumbnail.

    Create a detailed prompt for generating a thumbnail image that would attract viewers. Include:
        - Main visual elements
        - Color scheme
        - Text overlay suggestions
        - Overall composition
    
    Summary: {summary}
    """

    response = llm.invoke(prompt)

    thumbnail_prompt = response.content

    client = OpenAI()

    result = client.images.generate(
        model="gpt-image-1.5",  # 영상에서는 4가 나왔을 것이라 했으나 1.5...
        prompt=thumbnail_prompt,
        quality="low",
        moderation="low",
        size="auto",
    )

    image_bytes = base64.b64decode(result.data[0].b64_json)

    filename = f"thumbnail_{concept_id}.jpg"

    # 만들어진 이미지를 파일로 저장
    with open(filename, "wb") as file:
        file.write(image_bytes)

    return {
        "thumbnail_prompts": [thumbnail_prompt],
        "thumbnail_sketches": [filename],
    }

def human_feedback(state: State):
    answer = interrupt({
        "chosen_thumbnail": "Which thumbnail do you like the most?",
        "feedback": "Provide any feedback or changes you'd like for the final thumbnail."
    })

    user_feedback = answer["user_feedback"]
    chosen_prompt = answer["chosen_prompt"]

    return {"user_feedback": user_feedback, "chosen_prompt": state["thumbnail_prompts"][chosen_prompt-1]}

def generate_hd_thumbnail(state: State):

    chosen_prompt = state["chosen_prompt"]
    user_feedback = state["user_feedback"]

    prompt = f"""
    You are a professional YouTube thumbnail designer. Take this original thumbnail prompt and create an enhanced version that incorporates the user's specific feedback.

    ORIGINAL PROMPT:
    {chosen_prompt}

    USER FEEDBACK TO INCORPORATE:
    {user_feedback}

    Create an enhanced prompt that:
        1. Maintains the core concept from the original prompt
        2. Specifically addresses and implements the user's feedback requests
        3. Adds professional YouTube thumbnail specifications:
            - High contrast and bold visual elements
            - Clear focal points that draw the eye
            - Professional lighting and composition
            - Optimal text placement and readability with generous padding from edges
            - Colors that pop and grab attention
            - Elements that work well at small thumbnail sizes
            - IMPORTANT: Always ensure adequate white space/padding between any text and the image borders
    """

    response = llm.invoke(prompt)

    final_thumbnail_prompt = response.content

    client = OpenAI()

    result = client.images.generate(
        model="gpt-image-1.5", # 영상에서는 4가 나왔을 것이라 했으나 1.5...
        prompt=final_thumbnail_prompt,
        quality="high",
        moderation="low",
        size="auto",
    )

    image_bytes = base64.b64decode(result.data[0].b64_json)

    with open("thumbnail_final.jpg", "wb") as file:
        file.write(image_bytes)

graph_builder = StateGraph(State)

graph_builder.add_node("extract_audio", extract_audio)
graph_builder.add_node("transcribe_audio", transcribe_audio)
graph_builder.add_node("summarize_chunk", summarize_chunk)
graph_builder.add_node("mega_summary", mega_summary)
graph_builder.add_node("generate_thumbnails", generate_thumbnails)
graph_builder.add_node("human_feedback", human_feedback)
graph_builder.add_node("generate_hd_thumbnail", generate_hd_thumbnail)

graph_builder.add_edge(START, "extract_audio")
graph_builder.add_edge("extract_audio", "transcribe_audio")
graph_builder.add_conditional_edges("transcribe_audio", dispatch_summarizers, ["summarize_chunk"])
graph_builder.add_edge("summarize_chunk", "mega_summary")
graph_builder.add_conditional_edges("mega_summary", dispatch_artists, ["generate_thumbnails"])
graph_builder.add_edge("generate_thumbnails", "human_feedback")
graph_builder.add_edge("human_feedback", "generate_hd_thumbnail")
graph_builder.add_edge("generate_hd_thumbnail", END)

graph = graph_builder.compile(name="mr_thumbs")