import dotenv
dotenv.load_dotenv()
import os
import vertexai
from vertexai import agent_engines

vertexai.init(
    project=os.environ.get("PROJECT_ID"),
    location=os.environ.get("LOCATION"),
)

# deployments = agent_engines.list()

# for deployment in deployments:
#     print(deployment)

SESSION_ID = "4082861057641545728"

remote_app = agent_engines.get(os.environ.get("DEPLOYMENT_ID"))
# remote_app.delete(force=True)

# remote_session = remote_app.create_session(user_id="u_123")
# print(remote_session["id"])

for event in remote_app.stream_query(
    user_id="u_123",
    session_id=SESSION_ID,
    message="I'm going to Laos, any tips?"
):
    print(event, "\n", "="*60)