# 1. 프로젝트 소개
#### Flask를 이용한 폴더 모니터링 서버
- 기술 스택 (Python, REST, WebSocket, DBMS 등)
- 사용된 라이브러리 (Flask, SQLAlchemy 등)
# 2. 프로젝트 목표
#### 클라이언트에서 전달 받은 정보를 Database에 반영하고, 다른 클라이언트에 Broadcast 전송
- RESTful API 지원
- 클라이언트를 구분하여 Broadcast 전송
# 3. 모듈 설명
#### item_dao
- SQLAlchemy를 이용해서 MySQL에 접근
#### item_service
- ItemDao를 이용해서 MySQL을 관리
#### item_endpoint
- 클라이언트에게 필요한 RESTful Endpoint 정의
#### websocket
- Broadcast 전송을 위한 클라이언트간 WebSocket 프로토콜 지원
#### gc
- S3 Storage Object에 대한 garbage collection 기능 구현
# 4. 프로젝트 구성도
- sample
