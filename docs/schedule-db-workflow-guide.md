# Schedule DB 작성 워크플로우 가이드

> **이 파일이 단일 진실 출처(SoT)다.** Schedule DB 워크플로우와 관련된 모든 결정·작업은 이 문서를 기준으로 한다. Notion 페이지(<https://www.notion.so/364d8a0a7b5a81eeb4fbf6d96dfc1a6b>)는 더 이상 참조하지 않는다 — 보존용 사본일 뿐이며 본 로컬 파일의 내용이 우선한다.
>
> 변경이 필요하면 이 파일을 먼저 수정·커밋한다.
> 마지막 동기화 기준일: 2026-05-18

이 문서는 에이전트(또는 사람이) **Sub Project**를 받아서 그에 속하는 **Schedule DB 항목들**을 생성·작성할 때 따라야 할 절차와 규칙을 정의한다. 처음 보는 에이전트도 이 문서만으로 동일한 결과를 낼 수 있어야 한다.

---

## 0. TL;DR

1. 대상 **Sub Project** 페이지를 fetch해서 `Period`, `Objective`, `Status`, `Main Project DB` 확인
2. 해당 `Period` 시작 −2주 ~ 종료 +2주 범위의 **Daily DB** 페이지들을 모두 조회
3. Daily 기록의 `Overview/Retrospect/Solution` 등을 읽고 **반복되는 키워드/도메인 단위로 작업을 클러스터링**
4. 클러스터 하나당 **Schedule DB 항목 1개**를 생성. 템플릿(`[업무 키워드] 세부 내용`)을 기반으로 본문 작성
5. 본문은 검수자 callout 제거, `어떤 작업 / 왜 / 어떻게 / 산출물` 네 섹션을 채움
6. 관련 Daily DB 페이지들을 `Daily DB` relation으로, Sub Project를 `Sub Project DB` relation으로 연결

---

## 1. 작업 대상 DB 관계도

```
Main Project DB
      │  (relation, 1:N)
      ▼
Sub Project DB     ◀──── 이 문서의 입력
      │  (relation, 1:N)
      ▼
 Schedule DB       ◀──── 이 문서가 생성하는 산출물
      │  (relation, N:N)
      ▼
  Daily DB         ◀──── 작업 분할 근거 데이터
```

- **Sub Project DB** `collection://331d8a0a-7b5a-80b3-bc5f-000baa308aee`
- **Schedule DB** `collection://331d8a0a-7b5a-804b-ba22-000b8e5b7528`
- **Daily DB** `collection://7bc4b036-02f3-4d4b-b8c6-edc4563a0d65`

---

## 2. Schedule DB 속성 정의

생성하는 각 Schedule DB 항목은 아래 속성을 모두 채운다.

| 속성 | 타입 | 작성 규칙 |
| --- | --- | --- |
| **Name** | title | `[업무 키워드] 세부 내용` 형식. 키워드는 도메인 약어(Hardware, Perception, Navigation, Documentation, Resume 등). 기존 항목 컨벤션을 따른다. |
| **Objective** | text | 한 줄 목적. "~를 위해" 형태. |
| **Period** | date (range) | Daily DB 기록상 첫 등장 일자 ~ 마지막 등장 일자. 작업이 하루뿐이면 단일 날짜. |
| **Status** | status | 과거 완료 작업이면 `Done`. 기간을 넘겨 끝났으면 `Done (Delayed)`. 중단/보류는 `Archived`. |
| **Type** | select | Documentation / Research / Strategy / Design / Implementation / Integration / Testing / Deployment / Maintenance / Optimization 중 1개. 대부분 Implementation 또는 Research. |
| **담당자** | multi-select | 기본은 `최정민`. Daily 기록에 다른 사람이 명시되어 있으면 추가. (선택지: 최정민 / WATT / 박한규) |
| **Sub Project DB** | relation (1개) | **반드시** 입력받은 Sub Project 페이지 URL을 넣는다. 단, §9-9 정책에 해당하는 task는 `null`. |
| **Daily DB** | relation (N개) | 해당 작업이 언급된 모든 Daily 페이지 URL을 넣는다. |
| **Predecessor / Successor Task** | self-relation | 같은 Sub Project 내 작업 간 선후관계가 명확할 때만 연결. 불명확하면 비워둔다. |

---

## 3. 본문 템플릿 작성 규칙

기본 템플릿 페이지: <https://www.notion.so/331d8a0a7b5a80988cafdc0ea961f55e> (`[업무 키워드] 세부 내용`)

### 3-1. 제거할 것

> **Schedule DB 검수자 callout 블록은 제거한다.** (Gemini Gem 링크가 들어있는 빨간 callout)
> 기존 템플릿에 자동 삽입되더라도 생성 직후 삭제 또는 처음부터 본문에서 누락한다.

### 3-2. 채워야 할 4개 섹션

| 섹션 | 헤딩(고정) | 채우는 내용 |
| --- | --- | --- |
| What | `## 어떤 작업을 하나요?` | 작업의 범위·대상을 2~4문장으로. 어떤 시스템/모듈/문서를 다루는지 구체적으로 명시. |
| Why | `## 이 작업을 왜 해야 하나요?` | 상위 Sub Project의 Objective와 어떻게 연결되는지. "이 작업이 없으면 무엇이 막히는지"를 기준으로 작성. |
| How | `## 어떻게 접근할 건가요?` | 체크리스트(`- [ ]`) 또는 번호 매김 단계로 분해. 각 단계마다 **완료 기준**을 명시. |
| 산출물 | `## 산출물은 무엇인가요? (작업 완료의 정의) 자산 DB로 이동까지` | 코드/문서/측정 결과/링크 등 검증 가능한 형태로. "~ launch 파일 추가", "~ 문서 작성 완료" 같은 동작 완료형. |

섹션 헤딩 문자열은 그대로 유지한다.

### 3-3. 본문 끝의 "업무 상세 노트"

템플릿 끝에 있는 `업무 상세 노트` 서브페이지 링크는 그대로 둔다. 작성 시점에는 비워둬도 됨.

---

## 4. 절차 (Step-by-Step)

### Step 1. Sub Project 페이지 fetch

입력으로 받은 Sub Project URL/ID를 `notion-fetch`로 조회한다. 확보할 정보:

- `Period` (start, end) → Daily DB 검색 범위
- `Objective` → Why 섹션 작성 근거
- `Main Project DB` → 상위 컨텍스트 (필요 시 추가 fetch)
- 본문 회고 내용(있다면) → 작업 클러스터링 힌트

### Step 2. Daily DB 검색

범위: `Period.start − 14일` ~ `Period.end + 14일`

Daily 페이지 제목 포맷은 `YYYY년 MM월 DD일`. `notion-search`의 `data_source_url`을 Daily DB로 두고 월 단위로 쿼리해서 페이지들을 수집한다. 각 페이지를 `notion-fetch`로 열어 `Overview / Retrospect / Solution / Compliment / Feedback` 텍스트를 본다.

### Step 3. 작업 클러스터링

Daily 기록을 읽고 다음 기준으로 묶는다 (우선순위 순):

1. **연속된 키워드/모듈명**: 며칠에 걸쳐 동일한 기능/모듈/문서를 다루면 한 작업
2. **도메인**: 하드웨어, Perception, Navigation, Documentation 등 도메인이 같고 목표가 이어지면 한 작업
3. **산출물 단위**: 같은 launch 파일·같은 노드·같은 PR로 귀결되면 한 작업
4. **시간적 인접성**: 1~2일 간격이면 묶고, 1주 이상 비면 끊는다

작업 단위 권장 크기: **1개당 평균 3~10 Daily 기록**. 너무 작으면(<2일) 다른 작업과 합치고, 너무 크면(>20일) 페이즈로 분할한다.

### Step 4. Schedule DB 항목 생성

`notion-create-pages` 호출. parent는 Schedule DB 데이터소스 (`data_source_id: 331d8a0a-7b5a-804b-ba22-000b8e5b7528`).

- `template_id`는 기본 템플릿 `331d8a0a-7b5a-8098-8caf-dc0ea961f55e`을 사용하지 말 것 (검수자 callout이 자동 주입됨). 대신 `content`를 직접 작성한다.
- properties는 §2 표대로 채운다.
- 여러 항목을 한 번에 생성할 수 있으므로 가능하면 배치 호출.

### Step 5. 검증

생성 후 각 항목을 `notion-fetch`로 다시 열어 확인:

- [ ] 검수자 callout이 없는가
- [ ] What/Why/How/산출물 4개 섹션이 모두 채워졌는가
- [ ] `Sub Project DB` relation이 정확한 상위 프로젝트를 가리키는가 (또는 §9-9에 따라 의도적으로 null인가)
- [ ] `Daily DB` relation이 근거 일자 페이지들을 가리키는가
- [ ] Period가 Daily 기록의 실제 범위와 일치하는가

---

## 5. 예외 케이스

### 5-1. Daily DB 기록이 없는 Sub Project (Daily DB 시작 이전)

**Daily DB는 2024년 10월부터 데이터가 존재한다.** 그 이전(2024-09 이하) 시점의 Sub Project는 Daily DB만으로는 작업을 분할할 수 없으므로, **아래 보조 데이터 소스를 조합하여 대체한다.**

#### 보조 데이터 소스 — 와트(WATT) 정규직 관련

와트 정규직으로 수행한 작업은 아래 2개 DB에 기록되어 있다. 위치: `workspace > private > 와트 정규직 (현재) > Project > develop` 하위.

| DB | 데이터소스 | 역할 |
| --- | --- | --- |
| **Task DB** | `collection://74a66886-d858-4d63-81e2-c4234f9f84da` | 작업 단위 기록. `Task / Why / How / Results / Retrospect / TargetDuration / RealDuration / Completeness / StartingDay` 속성 보유. **Schedule DB와 거의 1:1 매핑됨.** |
| **Monthly DB** | `collection://b053f150-b3a9-43b2-a1dc-7aceba988233` | 월별 Overview 페이지. 페이지 본문에 **일별 column** 형식으로 하루하루 작업/코드 노트/체크리스트가 정리되어 있어 **Daily DB의 역할을 대신**한다. |

#### 속성 매핑 (Task DB → Schedule DB)

| Task DB | Schedule DB | 비고 |
| --- | --- | --- |
| `Task` | `Name` | `[키워드] 세부 내용` 포맷으로 재작성. |
| `Why` | 본문 "이 작업을 왜 해야 하나요?" 섹션 | 그대로 옮긴다. |
| `How` | 본문 "어떻게 접근할 건가요?" 섹션 | 체크리스트 형식으로 변환. |
| `Results` | 본문 "산출물은 무엇인가요?" 섹션 | 그대로. |
| `Retrospect` | 본문 "특이사항" 섹션 | 관찰/아쉬운 점. |
| `StartingDay` | `Period.start` | StartingDay는 created_time. RealDuration이 있으면 `Period.end` 추정에 활용. |
| `RealDuration` / `TargetDuration` | `Period.end` 산출 | "3일", "1주" 같은 자연어를 파싱해서 더한다. 애매하면 Monthly DB의 일별 기록으로 교차 검증. |
| `Completeness` (100%) | `Status = Done` | 100% 미만이면 `Done (Delayed)` 또는 `Archived`로 판단. |

#### 절차 변경점 (본문 §4 대비)

- **Step 2 (Daily DB 검색)** 대신:
  1. Monthly DB에서 Sub Project Period에 해당하는 `YYYY년 MM월` 페이지들을 조회 (Period의 시작/종료 월 + 앞뒤 1개월 패딩).
  2. 각 Monthly 페이지를 fetch해서 본문의 일별 column 기록을 읽는다. 이게 **Daily 기록을 대체한다.**
  3. Task DB를 `created_date_range` 필터로 같은 기간 조회해서 이미 정리된 작업 단위를 확보한다.
- **Step 3 (클러스터링)**: Task DB에 이미 작업 단위가 있으면 **Task DB의 row 하나당 Schedule DB 항목 하나**를 기본값으로 둔다. Monthly DB 일별 기록과 교차 검증해서 누락이 있으면 추가 항목 생성.
- **Step 4 (생성)**:
  - `Daily DB` relation 속성은 **비워둔다** (Daily DB에 대응 페이지가 없음).
  - `Sub Project DB` relation은 정상적으로 연결.
  - 본문 끝에 **"참고 데이터 소스"** 구역을 두고 관련 Monthly·Task 페이지 URL을 각주 형태로 넣는다.

#### 구체 적용 케이스: PoC Softbank Robotics and Yamato

- **Sub Project URL**: <https://www.notion.so/351d8a0a7b5a804e929ed3baeec1b193>
- **Period**: 2024-07-01 ~ 2024-08-31
- **Task DB View**: <https://www.notion.so/jeongminspace/85c23f93e5f64541a426d619993c053f?v=27c9e05ea863414d8aa7666101f449be>
- **Monthly DB View**: <https://www.notion.so/jeongminspace/30dd8a0a7b5a807c8d75eba77dd4a75a?v=30dd8a0a7b5a80348ecb000cc8899acb>
- **항상 결합 확인해야 할 Monthly 페이지**:
  - `2024년 06월` (패딩)
  - `2024년 07월` (핵심)
  - `2024년 08월` (핵심)
  - `2024년 09월` (패딩)

더불어 PoC Sub Project 페이지 자체 본문에도 `### 무엇을 했는가 ?` 회고가 있어서 **3중 교차 검증**이 가능하다 (Sub Project 회고 × Task DB × Monthly DB 일별).

### 5-2. 회고/Overview 페이지에 이미 작업이 정리되어 있는 경우

일부 Sub Project 페이지에는 `### 무엇을 했는가 ?` 같은 회고 섹션에 이미 작업 6~10개가 bullet으로 정리되어 있다. 이 경우 회고 bullet과 Daily 기록을 **교차 검증**해서 작업 단위를 정한다. 회고 bullet 하나당 Schedule 항목 1개를 기본값으로 두고, Daily 기록상 분량이 크면 더 잘게 쪼갠다.

---

## 6. 작성 톤 가이드

- 기존 Schedule DB 항목들의 톤을 따른다. 예: `[Hardware] electrical system inspection`, `[Perception] research and develop zone ros2 package`
- 한국어 / 영어 혼용 가능. Name의 키워드는 영어, 본문 설명은 한국어가 일반적.
- How 섹션은 명령형 문장("~한다")으로 통일.
- 코드/명령어는 인라인 코드(`backtick`)로 표기.
- 외부 페이지·노드·도구 이름은 가능한 한 정확히(예: `teb_local_planner`, `SpatioTemporalVoxelLayer`).

---

## 7. 사용 예시

```
에이전트 입력:
  Sub Project: "James Mobile Robot Development"
  Sub Project URL: https://www.notion.so/331d8a0a7b5a80949ce0fcaeca179803

에이전트 작업:
  1. fetch → Period 확인 (예: 2025-08-01 ~ 2026-05-31)
  2. Daily DB 검색 (2025-07-15 ~ 2026-06-14)
  3. 일별 기록 N개 fetch
  4. 키워드 클러스터링 → 작업 7~12개로 분해
  5. Schedule DB에 N개 항목 batch 생성 (template 우회, content 직접 작성)
  6. 검증 체크리스트 통과
```

---

## 8. 변경 이력

- 2026-05-18 — 초안 작성. PoC Softbank 케이스를 통해 Daily DB 시작 시점(2024-10) 한계 확인.
- 2026-05-18 — §5-1 확장: 와트 Task DB / Monthly DB를 보조 데이터 소스로 정의, 속성 매핑 표와 PoC Softbank 적용 케이스 명시.
- 2026-05-18 — §9 신설: PoC Softbank 첫 항목(`[Navigation] tune teb_local_planner for narrow path`) 작성 과정에서 발견한 8가지 주의사항 추가.
- 2026-05-18 — §9-9 신설: Sub Project 미연결 task 처리 정책 정의 (Recovery / 스테이션 R&D / mW / JamesW1.3 유지보수 등 PoC Softbank 외부 작업 처리 케이스 반영).

---

## 9. 실작업 학습 노트 (PoC Softbank 첫 항목 작성 후 추가)

PoC Softbank Sub Project의 첫 Schedule 항목([`[Navigation] tune teb_local_planner for narrow path`](https://www.notion.so/364d8a0a7b5a81149bd0f47cc4850333)) 생성 과정에서 발견한 주의사항을 §1~§8에 보강하는 형태로 기록한다.

### 9-1. Period는 Task DB `StartingDay`로 잡지 말 것

- Task DB의 `StartingDay`(=created_time)는 회고·정리 시점일 가능성이 있다. 특히 "Develop modules in James & Station" 페이지 하위 **inline DB**의 row는 작업 종료 후 정리용으로 작성된 경우가 많다.
- **첫 항목 사례**: TEB Local Planner inline row는 `StartingDay=2024-07-23`이지만 Monthly DB 일별 column에는 **2024-07-03 단 하루만 등장**. 실제 Period는 2024-07-03 단일 일자로 확정.
- 규칙: `Period`는 **Monthly DB 일별 column에서 실제 등장한 일자**만 사용한다. 단일 등장이면 `date:Period:end=NULL`.
- 절대 금지: Sub Project Period의 end(예: 2024-08-31)에 모든 task end를 맞추는 것 — 과대예측 위험.

### 9-2. "Develop modules in James & Station" inline DB는 별개 데이터 소스

- 해당 페이지(`6fec6d5e-21e3-4efc-949a-8ae9d540e2d3`)는 본문에 별도 inline DB(`collection://6f3122a6-f8b7-4209-93f2-d4d762232083`)를 가진다.
- 스키마가 메인 Task DB와 다르다: `모듈` / `완성도` / `회고` (메인 Task DB의 `Task`/`Why`/`How`/`Results`/`Retrospect`/`Completeness`와 다름).
- `notion-search`로 메인 Task DB(`collection://74a66886-d858-4d63-81e2-c4234f9f84da`)를 검색해도 inline DB row는 나오지 않는다.
- 메인 Task DB 검색 결과에 `Develop modules in James & Station` 페이지가 등장하면, **그 페이지를 별도 fetch해서 inline DB row를 확인**해야 한다.
- PoC Softbank의 경우 TEB Local Planner, DWA 등이 이 inline DB에 있다.

### 9-3. `notion-search`는 25개 한도 — 도메인 키워드 반복 검색

- 단일 쿼리로는 누락 발생. PoC 기간 Task DB는 첫 검색(query=`task`)에서 25개였으나 실제로는 28개 이상이었다.
- 도메인 키워드(`협로`, `teb`, `dwa`, `pose`, `이미지`, `법선`, `cliff`, `imu`, `리프트`, `시연`, `chatgpt`, `yolo` 등)로 반복 검색.
- 각 검색에 `filters.created_date_range`(Period ± 2주)를 항상 적용.

### 9-4. 회고 6개 = 시드, 실제 작업 수는 더 많다

- Sub Project 본문 `### 무엇을 했는가?` 회고 bullet은 핵심 작업의 시드일 뿐, 전수가 아니다.
- PoC Softbank 사례: 회고 6개 < 메인 Task DB row 약 26개 < 최종 Schedule 항목 약 38개.
- 회고 일부(Pose Saver, 이미지 수집, 법선 벡터, Cliff Detector)는 메인 Task DB에 별도 row가 없고 inline DB·외부 페이지에만 존재한다.
- Monthly DB 일별 column에만 등장하는 작업(예: 카드 태깅, 층 정보 생성, Auto Initial Pose, 리프트 수리, 판교·야마토·코엑스 시연, JamesW IRED/컨베이어/음성/도킹, 데모 환경 세팅 잡무)도 별도 Schedule 항목으로 잡아야 한다.

### 9-5. 묶기 결정은 사용자 확인 필수 — 자동 판단 금지

- Task DB row가 잘게 쪼개진 경우 묶을지 1:1 유지할지는 **반드시 사용자 결정**.
- PoC Softbank 적용 결정 예시:
  - ChatGPT 관련 6 row → 1개 통합 (`[Research] ChatGPT 한·일 OCR/번역 통합 검증`)
  - 학습 2 row (`Understanding James Code` + `Understanding Station Code`) → 1개 통합
  - RGBD 카메라 2 row (`Test Depth Camera SEN0579` + `RGBD A075V`) → 1개 통합 (`[Hardware] RGBD 카메라 비교 테스트`)
  - `Develop modules in James & Station` → 메타 task로 유지하고 JamesW 4개(IRED/컨베이어/음성/도킹) + 스테이션 리팩토링을 그 하위로
- 묶을 후보 식별 시 항상 사용자에게 옵션과 함께 질문.

### 9-6. 본문 작성 추가 규칙 (§3-2 보강)

4섹션(어떤 작업/왜/어떻게/산출물) 뒤에 다음 2개 섹션을 추가한다.

| 섹션 | 헤딩(고정) | 채우는 내용 |
| --- | --- | --- |
| Retrospect | `## 특이사항` | Task DB `Retrospect` 또는 Sub Project 회고의 "아쉬운점" 매핑. 1~3문장. |
| Sources | `## 참고 데이터 소스` | 보조 출처 URL을 bullet로. (1) Task DB row URL — inline DB row 포함. (2) Sub Project 회고 페이지의 해당 bullet 링크. (3) Monthly DB 일별 column 페이지 — 해당 일자 mention이 있는 경우. |

검수자 callout은 절대 추가하지 않는다 — `template_id` 미사용 + `content` 직접 작성으로 우회한다 (§3-1 재확인).

### 9-7. SQLite property 작성 표기

`notion-create-pages` / `notion-update-page` 호출 시 properties JSON 표기:

- `Sub Project DB` (limit=1 관계): JSON array of URL string. 예: `"[\"https://www.notion.so/351d8a0a7b5a804e929ed3baeec1b193\"]"`
- `담당자` (multi-select): JSON array string. 예: `"[\"최정민\"]"`
- 날짜: `date:Period:start` (ISO-8601), `date:Period:end` (단일 일자면 NULL), `date:Period:is_datetime` (0)
- `Status` / `Type`: 정확한 option name 문자열. 예: `"Done"`, `"Implementation"`
- `Daily DB` (관계): 2024-10 이전 작업은 비워둠 (§5-1)

### 9-8. 검증 체크리스트 (생성 직후 매 항목마다 실행)

- [ ] 검수자 callout 없음
- [ ] What / Why / How / 산출물 4개 섹션 모두 채워짐
- [ ] **특이사항** 섹션 채워짐 (회고·Retrospect 매핑)
- [ ] **참고 데이터 소스** 섹션에 보조 출처 URL 있음
- [ ] `Sub Project DB` relation = 정확한 상위 프로젝트 1개
- [ ] `Daily DB` relation = 비워둠 (2024-10 이전 작업)
- [ ] `Period` = Monthly DB 실제 등장 일자 (Task DB `StartingDay` 아님)
- [ ] 단일 일자 작업이면 `date:Period:end` = NULL
- [ ] `Type` / `Status` / `담당자` 정확한 옵션 문자열
- [ ] **`Sub Project DB`가 NULL이면** 본문 "특이사항" 섹션에 미연결 사유 + 후속 연결 대상 Sub Project 명시 메모가 있는가

### 9-9. Sub Project 미연결 task 처리 정책

PoC Softbank Sub Project 작업을 정리하다 보면 Monthly/Task DB에 등장하지만 **PoC Softbank Sub Project에 속하지 않는** task가 발견된다. 이런 task는 PoC에 강제 연결하지 말고 `Sub Project DB`를 비운 채(`NULL`) Schedule DB에 먼저 등록하고, 해당 Sub Project가 생성되면 그때 relation을 채운다.

#### 어떤 task가 여기에 해당하는가

- **Recovery Mobile Manipulator 하위 작업**: CM4 USB-to-CAN 펌웨어, IMU 축 정렬 등 — Recovery Sub Project가 아직 없음.
- **스테이션 R&D**: 스테이션 박스 크기 추정용 대체 RGBD 카메라(SEN0579·A075V) 검토 등 — 스테이션 Sub Project가 아직 없음.
- **mW 시스템 세팅**: 4K IMX378 FOV 측정 등 — mW Sub Project가 아직 없음.
- **시연 이후 유지보수**: 코엑스 시연 뒤 JamesW1.3 리프트 와이어 교체 등 — PoC Softbank(일본 시연) Period 안에 떨어져 있더라도 PoC 산출물이 아닌 별도 유지보수 활동.
- 판단 기준: Sub Project Objective와 직접 연결되지 않으면 PoC에 묶지 않는다 (§9-5 "묶기 결정은 사용자 확인 필수" 원칙).

#### 작성 규칙

- `Sub Project DB` 속성: `null` (`notion-create-pages` properties에서 `"Sub Project DB": null`)
- `Daily DB` 속성: 그대로 §5-1 규칙대로 비워둠 (2024-10 이전 작업)
- 본문 **"특이사항" 섹션에 반드시 다음 형식의 메모 1줄** 포함:
  - `**이 task는 [PoC Softbank Sub Project가 아닌 / 일본 PoC 시연용 작업이 아닌] [상위 컨텍스트(예: Recovery Mobile Manipulator / 스테이션 R&D / mW 시스템 세팅 / JamesW1.3 유지보수)] 작업**이다. 추후 [해당 Sub Project명] 생성 시 연결한다 (가이드 §9 정책).`
- Status·Type·Period·담당자 등 다른 속성은 §2 규칙 그대로.

#### 추후 연결 절차

해당 Sub Project가 생성되면:

1. `notion-search`로 `Sub Project DB`가 비어있는 Schedule 항목 조회 (`Sub Project DB is_empty`).
2. 본문 "특이사항"의 미연결 사유 메모를 보고 어떤 Sub Project에 연결할지 식별.
3. `notion-update-page`로 `Sub Project DB` relation을 채운다. 본문 메모는 그대로 두거나, "~~로 후속 연결됨" 형태로 짧게 갱신.

#### 적용 사례 (2026-05-18 기준)

PoC Softbank Schedule 작성 중 C 카테고리(Sub Project 미연결) 5개 항목이 이 정책으로 등록됨:

- C-16 `[Hardware] upload firmware to CM4 USB-to-CAN module` → Recovery Mobile Manipulator
- C-17 `[Research] evaluate alternative RGBD cameras (SEN0579, A075V) for station box estimation` → 스테이션 R&D
- C-18 `[Hardware] configure IMU axis alignment via watt_robot_common imu.launch` → Recovery Mobile Manipulator
- C-19 `[Hardware] measure 4K IMX378 FOV on mW system installation` → mW 시스템 세팅
- C-20 `[Hardware] debug and repair JamesW1.3 lift mechanism (wire replacement)` → JamesW1.3 유지보수
