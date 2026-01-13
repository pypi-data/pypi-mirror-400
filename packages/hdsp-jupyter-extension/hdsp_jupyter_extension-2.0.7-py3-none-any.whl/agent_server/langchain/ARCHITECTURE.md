# LangChain Agent Architecture

## 목차
1. [개요](#개요)
2. [전체 구조](#전체-구조)
3. [디렉토리 구조](#디렉토리-구조)
4. [핵심 컴포넌트](#핵심-컴포넌트)
5. [데이터 흐름](#데이터-흐름)
6. [미들웨어 시스템](#미들웨어-시스템)
7. [도구 시스템](#도구-시스템)
8. [실행 흐름](#실행-흐름)

---

## 개요

이 시스템은 LangChain을 기반으로 Jupyter 노트북 환경에서 동작하는 데이터 분석 에이전트입니다. 주요 특징:

- **Human-in-the-Loop (HITL)**: 코드 실행 전 사용자 승인 필요
- **TodoList 기반 작업 관리**: 작업을 단계별로 추적
- **스트리밍 응답**: 실시간으로 에이전트 상태 전달
- **멀티 모델 지원**: Gemini, OpenAI, vLLM
- **커스텀 미들웨어**: 빈 응답 처리, continuation 프롬프트 주입 등

---

## 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    Jupyter Extension (Frontend)              │
│  - AgentPanel.tsx: UI 컴포넌트                               │
│  - ApiService.ts: API 통신                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/SSE
┌──────────────────────▼──────────────────────────────────────┐
│              Jupyter Extension (Backend)                     │
│  - handlers.py: HTTP 핸들러                                  │
│    - ChatStreamHandler: 에이전트 스트리밍                    │
│    - ExecuteCommandHandler: 쉘 명령 실행                     │
│    - CheckResourceHandler: 리소스 확인                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST
┌──────────────────────▼──────────────────────────────────────┐
│                Agent Server (FastAPI)                        │
│  - langchain_agent.py: 라우터                                │
│    - stream_agent(): 초기 요청 처리                          │
│    - resume_agent(): 인터럽트 재개                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              LangChain Agent (agent.py)                      │
│  - create_simple_chat_agent(): 에이전트 생성                 │
│  - Middleware 체인                                           │
│  - Tools 등록                                                │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
┌────────▼────────┐ ┌─▼──────────┐ ┌▼─────────────┐
│   Middleware    │ │   Tools    │ │ LLM Factory  │
│                 │ │            │ │              │
│ - Empty Response│ │ - Jupyter  │ │ - Gemini     │
│ - Continuation  │ │ - File I/O │ │ - OpenAI     │
│ - HITL          │ │ - Search   │ │ - vLLM       │
│ - TodoList      │ │ - Shell    │ │              │
└─────────────────┘ └────────────┘ └──────────────┘
```

---

## 디렉토리 구조

### `agent_server/langchain/`

```
langchain/
├── __init__.py                 # 모듈 초기화
├── agent.py                    # 에이전트 생성 및 설정
├── custom_middleware.py        # 커스텀 미들웨어 정의
├── hitl_config.py              # HITL 설정
├── llm_factory.py              # LLM 인스턴스 생성
├── logging_utils.py            # 로깅 유틸리티
├── prompts.py                  # 시스템 프롬프트 및 스키마
├── state.py                    # 상태 정의 (TypedDict, dataclass)
├── executors/
│   ├── __init__.py
│   └── notebook_searcher.py   # 노트북 검색 기능
└── tools/
    ├── __init__.py
    ├── file_tools.py           # 파일 읽기/쓰기/목록
    ├── jupyter_tools.py        # Jupyter 셀 실행, 마크다운, final_answer
    ├── resource_tools.py       # 리소스 확인 (파일 크기, 메모리)
    ├── search_tools.py         # 워크스페이스 검색, 노트북 검색
    └── shell_tools.py          # 쉘 명령 실행
```

### `agent_server/routers/`

```
routers/
└── langchain_agent.py          # FastAPI 라우터
    - stream_agent()            # POST /agent/langchain/stream
    - resume_agent()            # POST /agent/langchain/resume
    - search_workspace()        # POST /agent/search/workspace
    - clear_agent_cache()       # POST /agent/langchain/clear
```

### `extensions/jupyter/jupyter_ext/`

```
jupyter_ext/
└── handlers.py                 # Jupyter Extension 핸들러
    - ChatStreamHandler         # GET /hdsp-agent/chat/stream
    - ExecuteCommandHandler     # POST /hdsp-agent/execute/command
    - CheckResourceHandler      # POST /hdsp-agent/check-resource
    - WriteFileHandler          # POST /hdsp-agent/write-file
    - (기타 핸들러)
```

---

## 핵심 컴포넌트

### 1. Agent (`agent.py`)

#### `create_simple_chat_agent()`
에이전트 인스턴스를 생성하고 설정합니다.

**주요 작업**:
1. LLM 생성 (`llm_factory.create_llm()`)
2. Tools 등록 (`_get_all_tools()`)
3. Middleware 체인 구성
4. Checkpointer 설정 (InMemorySaver)
5. 시스템 프롬프트 설정 (Gemini-2.5-flash 전용 프롬프트 추가)

**Middleware 순서**:
```python
1. handle_empty_response        # 빈 응답 처리
2. limit_tool_calls             # 한 번에 1개 도구만 호출
3. inject_continuation          # non-HITL 도구 후 continuation 프롬프트
4. patch_tool_calls             # dangling tool call 수정
5. TodoListMiddleware           # 작업 목록 관리
6. HumanInTheLoopMiddleware     # 코드 실행 전 사용자 승인
7. ModelCallLimitMiddleware     # LLM 호출 횟수 제한 (30회)
8. ToolCallLimitMiddleware      # 특정 도구 호출 제한
9. SummarizationMiddleware      # 대화 요약
```

**Tools**:
```python
- jupyter_cell_tool            # Python 코드 실행
- markdown_tool                # 마크다운 셀 추가
- final_answer_tool            # 작업 완료 및 요약
- read_file_tool               # 파일 읽기
- write_file_tool              # 파일 쓰기
- list_files_tool              # 디렉토리 목록
- search_workspace_tool        # 워크스페이스 검색 (grep/rg)
- search_notebook_cells_tool   # 노트북 셀 검색
- execute_command_tool         # 쉘 명령 실행
- check_resource_tool          # 리소스 확인
```

---

### 2. Router (`langchain_agent.py`)

FastAPI 라우터로, 클라이언트 요청을 받아 에이전트를 실행합니다.

#### `stream_agent()` - POST `/agent/langchain/stream`
초기 요청을 처리하고 SSE 스트리밍으로 응답합니다.

**흐름**:
```
1. AgentRequest 파싱
2. 설정 준비 (LLM config, workspace root, thread_id)
3. 에이전트 생성 (create_simple_chat_agent)
4. Checkpointer 생성/조회 (InMemorySaver)
5. 스트리밍 시작 (agent.stream)
6. 이벤트 처리 루프:
   - todos: TodoList 업데이트
   - messages: AIMessage/ToolMessage 처리
   - interrupt: HITL 인터럽트 발생
7. SSE 이벤트 전송:
   - event: todos           # Todo 리스트 업데이트
   - event: token           # LLM 응답 토큰
   - event: debug           # 디버그 메시지
   - event: tool_call       # 도구 호출 요청
   - event: interrupt       # HITL 인터럽트
   - event: complete        # 완료
```

**주요 처리**:
- **ToolMessage (final_answer_tool)**: `final_answer` 추출, `summary` 필드에서 `next_items` JSON 추출 후 마크다운 코드 블록으로 변환
- **AIMessage**: tool_calls 확인, 빈 content는 필터링, 중복 제거
- **Interrupt**: HITL 도구 호출 시 스트리밍 일시 중지, 클라이언트로 interrupt 이벤트 전송

#### `resume_agent()` - POST `/agent/langchain/resume`
HITL 인터럽트 이후 사용자 결정(승인/거부)을 받아 에이전트를 재개합니다.

**흐름**:
```
1. ResumeRequest 파싱 (thread_id, decision, execution_result)
2. Checkpointer에서 기존 상태 조회
3. 인터럽트 메시지 찾기
4. 사용자 결정에 따라 업데이트:
   - approved: execution_result를 ToolMessage arguments에 주입
   - rejected: rejection_reason 추가
5. 에이전트 재개 (agent.stream)
6. SSE 이벤트 전송 (stream_agent와 동일)
```

---

### 3. Handlers (`handlers.py`)

Jupyter Extension의 백엔드 핸들러로, 클라이언트 요청을 Agent Server로 전달합니다.

#### `ChatStreamHandler` - GET `/hdsp-agent/chat/stream`
에이전트와의 대화를 스트리밍합니다.

**흐름**:
```
1. GET 파라미터 파싱 (message, sessionId, mode 등)
2. Agent Server로 POST 요청
   - URL: {AGENT_SERVER_URL}/agent/langchain/stream
   - Body: AgentRequest
3. SSE 스트리밍 응답 전달
4. event: tool_call 감지 시:
   - jupyter_cell_tool: 클라이언트에 전달 (HITL)
   - execute_command_tool: 서버에서 실행 후 결과 반환
   - check_resource_tool: 서버에서 실행 후 결과 반환
5. interrupt 이벤트 수신 시: 클라이언트로 전달, 대기
```

#### `ExecuteCommandHandler` - POST `/hdsp-agent/execute/command`
쉘 명령을 실행하고 결과를 반환합니다.

**흐름**:
```
1. POST body 파싱 (command, stdin, cwd, timeout)
2. subprocess로 명령 실행
3. stdout/stderr 수집
4. 결과 반환 (success, output, error)
```

#### `CheckResourceHandler` - POST `/hdsp-agent/check-resource`
파일 크기 및 DataFrame 메모리 사용량을 확인합니다.

**흐름**:
```
1. POST body 파싱 (files, dataframes)
2. 파일 크기 확인 (subprocess: du -sh)
3. DataFrame 메모리 확인 (jupyter_cell_tool 호출)
4. 결과 반환 (file_sizes, dataframe_memory)
```

---

## 데이터 흐름

### 초기 요청 흐름

```
[Client]
   │
   ├─ message: "타이타닉 데이터 분석해줘"
   │
   ▼
[Jupyter Extension: ChatStreamHandler]
   │
   ├─ POST /agent/langchain/stream
   │  {
   │    request: "타이타닉 데이터 분석해줘",
   │    threadId: "uuid",
   │    workspaceRoot: "/path/to/workspace",
   │    llmConfig: { provider: "gemini", ... }
   │  }
   │
   ▼
[Agent Server: stream_agent()]
   │
   ├─ create_simple_chat_agent(llm_config, workspace_root)
   │  │
   │  ├─ create_llm() → ChatGoogleGenerativeAI
   │  ├─ _get_all_tools() → [jupyter_cell_tool, ...]
   │  ├─ middleware 체인 구성
   │  └─ create_agent(model, tools, middleware, checkpointer)
   │
   ├─ agent.stream(input, config)
   │  │
   │  ├─ [TodoListMiddleware] → write_todos 호출
   │  │  → todos: [
   │  │      {content: "데이터 로드", status: "pending"},
   │  │      {content: "EDA", status: "pending"},
   │  │      {content: "다음 단계 제시", status: "pending"}
   │  │    ]
   │  │
   │  ├─ [LLM] → AIMessage with tool_calls
   │  │  → tool_calls: [{
   │  │      name: "check_resource_tool",
   │  │      args: {files: ["titanic.csv"]}
   │  │    }]
   │  │
   │  ├─ [HumanInTheLoopMiddleware] → interrupt (non-HITL이면 통과)
   │  │
   │  ├─ [Tool Execution] → check_resource_tool()
   │  │  → {status: "pending_execution", ...}
   │  │
   │  └─ [Stream] → SSE 이벤트 전송
   │     - event: todos
   │     - event: debug (🔧 Tool 실행: check_resource_tool)
   │     - event: tool_call
   │
   ▼
[Jupyter Extension: ChatStreamHandler]
   │
   ├─ tool_call 수신 (check_resource_tool)
   │  → CheckResourceHandler 호출
   │  → execution_result 획득
   │
   ├─ POST /agent/langchain/resume
   │  {
   │    threadId: "uuid",
   │    decision: "approved",
   │    execution_result: {...}
   │  }
   │
   ▼
[Agent Server: resume_agent()]
   │
   ├─ 인터럽트 메시지 업데이트 (execution_result 주입)
   │
   ├─ agent.stream(None, config) → 재개
   │  │
   │  ├─ [LLM] → ToolMessage 처리
   │  │  → "파일 크기: 60KB"
   │  │
   │  ├─ [inject_continuation] → continuation 프롬프트 주입
   │  │  → "[SYSTEM] Tool 'check_resource_tool' completed. Continue..."
   │  │
   │  ├─ [LLM] → AIMessage with tool_calls
   │  │  → tool_calls: [{
   │  │      name: "jupyter_cell_tool",
   │  │      args: {code: "import pandas as pd\ndf = pd.read_csv('titanic.csv')"}
   │  │    }]
   │  │
   │  ├─ [HumanInTheLoopMiddleware] → interrupt (HITL)
   │  │
   │  └─ [Stream] → SSE 이벤트 전송
   │     - event: interrupt
   │
   ▼
[Jupyter Extension: ChatStreamHandler]
   │
   ├─ interrupt 수신 (jupyter_cell_tool)
   │  → 클라이언트로 전달 (UI에서 사용자 승인 대기)
   │
   ├─ 사용자 승인 후
   │  → Jupyter 커널에서 코드 실행
   │  → execution_result 획득
   │
   ├─ POST /agent/langchain/resume
   │
   ▼
... (반복)
```

### final_answer_tool 처리 흐름

```
[LLM]
   │
   ├─ AIMessage with tool_calls
   │  → tool_calls: [{
   │      name: "final_answer_tool",
   │      args: {
   │        answer: "분석 완료",
   │        summary: '{"next_items": [...]}'  // JSON 문자열
   │      }
   │    }]
   │
   ▼
[Tool Execution]
   │
   ├─ final_answer_tool(answer, summary)
   │  → {
   │      tool: "final_answer",
   │      parameters: {answer: "...", summary: "..."},
   │      status: "complete"
   │    }
   │
   ▼
[Router: stream_agent()]
   │
   ├─ ToolMessage 수신
   │  │
   │  ├─ tool_result.get("answer")
   │  ├─ summary = tool_result.get("summary")
   │  │
   │  ├─ summary가 JSON 문자열이면:
   │  │  │
   │  │  ├─ summary_json = json.loads(summary)
   │  │  ├─ if "next_items" in summary_json:
   │  │  │    next_items_block = f"\n\n```json\n{json.dumps(summary_json)}\n```"
   │  │  │    final_answer = answer + next_items_block
   │  │  │
   │  │  └─ yield {"event": "token", "data": {"content": final_answer}}
   │  │
   │  ├─ yield {"event": "todos", "data": {"todos": _complete_todos(todos)}}
   │  ├─ yield {"event": "debug_clear"}
   │  └─ yield {"event": "complete"}
   │
   └─ return (스트림 종료)
```

---

## 미들웨어 시스템

### 1. `handle_empty_response`
빈 응답 또는 text-only 응답을 처리합니다.

**동작**:
1. LLM 응답 확인:
   - `tool_calls` 있으면 → 정상 응답, 통과
   - `content`에 JSON이 있으면 → 파싱하여 tool_call 생성
2. 마지막 메시지가 `final_answer_tool` 결과이면 → 그대로 반환 (에이전트 자연 종료)
3. 빈 응답이면 → JSON 스키마 프롬프트로 재시도 (최대 2회)
4. 재시도 실패 시 → synthetic `final_answer_tool` 생성

**Gemini 2.5 Flash 대응**:
- content가 리스트인 경우 처리 (`parse_json_tool_call`)
- multimodal 응답 지원

### 2. `inject_continuation`
non-HITL 도구 실행 후 continuation 프롬프트를 주입합니다.

**대상 도구**:
```python
NON_HITL_TOOLS = {
    "markdown_tool",
    "read_file_tool",
    "list_files_tool",
    "search_workspace_tool",
    "search_notebook_cells_tool",
    "write_todos",
}
```

**동작**:
1. 마지막 메시지가 non-HITL 도구의 ToolMessage인지 확인
2. todos 상태 확인:
   - pending/in_progress 있으면 → "Continue with pending tasks: ..."
   - 모두 완료이면 → "Call final_answer_tool with a summary NOW."
3. HumanMessage로 프롬프트 주입

### 3. `limit_tool_calls`
한 번에 1개 도구만 호출하도록 제한합니다.

**동작**:
1. AIMessage의 `tool_calls` 개수 확인
2. 2개 이상이면 → 첫 번째만 유지, 나머지 제거
3. 로그 출력

### 4. `patch_tool_calls`
Dangling tool call (실행되지 않은 도구 호출)을 수정합니다.

**동작**:
1. 마지막 메시지가 AIMessage with tool_calls인지 확인
2. 그 다음 메시지가 ToolMessage가 아니면 → dangling
3. synthetic ToolMessage 생성하여 주입

### 5. `TodoListMiddleware` (LangChain 내장)
작업 목록을 관리합니다.

**동작**:
1. `write_todos` 도구 등록
2. LLM이 `write_todos` 호출하면 → state에 todos 저장
3. 시스템 프롬프트에 todo 관리 지침 추가

### 6. `HumanInTheLoopMiddleware` (LangChain 내장)
사용자 승인이 필요한 도구 실행 전 인터럽트를 발생시킵니다.

**대상 도구**:
```python
HITL_TOOLS = {
    "jupyter_cell_tool",
    "execute_command_tool",
    "write_file_tool",
}
```

**동작**:
1. AIMessage with tool_calls 감지
2. tool_calls 중 HITL 도구가 있으면 → interrupt 발생
3. 에이전트 일시 중지, 클라이언트로 제어 반환

### 7. `ModelCallLimitMiddleware` (LangChain 내장)
LLM 호출 횟수를 제한합니다.

**설정**:
- `run_limit=30`: 최대 30회 LLM 호출
- `exit_behavior="end"`: 제한 도달 시 에이전트 종료

### 8. `ToolCallLimitMiddleware` (LangChain 내장)
특정 도구의 호출 횟수를 제한합니다.

**설정**:
```python
- write_todos: run_limit=5, exit_behavior="continue"
- list_files_tool: run_limit=5, exit_behavior="continue"
```

### 9. `SummarizationMiddleware` (LangChain 내장)
대화가 길어지면 요약합니다.

**설정**:
- `trigger`: tokens=8000 또는 messages=30
- `keep`: 최근 10개 메시지 유지
- `summary_prefix`: "[이전 대화 요약]\n"

---

## 도구 시스템

### Jupyter Tools (`jupyter_tools.py`)

#### `jupyter_cell_tool`
Python 코드를 Jupyter 셀에서 실행합니다.

**파라미터**:
- `code`: Python 코드
- `description`: 코드 설명 (선택)
- `execution_result`: 클라이언트에서 실행한 결과 (HITL 후)

**반환**:
```python
{
    "tool": "jupyter_cell",
    "parameters": {"code": "...", "description": "..."},
    "status": "pending_execution",  # 또는 "complete"
    "message": "Code cell queued for execution...",
    "execution_result": {...}  # HITL 후
}
```

**특징**:
- 마크다운 코드 블록 래퍼 제거
- HITL 대상 (사용자 승인 필요)

#### `markdown_tool`
마크다운 셀을 추가합니다.

**파라미터**:
- `content`: 마크다운 내용

**반환**:
```python
{
    "tool": "markdown",
    "parameters": {"content": "..."},
    "status": "completed",
    "message": "Markdown cell added successfully."
}
```

**특징**:
- non-HITL (즉시 실행)

#### `final_answer_tool`
작업을 완료하고 요약을 제공합니다.

**파라미터**:
- `answer`: 최종 답변
- `summary`: 요약 (선택, `next_items` JSON 포함 가능)

**반환**:
```python
{
    "tool": "final_answer",
    "parameters": {"answer": "...", "summary": "..."},
    "status": "complete",
    "message": "Task completed successfully"
}
```

**특징**:
- 에이전트 종료 신호
- `summary` 필드에 `next_items` JSON 포함 가능 (Gemini)

---

### File Tools (`file_tools.py`)

#### `read_file_tool`
파일을 읽습니다.

**파라미터**:
- `path`: 파일 경로

**반환**:
```python
{
    "tool": "read_file",
    "parameters": {"path": "..."},
    "status": "completed",
    "content": "파일 내용..."
}
```

**특징**:
- workspace_root 기준 상대 경로
- 경로 벗어나기 방지 (`_validate_path`)

#### `write_file_tool`
파일을 씁니다.

**파라미터**:
- `path`: 파일 경로
- `content`: 내용
- `overwrite`: 덮어쓰기 여부 (기본 False)

**반환**:
```python
{
    "tool": "write_file",
    "parameters": {"path": "...", "content": "...", "overwrite": False},
    "status": "pending_execution",  # HITL
    "message": "File write queued..."
}
```

**특징**:
- HITL 대상 (사용자 승인 필요)

#### `list_files_tool`
디렉토리 목록을 가져옵니다.

**파라미터**:
- `path`: 디렉토리 경로 (기본 ".")
- `recursive`: 재귀 탐색 여부 (기본 False)

**반환**:
```python
{
    "tool": "list_files",
    "parameters": {"path": ".", "recursive": False},
    "status": "completed",
    "files": ["file1.py", "file2.csv", ...]
}
```

---

### Search Tools (`search_tools.py`)

#### `search_workspace_tool`
워크스페이스에서 패턴을 검색합니다 (grep/ripgrep).

**파라미터**:
- `pattern`: 정규식 패턴
- `file_types`: 파일 타입 필터 (예: ["py", "md"])
- `path`: 검색 경로 (기본 ".")

**반환**:
```python
{
    "tool": "search_workspace",
    "parameters": {"pattern": "...", "file_types": ["py"], "path": "."},
    "status": "completed",
    "results": [
        {"file": "file1.py", "line_number": 10, "line": "..."},
        ...
    ],
    "command": "rg ... (또는 grep ...)"
}
```

**특징**:
- ripgrep 우선 사용 (속도)
- 없으면 grep 사용

#### `search_notebook_cells_tool`
Jupyter 노트북 셀에서 패턴을 검색합니다.

**파라미터**:
- `pattern`: 정규식 패턴
- `notebook_path`: 노트북 경로 (선택, 없으면 전체)

**반환**:
```python
{
    "tool": "search_notebook_cells",
    "parameters": {"pattern": "...", "notebook_path": "..."},
    "status": "completed",
    "results": [
        {
            "notebook": "analysis.ipynb",
            "cell_index": 3,
            "cell_type": "code",
            "source": "...",
            "matches": [...]
        },
        ...
    ]
}
```

---

### Shell Tools (`shell_tools.py`)

#### `execute_command_tool`
쉘 명령을 실행합니다.

**파라미터**:
- `command`: 쉘 명령
- `stdin`: 인터랙티브 프롬프트 입력 (기본 "y\n")
- `timeout`: 타임아웃 (밀리초, 기본 600000)
- `execution_result`: 클라이언트에서 실행한 결과 (HITL 후)

**반환**:
```python
{
    "tool": "execute_command_tool",
    "parameters": {"command": "...", "stdin": "y\n", "timeout": 600000},
    "status": "pending_execution",  # 또는 "complete"
    "message": "Shell command queued...",
    "execution_result": {...}  # HITL 후
}
```

**특징**:
- HITL 대상 (사용자 승인 필요)
- 장시간 실행 명령 금지 (프롬프트에 명시)

---

### Resource Tools (`resource_tools.py`)

#### `check_resource_tool`
파일 크기 및 DataFrame 메모리 사용량을 확인합니다.

**파라미터**:
- `files`: 파일 경로 리스트
- `dataframes`: DataFrame 변수명 리스트

**반환**:
```python
{
    "tool": "check_resource_tool",
    "parameters": {"files": ["titanic.csv"], "dataframes": ["df"]},
    "status": "pending_execution",  # 클라이언트에서 실행
    "message": "Resource check queued...",
    "execution_result": {
        "file_sizes": {"titanic.csv": "60KB"},
        "dataframe_memory": {"df": "2.5MB"}
    }
}
```

**특징**:
- 클라이언트에서 실행 (Jupyter Extension의 CheckResourceHandler)
- 대용량 파일 로드 전 확인

---

## 실행 흐름

### 1. 초기화 흐름

```python
# 1. 라우터에서 에이전트 생성
agent = create_simple_chat_agent(
    llm_config=llm_config,
    workspace_root=workspace_root,
    enable_hitl=True,
    enable_todo_list=True,
    checkpointer=checkpointer,
    system_prompt_override=None
)

# 2. create_simple_chat_agent 내부
llm = create_llm(llm_config)  # Gemini/OpenAI/vLLM
tools = _get_all_tools()

# 3. Middleware 체인 구성
middleware = [
    handle_empty_response,
    limit_tool_calls,
    inject_continuation,
    patch_tool_calls,
    TodoListMiddleware(...),
    HumanInTheLoopMiddleware(...),
    ModelCallLimitMiddleware(run_limit=30),
    ToolCallLimitMiddleware(...),
    SummarizationMiddleware(...)
]

# 4. 시스템 프롬프트 설정
system_prompt = DEFAULT_SYSTEM_PROMPT
if "gemini-2.5-flash" in llm_config.get("gemini", {}).get("model", ""):
    system_prompt += GEMINI_CONTENT_PROMPT

# 5. 에이전트 생성
agent = create_agent(
    model=llm,
    tools=tools,
    middleware=middleware,
    checkpointer=checkpointer,
    system_prompt=system_prompt
)
```

### 2. 스트리밍 흐름

```python
# 1. 라우터에서 스트리밍 시작
async for step in agent.stream(agent_input, config):
    # 2. step은 딕셔너리 {"messages": [...], "todos": [...]}

    # 3. todos 처리
    if "todos" in step:
        todos = step["todos"]
        yield {"event": "todos", "data": json.dumps({"todos": todos})}

    # 4. messages 처리
    if "messages" in step:
        last_message = step["messages"][-1]

        # 5. ToolMessage 처리
        if isinstance(last_message, ToolMessage):
            tool_name = last_message.name

            if tool_name == "final_answer_tool":
                # 6. final_answer 추출
                tool_result = json.loads(last_message.content)
                final_answer = tool_result.get("answer")
                summary = tool_result.get("summary")

                # 7. summary에서 next_items 추출
                if summary:
                    summary_json = json.loads(summary)
                    if "next_items" in summary_json:
                        next_items_block = f"\n\n```json\n{json.dumps(summary_json)}\n```"
                        final_answer += next_items_block

                # 8. 응답 전송
                yield {"event": "token", "data": {"content": final_answer}}
                yield {"event": "complete", "data": {"success": True}}
                return

        # 9. AIMessage 처리
        elif isinstance(last_message, AIMessage):
            # 10. tool_calls 확인
            if last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    # 11. 디버그 이벤트
                    yield {"event": "debug", "data": {"status": f"🔧 Tool 실행: {tool_call['name']}"}}

                    # 12. HITL 도구이면 tool_call 이벤트
                    if tool_call["name"] in HITL_TOOLS:
                        yield {"event": "tool_call", "data": tool_call}

            # 13. content 전송
            if last_message.content:
                yield {"event": "token", "data": {"content": last_message.content}}
```

### 3. HITL 인터럽트 흐름

```python
# 1. HumanInTheLoopMiddleware에서 인터럽트 발생
# LangGraph는 interrupt를 state에 저장하고 스트리밍 종료

# 2. 라우터에서 인터럽트 감지
if "__interrupt__" in step:
    interrupt_data = step["__interrupt__"]
    yield {"event": "interrupt", "data": interrupt_data}
    return  # 스트리밍 종료

# 3. 클라이언트에서 사용자 결정 대기
# - jupyter_cell_tool: UI에서 승인/거부
# - execute_command_tool/check_resource_tool: 서버에서 실행

# 4. 클라이언트가 resume_agent() 호출
POST /agent/langchain/resume
{
    "threadId": "uuid",
    "decision": "approved",
    "execution_result": {...}
}

# 5. resume_agent에서 인터럽트 메시지 업데이트
interrupt_message.args["execution_result"] = execution_result

# 6. 에이전트 재개
agent.stream(None, config)  # None은 새 입력 없음을 의미
```

### 4. 에이전트 종료 흐름

```python
# 1. LLM이 final_answer_tool 호출
AIMessage(tool_calls=[{
    "name": "final_answer_tool",
    "args": {"answer": "...", "summary": "..."}
}])

# 2. final_answer_tool 실행
result = {
    "tool": "final_answer",
    "parameters": {...},
    "status": "complete"
}

# 3. ToolMessage 생성
ToolMessage(name="final_answer_tool", content=json.dumps(result))

# 4. LangGraph가 ToolMessage를 LLM에 전달
# LLM이 빈 응답 반환 (도구 호출 없음)

# 5. handle_empty_response 미들웨어
# 마지막 메시지가 final_answer_tool이면 → 그대로 반환
# synthetic answer 생성하지 않음

# 6. LangGraph가 도구 호출 없는 응답 받고 종료
# agent.stream() 루프 종료

# 7. 라우터에서 complete 이벤트 전송
yield {"event": "complete", "data": {"success": True}}
return
```

---

## 주요 설계 결정 사항

### 1. Gemini 2.5 Flash 대응
- **문제**: content 빈값, multimodal 응답 (리스트)
- **해결**:
  - 시스템 프롬프트에 content 포함 지시 추가
  - `parse_json_tool_call`에서 리스트 처리

### 2. final_answer_tool 반복 호출 방지
- **문제**: `final_answer_tool` 호출 후에도 에이전트 계속 실행
- **해결**:
  - `ToolCallLimitMiddleware` 제거 (스레드 전체 카운트 문제)
  - `handle_empty_response`에서 `final_answer_tool` 후 synthetic answer 생성 안함
  - 에이전트가 자연스럽게 종료

### 3. next_items UI 누락 문제
- **문제**: Gemini가 `summary` 필드에 JSON 문자열로 `next_items` 전달
- **해결**:
  - 라우터에서 `summary` 필드 파싱
  - `next_items` JSON을 마크다운 코드 블록으로 변환
  - UI의 `extractNextItemsBlock` 함수가 파싱

### 4. HITL 도구 vs non-HITL 도구
- **HITL**: 사용자 승인 필요
  - `jupyter_cell_tool`, `execute_command_tool`, `write_file_tool`
- **non-HITL**: 즉시 실행
  - `markdown_tool`, `read_file_tool`, `list_files_tool`, `search_*_tool`
- **클라이언트 실행**: 서버에서 실행하지 않음
  - `check_resource_tool`: CheckResourceHandler에서 처리

### 5. Checkpointer (InMemorySaver)
- 스레드별로 대화 상태 저장
- HITL 인터럽트 재개에 필수
- 메모리 기반 (서버 재시작 시 초기화)

### 6. SSE 스트리밍 이벤트
- `todos`: TodoList 업데이트
- `token`: LLM 응답 토큰
- `debug`: 디버그 메시지 (도구 실행 상태)
- `tool_call`: HITL 도구 호출 요청
- `interrupt`: HITL 인터럽트 발생
- `complete`: 완료
- `debug_clear`: 디버그 메시지 클리어

---

## 디버깅 가이드

### 로그 확인

#### Agent Server
```bash
# 전체 로그
tail -f agent-server.log

# LLM 호출 로그
grep "AGENT -> LLM PROMPT" agent-server.log

# 미들웨어 로그
grep "Middleware:" agent-server.log

# 도구 실행 로그
grep "Tool 실행:" agent-server.log
```

#### Jupyter Extension
```bash
# Jupyter 서버 로그
jupyter lab --debug
```

### 주요 로그 패턴

#### 1. LLM 프롬프트
```
================================================================================================
AGENT -> LLM PROMPT SYSTEM (1521 chars)
================================================================================================
You are an expert Python data scientist...

================================================================================================
AGENT -> LLM PROMPT USER MESSAGES (batch=0)
================================================================================================
[0] HumanMessage
  "타이타닉 데이터 분석해줘"
```

#### 2. LLM 응답
```
================================================================================================
AGENT <- LLM RESPONSE
================================================================================================
AIMessage
{
  "content": "데이터를 로드하겠습니다.",
  "tool_calls": [
    {
      "name": "jupyter_cell_tool",
      "args": {"code": "import pandas as pd\ndf = pd.read_csv('titanic.csv')"}
    }
  ]
}
```

#### 3. 미들웨어 실행
```
Middleware: handle_empty_response [START]
handle_empty_response: attempt=1, type=AIMessage, content=True, tool_calls=True
Middleware: handle_empty_response [FINISH]

Middleware: inject_continuation_after_non_hitl_tool [START]
Injecting continuation prompt after non-HITL tool: write_todos
Middleware: inject_continuation_after_non_hitl_tool [FINISH]
```

#### 4. 도구 호출
```
SSE: Emitting debug event for tool: jupyter_cell_tool
🔧 Tool 실행: jupyter_cell_tool
```

#### 5. HITL 인터럽트
```
SimpleAgent interrupt detected with value: {...}
SSE: Sending interrupt event
```

### 트러블슈팅

#### 문제: 에이전트가 빈 응답만 반환
- **원인**: Gemini 2.5 Flash의 빈 content
- **확인**: `handle_empty_response` 로그에서 `content=False, tool_calls=False`
- **해결**: 시스템 프롬프트에 content 포함 지시 추가됨

#### 문제: final_answer_tool이 반복 호출
- **원인**: `handle_empty_response`가 synthetic answer 생성
- **확인**: 로그에서 `"Synthesizing final_answer response."`
- **해결**: `final_answer_tool` 후 synthetic answer 생성 안하도록 수정됨

#### 문제: next_items UI가 표시되지 않음
- **원인**: Gemini가 `summary` 필드에 JSON 문자열로 전달
- **확인**: ToolMessage content에서 `"summary": "{\"next_items\": [...]}"` 확인
- **해결**: 라우터에서 `summary` 파싱 로직 추가됨

#### 문제: HITL 인터럽트 후 재개되지 않음
- **원인**: Checkpointer에 상태 없음
- **확인**: `resume_agent`에서 "No existing state for thread" 로그
- **해결**: `stream_agent`에서 Checkpointer 생성 확인

---

## 확장 가이드

### 새 도구 추가

1. `tools/` 디렉토리에 파일 생성 (예: `custom_tools.py`)
2. `@tool` 데코레이터로 함수 정의
3. `tools/__init__.py`에서 export
4. `agent.py`의 `_get_all_tools()`에 추가

```python
# tools/custom_tools.py
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param: str = Field(description="Parameter description")

@tool(args_schema=MyToolInput)
def my_tool(param: str) -> Dict[str, Any]:
    """Tool description for LLM."""
    return {
        "tool": "my_tool",
        "parameters": {"param": param},
        "status": "completed",
        "result": "..."
    }

# tools/__init__.py
from .custom_tools import my_tool

# agent.py
def _get_all_tools():
    return [
        jupyter_cell_tool,
        markdown_tool,
        final_answer_tool,
        my_tool,  # 추가
        ...
    ]
```

### 새 미들웨어 추가

```python
# custom_middleware.py
def create_my_middleware(wrap_model_call):
    @wrap_model_call
    @_with_middleware_logging("my_middleware")
    def my_middleware(request, handler):
        # 전처리
        logger.info("Before LLM call")

        # LLM 호출
        response = handler(request)

        # 후처리
        logger.info("After LLM call")

        return response

    return my_middleware

# agent.py
def create_simple_chat_agent(...):
    ...
    my_middleware = create_my_middleware(wrap_model_call)
    middleware.append(my_middleware)
    ...
```

### 새 LLM Provider 추가

```python
# llm_factory.py
def _create_custom_llm(llm_config: Dict[str, Any], callbacks):
    from custom_llm_package import CustomLLM

    custom_config = llm_config.get("custom", {})
    api_key = custom_config.get("apiKey")
    model = custom_config.get("model", "default-model")

    return CustomLLM(
        model=model,
        api_key=api_key,
        temperature=0.0,
        callbacks=callbacks
    )

def create_llm(llm_config: Dict[str, Any]):
    provider = llm_config.get("provider", "gemini")

    if provider == "custom":
        return _create_custom_llm(llm_config, callbacks)
    ...
```

---

## 참고 자료

- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Agent Middleware](https://python.langchain.com/docs/modules/agents/middleware/)
- [FastAPI SSE](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Jupyter Server Extension](https://jupyter-server.readthedocs.io/en/latest/developers/extensions.html)
