# n8n 운용 가이드

> AIHub 사이트에서 n8n 워크플로우를 운용하기 위한 실무 참조 문서

---

## 1. 환경 개요

### n8n 서버
| 항목 | 값 |
|------|-----|
| URL | http://localhost:5678 |
| 포트 | 5678 |
| 실행 방식 | 로컬 서버 |

### MCP 설정
**파일 위치**: `C:\Users\PC\.gemini\antigravity\mcp_config.json`

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "http://localhost:5678",
        "N8N_BASE_URL": "http://localhost:5678",
        "N8N_API_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTg0OWNkYi0xZGE1LTQ5NjMtYjM3NS0zZGYwZGFiMzg4ZDciLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5MzYwMzc4LCJleHAiOjE3NzE5MDkyMDB9.4QxNFWrnjpyuHXQFtjQwBgXpfo4JUZMBFVp2HJ22cWg"
      }
    }
  }
}
```

### Supabase 연결 정보
| 항목 | 값 |
|------|-----|
| 프로젝트 URL | https://jogjurkmqfqbwfbhbvwl.supabase.co |
| API Key (Service Role) | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpvZ2p1cmttcWZxYndmYmhidndsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjUzOTQ0OSwiZXhwIjoyMDcyMTE1NDQ5fQ.CLUItDgH2iafi8pT9fW5hP3oC3_UN8Lg1IgaW9-cJE4` |

---

## 2. 설치된 스킬 (7개)

**위치**: `C:\Users\PC\.gemini\antigravity\skills`

| 스킬 | 용도 | 우선순위 |
|------|------|---------|
| **n8n-mcp-tools-expert** | MCP 도구 사용법 | 최우선 |
| **n8n-expression-syntax** | `{{}}` 표현식 문법 | 높음 |
| **n8n-workflow-patterns** | 워크플로우 아키텍처 패턴 | 높음 |
| **n8n-validation-expert** | 검증 및 디버깅 | 중간 |
| **n8n-node-configuration** | 노드 설정 규칙 | 중간 |
| **n8n-code-javascript** | JavaScript 코드 노드 | 필요시 |
| **n8n-code-python** | Python 코드 노드 | 필요시 |

### MCP 활성화 방법
1. Antigravity 채팅 우측 상단 `...` 클릭
2. **MCP Servers** 선택
3. **Manage MCP Servers** → **Refresh** 클릭
4. `n8n-mcp` 활성화 확인

---

## 3. MCP 도구 레퍼런스

### 탐색 도구
| 도구 | 용도 | 예시 |
|------|------|------|
| `search_nodes` | 노드 검색 | `search_nodes("slack")` |
| `get_node` | 노드 상세 정보 | `get_node("n8n-nodes-base.slack", detail="standard")` |
| `search_templates` | 2,709개 템플릿 검색 | `search_templates("discord webhook")` |

### 검증 도구
| 도구 | 용도 | 프로필 옵션 |
|------|------|------------|
| `validate_node` | 노드 구성 검증 | minimal, runtime, ai-friendly, strict |
| `validate_workflow` | 워크플로우 전체 검증 | - |

### 관리 도구
| 도구 | 용도 |
|------|------|
| `n8n_create_workflow` | 새 워크플로우 생성 |
| `n8n_update_partial_workflow` | 점진적 수정 (17가지 작업) |
| `n8n_autofix_workflow` | 자동 수정 |
| `n8n_validate_workflow` | ID로 워크플로우 검증 |
| `n8n_test_workflow` | 워크플로우 테스트 실행 |

### nodeType 형식 주의
- **검색/검증**: `nodes-base.slack` (짧은 접두사)
- **워크플로우**: `n8n-nodes-base.slack` (긴 접두사)

---

## 4. 배포된 워크플로우

### 4.1 AIHub Chatbot v1.1

**파일**: `aihub_chatbot_final.json`
**엔드포인트**: `POST /aihub/recommend`

```
┌─────────────┐    ┌───────────────┐    ┌────────────┐
│   Webhook   │───→│ Process Input │───→│  AI Agent  │
│  (POST)     │    │  (JS Code)    │    │  (Gemini)  │
└─────────────┘    └───────────────┘    └─────┬──────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        │                     │                     │
                        ▼                     ▼                     │
                  ┌──────────┐        ┌──────────────┐              │
                  │ Gemini   │        │ Search AIHub │              │
                  │ Model    │        │ DB (HTTP)    │              │
                  └──────────┘        └──────────────┘              │
                                              │
                  ┌───────────────────────────┘
                  ▼
           ┌─────────────┐    ┌──────────┐
           │ Edit Fields │───→│ Response │
           │   (Set)     │    │ (Webhook)│
           └─────────────┘    └──────────┘
```

**노드 구성**:
| 노드 | 타입 | 역할 |
|------|------|------|
| Webhook | `n8n-nodes-base.webhook` | POST 요청 수신 |
| Process Input | `n8n-nodes-base.code` | 메시지 정규화, 키워드 추출 |
| AI Agent | `@n8n/n8n-nodes-langchain.agent` | AI 기반 응답 생성 |
| Gemini Model | `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` | LLM 모델 |
| Search AIHub DB | `@n8n/n8n-nodes-langchain.toolHttpRequest` | Supabase 검색 |
| Edit Fields | `n8n-nodes-base.set` | 응답 형식 정리 |
| Response | `n8n-nodes-base.respondToWebhook` | JSON 응답 반환 |

**Credential ID**: `LvKiLI0sFdNjT8AH` (Google Gemini API)

---

### 4.2 AIHub Embedding Generator

**파일**: `embedding_generator_workflow.json`
**트리거**: 수동 실행 (Manual Trigger)

```
┌───────┐    ┌─────────────────┐    ┌───────────────────┐
│ Start │───→│ Fetch All       │───→│ Split Into        │
│       │    │ Content (HTTP)  │    │ Batches (1개씩)   │
└───────┘    └─────────────────┘    └────────┬──────────┘
                                             │
                 ┌───────────────────────────┘
                 ▼
          ┌──────────────┐    ┌─────────────────────┐
          │ Prepare Text │───→│ Google Embedding    │
          │ (JS Code)    │    │ API (text-004)      │
          └──────────────┘    └──────────┬──────────┘
                                         │
          ┌──────────────────────────────┘
          ▼
   ┌─────────────┐    ┌──────────────────┐    ┌───────────┐
   │ Merge Data  │───→│ Save to Supabase │───→│ Loop Done │
   │ (JS Code)   │    │ (HTTP POST)      │    │           │
   └─────────────┘    └────────┬─────────┘    └───────────┘
                               │
                               └────────→ (Split Into Batches로 루프)
```

**처리 흐름**:
1. `aihub_content_catalog_v1` 테이블에서 전체 콘텐츠 조회
2. 1개씩 배치 처리
3. 제목 + 한줄소개 + 설명을 결합하여 텍스트 생성
4. Google text-embedding-004 모델로 768차원 벡터 생성
5. `aihub_embeddings` 테이블에 저장

---

## 5. 데이터베이스 설정

### 테이블: `aihub_embeddings`

```sql
CREATE TABLE aihub_embeddings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content_id TEXT NOT NULL,           -- aihub_content_catalog_v1.item_id
    item_type TEXT,                      -- guide, preset_agent 등
    content_text TEXT NOT NULL,          -- 임베딩 생성 원본 텍스트
    embedding vector(768),               -- 768차원 벡터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스
CREATE INDEX aihub_embeddings_embedding_idx
ON aihub_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

CREATE INDEX aihub_embeddings_content_id_idx ON aihub_embeddings (content_id);
```

### 검색 함수: `search_aihub_v2`

```sql
CREATE OR REPLACE FUNCTION search_aihub_v2(
  query_embedding vector(768),
  match_threshold float DEFAULT 0.1,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id text, item_type text, title text, one_liner text,
  description text, url text, tags jsonb, platform text, similarity float
)
```

**특징**:
- 코사인 유사도 기반 검색
- NULL 안전 처리 (COALESCE)
- `aihub_content_catalog_v1`과 JOIN
- 유사도 순 정렬

---

## 6. 핵심 워크플로우 패턴

### Webhook Processing (가장 일반적)
```
Webhook → 데이터 처리 → 응답
```

### HTTP API Integration
```
트리거 → HTTP Request → 데이터 변환 → 저장/응답
```

### Database Operations
```
트리거 → DB 조회 → 처리 → DB 저장
```

### AI Agent Workflow
```
입력 → AI Agent + Tools → 응답
       ├── LLM Model
       └── Tool (HTTP/DB/Code)
```

### Scheduled Tasks
```
Schedule Trigger → 작업 실행 → 알림/저장
```

---

## 7. 워크플로우 생성 체크리스트

### 계획
- [ ] 패턴 식별 (webhook/API/DB/AI/scheduled)
- [ ] 필요 노드 나열
- [ ] 데이터 흐름 설계

### 구현
- [ ] 트리거 노드 추가
- [ ] 데이터 소스 노드 추가
- [ ] 인증 자격증명 구성
- [ ] 변환 노드 추가 (Set, Code, IF)
- [ ] 출력 노드 추가

### 검증
- [ ] `validate_node`로 각 노드 검증
- [ ] `validate_workflow`로 전체 검증
- [ ] 샘플 데이터로 테스트

### 배포
- [ ] 워크플로우 설정 검토
- [ ] `activateWorkflow` 작업으로 활성화
- [ ] 초기 실행 모니터링

---

## 8. 표현식 문법 빠른 참조

```javascript
// Webhook 데이터 접근
{{$json.body.fieldName}}

// 이전 노드 참조
{{$node["Node Name"].json.field}}

// 환경변수
{{$env.API_KEY}}

// 조건부
{{$json.status === "active" ? "Yes" : "No"}}
```

**주의**: 코드 노드에서는 `{{}}` 사용하지 않음 - 직접 JavaScript 사용

---

## 9. 참조 링크

- [n8n 공식 문서](https://docs.n8n.io)
- [n8n-mcp GitHub](https://github.com/czlonkowski/n8n-mcp)
- [n8n-skills GitHub](https://github.com/czlonkowski/n8n-skills)

---

*마지막 업데이트: 2026-01-29*
