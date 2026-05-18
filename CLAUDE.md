# Claude 작업 지침

## 가이드 문서 참조 원칙 (Single Source of Truth)

이 저장소에서 **Schedule DB 작성 워크플로우**와 관련된 모든 작업은 반드시 아래 로컬 문서를 단일 진실 출처(SoT)로 참조한다.

- **로컬 가이드 (SoT)**: [`docs/schedule-db-workflow-guide.md`](docs/schedule-db-workflow-guide.md)

### 규칙

1. Notion 페이지(`https://www.notion.so/364d8a0a7b5a81eeb4fbf6d96dfc1a6b`)는 **참조 금지**. 워크플로우 절차·속성 정의·예외 처리 등은 모두 로컬 가이드에서만 가져온다.
2. 가이드 변경이 필요하면 **로컬 파일을 먼저 수정**하고 커밋한다. 필요 시 사용자가 Notion 쪽을 직접 따라 갱신한다 (역방향 동기화는 사용자 결정).
3. Schedule DB 항목을 새로 만들거나 갱신할 때 §2 속성 정의, §3 본문 템플릿, §5 예외 케이스, §9 학습 노트(§9-9 Sub Project 미연결 정책 포함)를 그대로 따른다.
4. Notion API 호출(`notion-create-pages`, `notion-update-page`, `notion-fetch` 등)은 여전히 사용 가능하다. "참조 금지"는 가이드 문서 본문에 한정한다 — Notion DB의 실제 데이터(Sub Project, Task DB, Monthly DB, Daily DB row)는 정상적으로 fetch·search·update 한다.

### 변경 이력

- 2026-05-18 — 가이드 SoT를 로컬로 전환. 이전까지 Notion 페이지를 참조했으나 로컬 사본 동기화 이후 로컬을 단일 출처로 정함.
