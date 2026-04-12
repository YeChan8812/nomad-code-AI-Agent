A2A
- Agent가 서로 소통을 하면서 내가 원하는 것에 대한 답변을 해주는 것!
- google에서 이것을 잘 만들었기에 google로 만들어 봄

"from google.adk.a2a.utils.agent_to_a2a import to_a2a" -> to_a2a는 내가 만든 agent를 a2a 연결이 가능하게 만들어줌
- user-facing-agent에 들어가서 adk web으로 에이전트를 실행
- remote_adk_agent에 들어가서 "uvicorn agent:app --port 8001"로 서버 실행 uvicorn은 비동기 방식으로 서버를 실행시켜 주는 모듈 (이 명령어 뒤에 --reload를 임력해주면 수정될 때마다 재시작 함)
- 실행된 서버에서 /.well-known/agent-card.json 으로 들어가면 정의를 확인할 수 있음