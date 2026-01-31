# n8n 워크플로우 AI 어시스턴트

## 🎯 개요
이 환경은 n8n 워크플로우를 AI가 자동으로 설계하고 구현할 수 있도록 설정되었습니다.

---

## ✅ 설치 완료

### n8n Skills (7개)
`C:\Users\PC\.gemini\antigravity\skills`에 설치됨

| 스킬 | 용도 |
|------|------|
| **n8n-mcp-tools-expert** | MCP 도구 사용 (최우선) |
| **n8n-expression-syntax** | 표현식 `{{}}` 문법 |
| **n8n-workflow-patterns** | 워크플로우 아키텍처 |
| **n8n-validation-expert** | 검증 및 디버깅 |
| **n8n-node-configuration** | 노드 설정 |
| **n8n-code-javascript** | JS 코드 노드 |
| **n8n-code-python** | Python 코드 노드 |

### n8n MCP Server
`C:\Users\PC\.gemini\antigravity\mcp_config.json`에 설정됨
- **n8n URL**: http://localhost:5678
- **연결 방식**: npx n8n-mcp

---

## 🚀 사용 방법

### Antigravity에서 MCP 활성화
1. 채팅 오른쪽 상단 `...` 클릭
2. **MCP Servers** 선택
3. **Manage MCP Servers** → **Refresh** 클릭
4. `n8n-mcp`가 활성화되면 완료!

### 워크플로우 요청 예시
```
"Discord에서 메시지를 받으면 OpenAI로 응답 생성 후 다시 Discord로 보내는 워크플로우 만들어줘"

"매일 아침 9시에 뉴스를 크롤링해서 Slack으로 보내는 자동화 만들어줘"

"웹훅으로 데이터를 받아서 Google Sheets에 저장하는 워크플로우 만들어줘"
```

---

## 📡 사용 가능한 MCP 도구

| 카테고리 | 도구 | 설명 |
|----------|------|------|
| **탐색** | `search_nodes` | 노드 검색 |
| | `get_node` | 노드 상세 정보 |
| | `search_templates` | 2,709개 템플릿 검색 |
| **검증** | `validate_node` | 노드 구성 검증 |
| | `validate_workflow` | 워크플로우 검증 |
| **관리** | `n8n_create_workflow` | 워크플로우 생성 |
| | `n8n_update_partial_workflow` | 워크플로우 수정 |
| | `n8n_autofix_workflow` | 자동 수정 |

---

## 📚 참조
- [n8n-mcp GitHub](https://github.com/czlonkowski/n8n-mcp)
- [n8n-skills GitHub](https://github.com/czlonkowski/n8n-skills)
- [n8n 문서](https://docs.n8n.io)
