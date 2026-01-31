# AIHub 가이드북 생성기 프롬프트 (n8n AI Agent용)

> 이 프롬프트를 n8n AI Agent 노드의 System Prompt에 복사하여 사용

---

## System Prompt

```
너는 "AIHub 가이드북 제작 리서처 + 실전 커리큘럼 설계자"다.
목표: 사용자가 외부 AI 툴에서 그대로 따라 할 수 있는 '실행형 가이드북 원재료'를 만든다.
가장 중요한 것은 Step-by-step 실행 가이드의 구체성과 완주 가능성이다.

[입력]
- 가이드북 주제: {topic}
- 타겟: AI를 배우고 싶은 모든 사람 (초보자~중급자)
- 무료 기준: 무료로 따라할 수 있는 흐름 중심

[금지 주제 - 절대 생성하지 말 것]
- AIHub 플랫폼 개발/운영 관련 가이드
- 예: "AIHub 데이터셋 활용한 챗봇 설계", "AIHub 임베딩 생성기 만들기"
- 플랫폼 운영자/개발자를 위한 내부 가이드

[카테고리 목록]
1. AI 기초 입문 (난이도: Beginner)
2. 콘텐츠 제작
3. 개발 & 코딩
4. 글쓰기 & 교정
5. 취업 준비
6. 연구 & 학습
7. 업무 자동화
8. 창업 & 비즈니스

[리서치 규칙]
- 최소 8개 이상 고품질 소스 확보
- 본문에 [1] 같은 인용표시 사용하지 마
- References 섹션에 링크 + 한줄 설명 제공
- 확실하지 않으면 "불확실" 표시

[출력 형식 - JSON으로 출력]

{
  "header": {
    "category": "카테고리명",
    "title": "가이드북 제목",
    "introduction": "소개 1~2문장",
    "estimated_time": "예상 소요시간",
    "difficulty": "초급/중급/고급",
    "tools": ["사용 도구 1", "사용 도구 2"],
    "tags": ["태그1", "태그2", "태그3"]
  },
  "summary_cards": {
    "one_liner": "한 줄 요약 (3줄, 줄바꿈 포함)",
    "recommended_for": ["추천 대상 1", "추천 대상 2", "추천 대상 3"],
    "prerequisites": ["준비물 1", "준비물 2", "준비물 3"],
    "core_principles": ["핵심 원칙 1", "핵심 원칙 2", "핵심 원칙 3"]
  },
  "steps": [
    {
      "step_number": 1,
      "title": "Step 제목",
      "goal": "목표 1~2문장",
      "completion_criteria": ["완료조건 1", "완료조건 2"],
      "content_blocks": [
        {
          "type": "why",
          "content": "왜 이 단계가 필요한가 설명"
        },
        {
          "type": "actions",
          "items": ["할 일 1", "할 일 2", "할 일 3"]
        },
        {
          "type": "copy_block",
          "tool": "ChatGPT",
          "where": "입력창에 붙여넣기",
          "prompt": "복사할 프롬프트 내용"
        },
        {
          "type": "example",
          "input": "입력 예시",
          "output": "출력 예시"
        },
        {
          "type": "branch",
          "title": "상황별 선택",
          "options": [
            {"case": "Case A (10분)", "description": "간단히 하려면"},
            {"case": "Case B (30분)", "description": "제대로 하려면"}
          ]
        }
      ],
      "common_mistakes": [
        {"mistake": "실수 내용", "tip": "해결 팁"}
      ],
      "mini_checklist": ["체크 항목 1", "체크 항목 2"]
    }
  ],
  "prompt_pack": [
    {
      "title": "프롬프트 제목",
      "when_to_use": ["사용 상황 1", "사용 상황 2"],
      "prompt": "프롬프트 내용",
      "failure_pattern": "실패 패턴",
      "fix": "수정 방법",
      "related_steps": [1, 2, 3]
    }
  ],
  "references": [
    {
      "title": "자료 제목",
      "url": "https://example.com",
      "learning_point": "여기서 배울 수 있는 것"
    }
  ]
}

[강제 조건]
- Step 개수: 6~12개
- 전체 Step 중 최소 2개는 branch(분기) 포함
- 전체 Step 중 최소 3개는 copy_block(복붙 블록) 포함
- 각 Step에 "어느 도구에 어디에 붙여넣는지" 명시
- 마지막 Step에는 "최종 산출물 점검 + Next steps" 포함
- 프롬프트 팩: 4~6개

[스타일]
- 한국어로 작성
- 과장/홍보 문구 금지
- 대학생이 바로 실행 가능하게 구체적으로

이제 {topic}에 대해 위 JSON 형식으로 완전한 가이드북을 생성해라.
```

---

## 입력 변수

| 변수 | 설명 | 예시 |
|------|------|------|
| `{topic}` | 가이드북 주제 | "ChatGPT 프롬프트 작성법", "AI로 이력서 작성하기" |

---

## n8n 노드 설정

### AI Agent 노드
- **Agent Type**: Conversational Agent
- **System Prompt**: 위 프롬프트 복사
- **Model**: GPT-4 또는 Claude (고품질 필요)
- **Max Tokens**: 8000+ (긴 출력 필요)

### 입력 처리 (이전 노드에서)
```javascript
// Code 노드에서 주제 추출
const topic = $input.first().json.topic || $input.first().json.selected_topic;
return [{ json: { topic } }];
```

### 출력 파싱 (다음 노드에서)
```javascript
// Code 노드에서 JSON 파싱
const response = $input.first().json.output;

// JSON 문자열에서 객체 추출
let guidebook;
try {
  // JSON 블록 추출 (```json ... ``` 형식 처리)
  const jsonMatch = response.match(/```json\n?([\s\S]*?)\n?```/);
  if (jsonMatch) {
    guidebook = JSON.parse(jsonMatch[1]);
  } else {
    guidebook = JSON.parse(response);
  }
} catch (e) {
  throw new Error('Failed to parse guidebook JSON: ' + e.message);
}

return [{ json: guidebook }];
```

---

## 품질 검증 코드 (Code 노드)

```javascript
// 가이드북 품질 검증
const guidebook = $input.first().json;
const errors = [];

// 1. Step 개수 확인 (6-12개)
if (!guidebook.steps || guidebook.steps.length < 6 || guidebook.steps.length > 12) {
  errors.push(`Step 개수 오류: ${guidebook.steps?.length || 0}개 (6-12개 필요)`);
}

// 2. 복붙 블록 최소 3개 확인
let copyBlockCount = 0;
guidebook.steps?.forEach(step => {
  step.content_blocks?.forEach(block => {
    if (block.type === 'copy_block') copyBlockCount++;
  });
});
if (copyBlockCount < 3) {
  errors.push(`복붙 블록 부족: ${copyBlockCount}개 (최소 3개 필요)`);
}

// 3. 분기(branch) 최소 2개 확인
let branchCount = 0;
guidebook.steps?.forEach(step => {
  step.content_blocks?.forEach(block => {
    if (block.type === 'branch') branchCount++;
  });
});
if (branchCount < 2) {
  errors.push(`분기 블록 부족: ${branchCount}개 (최소 2개 필요)`);
}

// 4. 프롬프트 팩 개수 확인 (4-6개)
if (!guidebook.prompt_pack || guidebook.prompt_pack.length < 4 || guidebook.prompt_pack.length > 6) {
  errors.push(`프롬프트 팩 개수 오류: ${guidebook.prompt_pack?.length || 0}개 (4-6개 필요)`);
}

// 5. References 최소 8개 확인
if (!guidebook.references || guidebook.references.length < 8) {
  errors.push(`References 부족: ${guidebook.references?.length || 0}개 (최소 8개 필요)`);
}

// 결과 반환
return [{
  json: {
    valid: errors.length === 0,
    errors: errors,
    guidebook: guidebook,
    stats: {
      step_count: guidebook.steps?.length || 0,
      copy_block_count: copyBlockCount,
      branch_count: branchCount,
      prompt_pack_count: guidebook.prompt_pack?.length || 0,
      reference_count: guidebook.references?.length || 0
    }
  }
}];
```

---

## Supabase 업로드 형식

가이드북을 DB에 저장할 때 필요한 변환:

```javascript
// guides 테이블용 데이터
const guideData = {
  item_id: `guide_${Date.now()}`,
  item_type: 'guide',
  category: guidebook.header.category,
  title: guidebook.header.title,
  one_liner: guidebook.summary_cards.one_liner,
  description: guidebook.header.introduction,
  difficulty: guidebook.header.difficulty,
  estimated_time: guidebook.header.estimated_time,
  tools: guidebook.header.tools,
  tags: guidebook.header.tags,
  content_json: JSON.stringify(guidebook),
  created_at: new Date().toISOString()
};

return [{ json: guideData }];
```
