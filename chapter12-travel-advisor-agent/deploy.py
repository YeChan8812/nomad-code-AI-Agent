import dotenv
dotenv.load_dotenv()
import os
import vertexai
import vertexai.agent_engines
from travel_advisor_agent.agent import travel_advisor_agent
from vertexai.preview import reasoning_engines

vertexai.init(
    project=os.environ.get("PROJECT_ID"),
    location=os.environ.get("LOCATION"),
    staging_bucket=os.environ.get("BUCKET")
)

app = reasoning_engines.AdkApp(
    agent=travel_advisor_agent,
    enable_tracing=True,
)

remote_app = vertexai.agent_engines.create(
    display_name="Travel Advisor Agent",
    agent_engine=app,
    requirements=[
        "google-cloud-aiplatform[adk,agent-engines]",
        "litellm"
    ],
    extra_packages=[
        "travel_advisor_agent"
    ],
    env_vars={
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY")
    }
)