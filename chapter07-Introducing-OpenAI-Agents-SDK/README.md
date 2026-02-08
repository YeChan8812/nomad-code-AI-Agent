agent_updated_stream_event
- open AI는 agent swarm를 만들 수 있게 해준다. 그래서 서로 다른 agent끼리 정보를 주고 받을 수 있음, 마치 대화하는 것처럼!
- 이 표시는 하나의 agent에서 다른 agent로 대화가 넘어갈 때 발생하는 이벤트이다.

run_item_stream_event
- run은 while true roop이다.
- run item은 run에서 agent가 취한 action이다.

raw_response_event
- agent에게 무슨 일이 일어나고 있는지 자세하게 제공한다

streamlit (https://streamlit.io)
python으로 UI를 만들 수 있게 해줌!

- 특정 값이 변경될 때마다 전체가 재시작 됨, 즉 data가 변경될 때 해당 파일에 있는 전체가 재시작된다고 이해하면 됨
- 이걸 잘 이해하고 코드를 짜야 실수하지 않음!!

그렇다면 어떻게 상태가 변경되지 않게 저장할 수 있을까?
- session_state를 활용하면 됨