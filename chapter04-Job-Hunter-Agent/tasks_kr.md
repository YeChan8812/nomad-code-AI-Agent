# Tasks Configuration (Translated to Korean)

이 문서는 `config/tasks.yaml` 파일의 내용을 한국어로 번역한 것입니다.

## 1. Job Extraction Task (직업 추출 작업)
**ID:** `job_extraction_task`  
**담당 에이전트:** `job_search_agent`

### 설명 (Description)
{level} 레벨의 {position} 직업을 {location}에서 찾고 추출합니다.

단계는 다음과 같습니다:
1. 웹 검색 도구를 사용하여 {location}의 {level} 레벨 {position} 직업을 검색합니다.
2. 검색 결과에서 직업 목록을 추출합니다.
3. {location}의 {level} 레벨 {position} 직업이 아닌 목록을 필터링합니다.

### 예상 결과물 (Expected Output)
`JobList` 스키마와 일치하는 JSON 객체.

---

## 2. Job Matching Task (직업 매칭 작업)
**ID:** `job_matching_task`  
**담당 에이전트:** `job_matching_agent`

### 설명 (Description)
당신은 커리어 매칭 전문가입니다.

추출된 직업 목록(JobList)과 사용자의 이력서가 주어졌을 때, 각 직업이 사용자의 다음 항목과 얼마나 잘 맞는지 평가합니다:
- 기술 스택
- 역할 레벨
- 산업 및 회사 규모 선호도
- 원격/근무 유연성
- 계약 형태
- 급여 기대치
- 이력서의 키워드 및 결격 사유

각 직업에 대해 1(부적합)부터 5(완벽한 적합)까지의 `match_score`를 할당하고 이유를 설명합니다.

목록의 각 직업에 `match_score`와 `reason` 필드를 추가합니다.

원래의 모든 직업 필드를 그대로 유지합니다. 어떤 직업도 변경하거나 걸러내지 마십시오.

### 예상 결과물 (Expected Output)
원래 `Job` 스키마와 일치하는 JSON 객체이며, 각 직업당 두 개의 추가 필드가 있습니다:
- `match_score`: 1에서 5 사이의 정수
- `reason`: 점수에 대한 짧은 설명

---

## 3. Job Selection Task (직업 선택 작업)
**ID:** `job_selection_task`  
**담당 에이전트:** `job_matching_agent`

### 설명 (Description)
당신은 직업 선택 전문가입니다.

`match_score`와 `reason` 필드가 포함된 직업 목록(RankedJobList)이 주어졌을 때, 당신의 임무는 다음과 같습니다:
1. `match_score`와 이유를 분석하여 사용자에게 **가장 적합한 직업**을 결정합니다.
2. 사용자의 선호도, 기술, 목표에 가장 부합하는 단 하나의 최고의 직업을 선택합니다.
3. 이력서와 직업의 일치도를 바탕으로 간결한 `reason` 필드에 선택을 정당화합니다.
4. 최고의 직업에 대해 `selected` 필드를 `true`로 설정하고 나머지 모든 직업은 `false`로 설정합니다.

원래 직업 필드(예: job_title, company_name 등)의 내용은 변경하지 마십시오.

### 예상 결과물 (Expected Output)
선택된 직업의 `ChosenJob` 스키마와 일치하는 JSON 객체.

---

## 4. Resume Rewriting Task (이력서 재작성 작업)
**ID:** `resume_rewriting_task`  
**담당 에이전트:** `resume_optimization_agent`
**출력 파일:** `output/rewritten_resume.md`

### 설명 (Description)
당신은 이력서 최적화 전문가입니다.

포함된 지식 소스로 제공된 사용자의 실제 이력서와 선택된 직업(ChosenJob)이 주어졌을 때, 당신의 임무는 **직무와의 연관성을 강조하기 위해 기존 이력서를 재작성**하는 것입니다. 단, 사실을 **조작하거나 부풀리지 않아야** 합니다.

중점 사항:
- 관련 기술, 프로젝트, 성과를 재배열, 재구성 및 강조
- 주요 직무 요건 및 키워드를 반영하도록 요약 및 경력 불릿 포인트 작성
- 직무 공고의 어조, 기술 초점, 용어에 맞추기
- 사용자의 원본 이력서에 있는 실제 경험만 유지

관련 없는 내용을 제거하거나 명확성을 위해 직함을 약간 수정할 수 있지만, **가짜 회사, 기술, 날짜, 역할을 추가해서는 안 됩니다**.

### 예상 결과물 (Expected Output)
선택된 직업에 맞춰 재작성되고 최적화된 **실제 사용자의 이력서**의 마크다운 형식 버전입니다.
이력서는 진실된 내용이어야 하며 사용자의 실제 이력에 근거해야 합니다.

---

## 5. Company Research Task (회사 조사 작업)
**ID:** `company_research_task`  
**담당 에이전트:** `company_research_agent`
**출력 파일:** `output/company_research.md`

### 설명 (Description)
당신은 회사 조사 및 인터뷰 준비 전문가입니다.

선택된 직업(ChosenJob)이 주어졌을 때, 공개 웹 리소스를 사용하여 채용 회사를 조사합니다.
당신의 목표는 다음과 같습니다:
1. 회사의 규모, 산업, 미션, 가치, 최근 뉴스를 파악합니다.
2. 채용 공고를 분석하여 팀 구조와 제품 맥락을 추론합니다.
3. 지원자가 직면할 수 있는 잠재적인 인터뷰 주제와 질문을 제안합니다.
4. 지원자가 인터뷰 중에 질문할 수 있는 통찰력 있는 질문 목록을 제공합니다.

회사 웹사이트, 보도 자료, 블로그, 소셜 미디어, 리뷰를 사용하여 통찰력을 얻으십시오.

### 예상 결과물 (Expected Output)
다음 섹션이 포함된 마크다운 파일:
- ## Company Overview (회사 개요)
- ## Mission and Values (미션 및 가치)
- ## Recent News or Changes (최근 뉴스 또는 변경 사항)
- ## Role Context and Product Involvement (역할 맥락 및 제품 관여)
- ## Likely Interview Topics (예상 인터뷰 주제)
- ## Suggested Questions to Ask (제안 질문)

---

## 6. Interview Prep Task (인터뷰 준비 작업)
**ID:** `interview_prep_task`  
**담당 에이전트:** `interview_prep_agent`
**출력 파일:** `output/interview_prep.md`

### 설명 (Description)
당신은 인터뷰 준비 코치입니다.

다음 정보를 결합하십시오:
1. 선택된 직업 (ChosenJob)
2. 맞춤형 이력서 (RewrittenResume)
3. 회사 조사 요약 (CompanyResearch)

다음 내용을 포함하는 상세한 인터뷰 준비 문서를 작성하십시오:
- 직무 요약 및 지원자에게 적합한 이유
- 가장 관련성 높은 부분에 초점을 맞춘 맞춤형 이력서의 스냅샷
- 회사, 제품, 가치에 대한 간결한 요약
- 직무 및 회사에 기반한 예상 인터뷰 질문
- 지원자가 면접관에게 물어볼 수 있는 맞춤형 질문
- 어조, 초점 영역, 주의해야 할 위험 신호(Red flags)에 대한 조언

문서는 깔끔하고 명확하며 지원자가 인터뷰에서 전략적 우위를 점할 수 있도록 설계되어야 합니다.
문서는 너무 짧지 않아야 하며, 포괄적인 내용이 되도록 필요한 만큼 충분히 작성하십시오.

### 예상 결과물 (Expected Output)
"Interview Prep: $CompanyName – $JobTitle"라는 제목의 마크다운 문서로 다음 섹션을 포함합니다:
- ## Job Overview (직무 개요)
- ## Why This Job Is a Fit (이 직무가 적합한 이유)
- ## Resume Highlights for This Role (이 역할을 위한 이력서 하이라이트)
- ## Company Summary (회사 요약)
- ## Predicted Interview Questions (예상 인터뷰 질문)
- ## Questions to Ask Them (질문할 내용)
- ## Concepts To Know/Review (알아두거나 검토해야 할 개념)
- ## Strategic Advice (전략적 조언)
