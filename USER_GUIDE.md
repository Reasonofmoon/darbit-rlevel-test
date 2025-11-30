# CEFR 영어 레벨 테스트 시스템 - 사용자 가이드

## 📖 시스템 소개

이 시스템은 **CEFR(Common European Framework of Reference for Languages)** 국제 기준에 맞춰 학생의 영어 능력을 과학적으로 평가하는 통합 솔루션입니다.

### 🎯 주요 특징

1. **5단계 레벨 측정**: PRE-A1부터 B2까지
2. **5개 영역 평가**: 읽기, 어휘, 회화, 문법, 작문
3. **20개 세부 평가 항목**: 루브릭 기반 정밀 평가
4. **과학적 문항 설계**: 선택지 균형, 난이도 조절
5. **자동 결과 분석**: 강점/약점 진단 및 학습 권장사항

---

## 🚀 빠른 시작

### 1단계: 레벨별 시험지 생성

```bash
# 단일 레벨 생성
cd /home/claude/cefr_level_test
python3 main.py --mode generate --level A2

# 전체 레벨 일괄 생성
python3 main.py --mode batch
```

### 2단계: 생성된 파일 확인

생성된 파일은 다음 위치에 저장됩니다:

```
/mnt/user-data/outputs/
├── tests/
│   ├── test_paper_PRE-A1_*.html (시험지)
│   ├── test_paper_A1_*.html
│   ├── test_paper_A2_*.html
│   ├── test_paper_B1_*.html
│   └── test_paper_B2_*.html
│
├── answer_keys/
│   ├── answer_key_PRE-A1_*.html (정답지)
│   ├── answer_key_A1_*.html
│   └── ... (각 레벨별)
│
└── results/
    └── result_학생이름_레벨_*.html (결과지)
```

### 3단계: 시험 실시

1. **시험지 출력**
   - HTML 파일을 브라우저에서 열기
   - Ctrl+P (Print) → PDF로 저장
   - 학생에게 배포

2. **시험 진행**
   - 객관식: 답안지에 체크
   - 작문: 지정된 공간에 작성
   - 제한 시간: 레벨별 45-60분

3. **채점**
   - 객관식: 정답지와 대조
   - 작문: 루브릭 기준 평가 (또는 LLM API 사용)

### 4단계: 결과 분석

```python
from main import CEFRTestSystem

system = CEFRTestSystem()

# 학생 답안 입력
student_answers = {
    'R1': 'A', 'R2': 'B', # ...
}

correct_answers = {
    'R1': 'A', 'R2': 'C', # ...
}

# 결과 생성
system.evaluate_test(
    level='A2',
    student_name='김영희',
    student_answers=student_answers,
    correct_answers=correct_answers
)
```

---

## 📊 레벨별 세부 정보

### PRE-A1 (Basic Beginner)
- **대상**: 초등 저학년, 영어 입문자
- **Reading Level**: Kindergarten - Grade 1.5
- **어휘량**: 100-300 단어
- **시험 시간**: 45분
- **문항 수**: 총 26문항
  - 읽기: 5문항
  - 어휘: 8문항
  - 회화: 5문항
  - 문법: 7문항 (be동사, 기본 명사)
  - 작문: 1과제 (5문장)

### A1 (Beginner)
- **대상**: 초등 중학년
- **Reading Level**: Grade 1.5 - 3.5
- **어휘량**: 300-700 단어
- **시험 시간**: 50분
- **문항 수**: 총 33문항
  - 읽기: 6문항
  - 어휘: 10문항
  - 회화: 6문항
  - 문법: 10문항 (be동사, 일반동사, 기본 시제)
  - 작문: 1과제 (5-7문장)

### A2 (Elementary)
- **대상**: 초등 고학년, 중1
- **Reading Level**: Grade 3.5 - 5.0
- **어휘량**: 700-1500 단어
- **시험 시간**: 55분
- **문항 수**: 총 38문항
  - 읽기: 8문항
  - 어휘: 12문항
  - 회화: 7문항
  - 문법: 10문항 (현재완료, 미래, 부정사)
  - 작문: 1과제 (이메일 작성, 60-80단어)

### B1 (Intermediate)
- **대상**: 중2-3
- **Reading Level**: Grade 5.0 - 7.0
- **어휘량**: 1500-3000 단어
- **시험 시간**: 60분
- **문항 수**: 총 43문항
  - 읽기: 10문항
  - 어휘: 12문항
  - 회화: 8문항
  - 문법: 12문항 (수동태, 관계사, 가정법)
  - 작문: 1과제 (의견 에세이, 100-120단어)

### B2 (Upper Intermediate)
- **대상**: 고등학생 이상
- **Reading Level**: Grade 7.0+
- **어휘량**: 3000-5000+ 단어
- **시험 시간**: 60분
- **문항 수**: 총 48문항
  - 읽기: 12문항
  - 어휘: 15문항
  - 회화: 8문항
  - 문법: 12문항 (고급 문법 전반)
  - 작문: 1과제 (공식 서한, 150-180단어)

---

## 📝 20개 평가 항목 (루브릭)

### Reading Skills (4항목)
1. **Main Idea Comprehension** - 주제 파악
2. **Detail Comprehension** - 세부 정보 이해
3. **Inference Skills** - 추론 능력
4. **Vocabulary in Context** - 문맥 어휘 이해

### Vocabulary Knowledge (4항목)
5. **Vocabulary Range** - 어휘의 양적 범위
6. **Vocabulary Precision** - 어휘 사용 정확성
7. **Collocations and Idioms** - 연어와 관용 표현
8. **Word Formation** - 파생어 이해

### Grammar Competence (4항목)
9. **Sentence Structure** - 문장 구조
10. **Verb Tenses** - 동사 시제
11. **Subject-Verb Agreement** - 주어-동사 일치
12. **Articles and Determiners** - 관사 사용

### Conversation Ability (4항목)
13. **Pragmatic Appropriacy** - 화용적 적절성
14. **Turn-Taking and Interaction** - 대화 교대
15. **Register and Formality** - 격식 수준
16. **Conversational Strategies** - 대화 전략

### Writing Performance (4항목)
17. **Task Achievement** - 과제 충족도
18. **Coherence and Cohesion** - 응집성
19. **Grammatical Accuracy** - 문법 정확성
20. **Lexical Resource** - 어휘 자원

각 항목은 0-4점으로 평가:
- **0점**: 능력 없음 (Not Demonstrated)
- **1점**: 발달 중 (Developing)
- **2점**: 적절함 (Adequate)
- **3점**: 숙달 (Proficient)
- **4점**: 우수함 (Exemplary)

---

## 🎯 결과 분석 활용법

### 학생용 결과지 구성

1. **Overall Score**
   - 총점/80점
   - 레벨 판정
   - 합격/불합격

2. **20-Criteria Checklist**
   - 각 항목별 점수
   - 체크 여부
   - 레벨 기준 설명

3. **Category Breakdown**
   - 5개 영역별 성취도
   - 시각적 차트
   - 백분율 표시

4. **Strengths (강점)**
   - 잘한 부분 5가지
   - 구체적 능력 명시

5. **Weaknesses (약점)**
   - 보완 필요 부분 5가지
   - 개선 영역 명시

6. **Recommendations (권장사항)**
   - 맞춤형 학습 제안
   - 다음 단계 안내

### 교사/학부모 활용

- **진단 도구**: 정확한 레벨 파악
- **학습 계획**: 약점 보완 중심
- **진도 관리**: 정기적 재평가
- **동기 부여**: 성장 가시화

---

## 🔧 고급 기능

### LLM API 연동 (작문 자동 평가)

```python
import openai

def evaluate_writing_with_llm(writing_sample, level):
    """OpenAI GPT를 사용한 작문 평가"""
    
    prompt = f"""
    Evaluate this CEFR {level} level writing sample based on 4 criteria.
    Score each criterion from 0-4 and provide detailed feedback.
    
    Criteria:
    1. Task Achievement
    2. Coherence and Cohesion
    3. Grammatical Accuracy
    4. Lexical Resource
    
    Writing Sample:
    {writing_sample}
    
    Return format:
    {{
        "W1": {{"score": 3, "feedback": "..."}},
        "W2": {{"score": 2, "feedback": "..."}},
        "W3": {{"score": 3, "feedback": "..."}},
        "W4": {{"score": 3, "feedback": "..."}}
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    return json.loads(response.choices[0].message.content)

# 사용 예시
llm_feedback = evaluate_writing_with_llm(student_writing, 'A2')
```

### 대안: Claude API 사용

```python
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Evaluate this writing: {writing_sample}"
    }]
)
```

### Gemini API 사용

```python
import google.generativeai as genai

genai.configure(api_key="your-api-key")
model = genai.GenerativeModel('gemini-pro')

response = model.generate_content(
    f"Evaluate this writing: {writing_sample}"
)
```

---

## 📊 데이터 분석

### JSON 데이터 구조

```json
{
  "metadata": {
    "level": "A2",
    "generated_date": "2024-11-24T04:48:09",
    "duration": 55,
    "total_questions": 38
  },
  "sections": {
    "reading": {
      "title": "Part 1: Reading Comprehension",
      "questions": [...]
    }
  }
}
```

### 통계 분석

```python
import json
import pandas as pd

# 여러 학생 결과 분석
results = []
for result_file in glob.glob('outputs/results/*.json'):
    with open(result_file) as f:
        results.append(json.load(f))

df = pd.DataFrame(results)

# 평균 점수
print(df['total_score'].mean())

# 레벨별 분포
print(df['determined_level'].value_counts())

# 카테고리별 강점/약점
print(df['category_scores'].apply(pd.Series).mean())
```

---

## 🎓 교육적 활용

### 정기 평가
- **주기**: 분기별 (3개월)
- **목적**: 진도 확인
- **활용**: 레벨 조정

### 배치 평가
- **시기**: 학기 초
- **목적**: 반 편성
- **활용**: 수준별 수업

### 진단 평가
- **필요시**: 수시
- **목적**: 약점 파악
- **활용**: 보충 수업

---

## ✅ 체크리스트

### 시험 전
- [ ] 레벨 선정
- [ ] 시험지 출력
- [ ] 답안지 준비
- [ ] 시간 확인 (45-60분)

### 시험 중
- [ ] 지시사항 설명
- [ ] 시간 관리
- [ ] 질문 대응

### 시험 후
- [ ] 객관식 채점
- [ ] 작문 평가 (루브릭 또는 LLM)
- [ ] 결과지 생성
- [ ] 학생 피드백

---

## 📞 문의 및 지원

### 기술 문의
- 시스템 오류
- 파일 생성 실패
- API 연동 문제

### 교육 문의
- CEFR 기준 해석
- 루브릭 적용
- 결과 해석

---

## 🔄 업데이트 계획

### v1.1 (예정)
- [ ] PDF 직접 생성
- [ ] 온라인 시험 지원
- [ ] 실시간 채점

### v1.2 (예정)
- [ ] 듣기 영역 추가
- [ ] 말하기 평가
- [ ] 적응형 테스트

---

**과학적이고 공정한 영어 능력 평가로 학생의 성장을 돕습니다.** 🎓📈
