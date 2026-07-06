# Sillok (실록)
 
AI가 조선의 왕이 되어 대화하고, 그 대화 기록이 실록(實錄)처럼 데이터베이스에 남는 사극 컨셉 챗봇 프로젝트.
 
Spring Boot + Spring AI 실습 과정에서, Chat Memory / Advisor 구조를 익히기 위해 만든 미니 프로젝트.
 
## 주요 기능
 
### 1. 왕과의 대화 (`/api/wang-chat`)
- 사용자가 메시지를 보내면 AI가 **왕의 1인칭 어투**로 대답.
- 대화의 `conversationId`는 **왕의 이름**입니다. 왕별로 대화 이력이 독립적으로 관리.
- 사용자가 반말이나 무례한 표현을 쓰면, LLM을 호출하지 않고 **왕이 직접 처벌을 명령**. (유배, 파직, 의금부 압송 등 랜덤 대사)
- 이 처벌 대사를 포함한 모든 대화는 그대로 실록(DB)에 기록.
### 2. 실록 조회 (`/api/sillok`)
- 사용자가 질문을 입력하면, 저장된 모든 왕의 대화 기록(실록)을 근거로 AI(사관 페르소나)가 답변.
- 근거가 없는 내용은 추측하지 않고 "해당 사료를 찾을 수 없사옵니다"라고 답한다.
## 기술 스택
 
| 분류 | 내용 |
|---|---|
| Language | Java 21 |
| Framework | Spring Boot 4.1.0 |
| Build Tool | Gradle |
| AI | Spring AI 2.0.0 (Google GenAI / Gemini) |
| Database | H2 (파일 기반, 영구 저장) |
| Config | YAML |
 
## 📂 프로젝트 구조
 
```
com.study.sillok
├── advisor
│   └── KingGuardAdvisor        # 반말/무례 언사 감지 → 처벌 대사 반환
├── config
│   └── ChatMemoryConfig       # JDBC 기반 ChatMemory 빈 설정
├── controller
│   ├── WangChatController      # /api/wang-chat
│   └── SillokQueryController   # /api/sillok
└── service
    ├── KingChatService         # 왕 페르소나 대화 로직
    └── SillokQueryService      # 실록 조회/RAG 로직
```
 
## 실행 방법
 
### 1. 환경 변수 설정
Google GenAI API 키 필요.
 
```bash
export GOOGLE_API_KEY=your-api-key-here
```
 
### 2. 애플리케이션 실행
 
```bash
./gradlew bootRun
```
 
### 3. H2 콘솔 접속
저장된 대화(실록)를 직접 확인하고 싶다면:
 
```
http://localhost:8080/h2-console
```
 
- JDBC URL: `jdbc:h2:file:./data/sillok`
- Driver: `org.h2.Driver`

## API 사용 예시
 
### 왕과의 대화
```bash
curl "http://localhost:8080/api/wang-chat?king=세종&message=전하 맥북은 던지지 마시옵소서"
```
```
경은 어찌하여 과인이 맥북을 던질 것이라 지레짐작하고 이리 호들갑을 떠는 것인가.

과인이 비록 정무로 인해 심기가 불편할 때가 있으나, ...
```

무례한 언사를 시도하면:
```bash
curl "http://localhost:8080/api/wang-chat?king=단종&message=밥은먹고다니냐"
```
```
무엄하도다! 감히 일국의 군주에게 식사 여부를 묻는단 말이냐.
```
 
### 실록 조회
```bash
curl "http://localhost:8080/api/sillok?question=세종이 맥북 던진 사건"
```
```
세종대왕께서는맥북을던진적이없으시옵니다.실록에따르면,
세종께서는신하가맥북을던지지말아달라고간언하자, ....
```

![실록](![alt text](image.png))
 
## 데이터베이스 참고
 
대화 기록은 Spring AI가 자동 생성하는 `SPRING_AI_CHAT_MEMORY` 테이블에 저장된다. `conversation_id` 컬럼에 왕의 이름이 그대로 들어간다.
 
## 향후 개선 아이디어
 
- [ ] 왕 이름별로 `/api/sillok` 조회 범위를 좁힐 수 있는 파라미터 추가
- [ ] 데이터가 많아질 경우 VectorStore + RAG 방식으로 전환
- [ ] Thymeleaf 기반 대화형 UI 페이지 추가
- [ ] 반말/무례 언사 탐지 정교화 (현재는 정규식 기반)
- [ ] AI 왕 페르소나가 실제 역사적 사건을 참조할 수 있게 설정
