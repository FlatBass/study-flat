# Daiso-File-mcp

Spring AI 기반 MCP(Model Context Protocol) Tool Calling 실습 프로젝트.
Gemini 모델(`gemini-3.1-flash-lite`)이 로컬 **파일시스템 MCP 서버**와 원격 **다이소 MCP 서버**의 도구를 호출해, 상품/재고를 검색하고 그 결과를 로컬 파일로 저장하는 흐름을 실습.

---

## 1. 프로젝트 목표

- Spring AI의 `ChatClient` + MCP 통합을 이용해 LLM이 **외부 도구(Tool)** 를 스스로 선택·호출하도록 구성.
- 서로 다른 전송 방식(stdio / streamable-http)의 MCP 서버를 **동시에** 연결.
- 여러 MCP 서버의 도구를 하나의 대화 흐름 안에서 조합.
  (예: 다이소 재고 검색 → 결과 정리 → 파일로 저장, 두 서버의 도구를 함께 사용)

## 2. 기술 스택

| 구분 | 내용 |
|---|---|
| Language / Build | Java, Gradle |
| Framework | Spring Boot 4.1.0 |
| AI | Spring AI 2.0.0, Google GenAI (Gemini) |
| Protocol | MCP (Model Context Protocol) — MCP Java SDK 1.0.x |

## 3. 연결된 MCP 서버

| 서버 | 전송 방식 | 역할 | 실행 위치 |
|---|---|---|---|
| `filesystem` | stdio | 로컬 디렉토리(`mcp-sandbox`)에 파일 읽기/쓰기 | 내 PC (하위 프로세스로 실행) |
| `daiso` | streamable-http | 다이소 상품 검색, 매장 조회, 재고 확인 등 | 원격 서버 (`https://mcp.aka.page`) |

## 4. 프로젝트 구조

```
src/main/java/com/study/day05_tool_mcp/
├── controller/
│   └── AiController.java       # REST 엔드포인트
├── service/
│   └── McpChatService.java     # ChatClient + 도구 조합 로직
└── mcp/
    └── McpToolCatalog.java     # 등록된 MCP 도구를 용도별로 분류/제공
```

- `McpToolCatalog` : Spring AI가 자동 구성한 `ToolCallbackProvider` 빈 하나로 filesystem/daiso 두 서버의 도구를 모두 받아온 뒤, 도구 이름 기준으로 **filesystem 전용 / daiso 전용 / 전체**로 나누어 제공.
- `McpChatService` : 상황에 맞는 도구 조합을 `ChatClient`에 넘겨 LLM이 호출.
- `AiController` : 실습용 REST API를 노출.

## 5. API 엔드포인트

| Method | URL | 설명 |
|---|---|---|
| GET | `/api/mcp?question=` | filesystem 도구만 사용 (파일 읽기/쓰기/탐색) |
| GET | `/api/daiso?question=` | daiso 도구만 사용 (상품/매장/재고 검색) |
| GET | `/api/daiso-file?question=` | daiso로 검색 + filesystem으로 결과를 파일 저장 (두 서버 도구 조합) |

### 사용 예시

```
GET /api/daiso?question=강남역 근처 다이소 매장 찾아줘

GET /api/daiso-file?question=수납박스 재고를 검색해서 json 파일로 저장해줘
```

## 6. 실행 방법

1. 환경 변수 `GOOGLE_API_KEY` 설정 (Gemini API 키)
2. `${user.dir}/mcp-sandbox` 디렉토리 생성 (filesystem MCP 서버가 접근할 루트)
3. Node.js / npx 설치 확인 (filesystem MCP 서버가 `npx`로 실행되므로 필요)
4. `./gradlew bootRun`

## 7. 트러블슈팅 메모

- Windows에서는 `command: npx.cmd`처럼 확장자를 명시해야 정상 실행.

---

## 8. `stdio` vs `streamable-http` — 차이

`application.yaml`에 있는 아래 두 설정은 **MCP 서버와 통신하는 방식(transport)** 자체가 다르다. 도구를 쓰는 입장(ChatClient, McpToolCatalog)에서는 차이가 안 보이지만, 내부적으로는 완전히 다른 연결 구조.

```yaml
ai:
  mcp:
    client:
      streamable-http:
        connections:
          daiso:
            url: https://mcp.aka.page
            endpoint: /mcp
      stdio:
        connections:
          filesystem:
            command: npx.cmd
            args:
              - "-y"
              - "@modelcontextprotocol/server-filesystem"
              - "${user.dir}/mcp-sandbox"
```

### stdio (Standard Input/Output)

- **연결 대상**: 내 컴퓨터에서 실행되는 **로컬 프로세스**
- **동작 방식**: Spring Boot 애플리케이션이 `command` + `args`로 지정한 프로그램을 **하위 프로세스로 직접 실행**하고, 그 프로세스의 표준 입력(stdin)/표준 출력(stdout)으로 JSON-RPC 메시지를 주고받는다.
- **예시**: `filesystem` 커넥션 — `npx.cmd -y @modelcontextprotocol/server-filesystem <경로>`를 자식 프로세스로 띄우고, 그 프로세스와 파이프로 통신
- **특징**
  - 네트워크 없이 동작 (로컬 자원 접근에 적합 — 파일시스템, 로컬 DB 등)
  - 앱이 시작될 때마다 서버 프로세스도 같이 뜨고, 앱이 죽으면 같이 종료됨
  - 외부에 노출되지 않으므로 별도 인증이 필요 없는 경우가 많음
  - 단점: 프로세스 기동 비용(특히 `npx`처럼 매번 패키지 확인/다운로드가 걸리는 경우) 때문에 초기 연결이 느려질 수 있음

### streamable-http

- **연결 대상**: 이미 어딘가에서 **독립적으로 실행 중인 원격(또는 별도) 서버**
- **동작 방식**: 앱이 프로세스를 띄우지 않고, 지정한 `url`(+ `endpoint`)로 **HTTP POST/GET 요청**을 보내 JSON-RPC 메시지를 주고받는다. 필요하면 SSE(Server-Sent Events)로 여러 응답을 스트리밍 받을 수 있다.
- **예시**: `daiso` 커넥션 — `https://mcp.aka.page/mcp`로 HTTP 요청을 보내 다이소 도구 목록을 받아오고 호출
- **특징**
  - 서버가 내 프로세스와 무관하게 어딘가에(클라우드, 다른 팀 서버 등) 떠 있어야 함
  - 여러 클라이언트가 동시에 접속 가능 (다중 사용자/다중 인스턴스에 적합)
  - 인증이 필요한 경우 헤더/토큰을 붙여야 함 (이번 다이소 서버는 별도 인증 없이 공개 사용 가능)
  - MCP 스펙(2025-03-26+)에서 기존 SSE 전송을 대체하는 최신 방식으로 권장됨

### 요약 비교

| 구분 | stdio | streamable-http |
|---|---|---|
| 서버 위치 | 내 PC (자식 프로세스) | 원격 / 별도 프로세스 |
| 통신 채널 | stdin/stdout 파이프 | HTTP(POST/GET), 필요시 SSE |
| 실행 주체 | 내 앱이 직접 기동 | 이미 떠 있는 서버에 접속만 함 |
| 네트워크 필요 여부 | 불필요 | 필요 |
| 적합한 대상 | 로컬 파일, 로컬 DB 등 내 컴퓨터 자원 | 외부 API를 감싼 공용/원격 서비스 |
| 이 프로젝트의 예 | `filesystem` (파일 읽기/쓰기) | `daiso` (다이소 상품/매장 API) |

즉, 이 프로젝트는 "내 컴퓨터 자원(파일)에는 stdio로, 외부 공개 서비스(다이소)에는 streamable-http로" 붙는 전형적인 하이브리드 구성이고, `McpToolCatalog`가 두 서버의 도구를 한데 모아 LLM에게 **하나의 도구 세트**처럼 제공하기 때문에 모델 입장에서는 어느 쪽이 stdio이고 어느 쪽이 http인지 신경 쓸 필요가 없다.