1. Agent의 성능을 평가하는 방법
 - 내가 만든 Agent가 잘 되는지 테스트 하는 것
 - 동일한 input에 항상 동일한 응답이 돌아오는 것이 아니기에 테스트하기 어렵다
 - Google adk로 agent를 테스트하는 방법은 2가지 (Eval 탭에서 설정 가능)
 1) agnet의 tool trajectory 테스트
    - agent가 어떤 tool을 호출하는지 테스트 하는 것 (순서대로 호출 했는지 등)
 2) agent의 response를 테스트

2. 자동 생성된 API를 사용해서 Agent를 실행하는 방법
 - adk api_server로 adk 서버를 실행할 수 있음
 - run과 run_sse 엔드포인트로 agent를 실행할 수 있음
  - 여기서 sse는 websocket과 동일한 기능을 한다고 생각하면 됨

3. Agent를 수동으로 사용하는 방법