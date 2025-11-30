# CEFR-Based English Level Test System

## 🎯 Overview

국제 공인 기준(CEFR: Common European Framework of Reference for Languages)에 맞춘 과학적이고 체계적인 영어 레벨 테스트 시스템입니다. 학생의 영어 능력을 객관적으로 평가하고, 20개 항목의 상세한 루브릭을 통해 강점과 약점을 분석합니다.

---

## 📊 System Features

### 1. **5-Level CEFR Test Generation**
- **PRE-A1**: Basic beginner (K-1.5 grade reading)
- **A1**: Beginner (1.5-3.5 grade reading)
- **A2**: Elementary (3.5-5.0 grade reading)
- **B1**: Intermediate (5.0-7.0 grade reading)
- **B2**: Upper Intermediate (7.0+ grade reading)

### 2. **Comprehensive Assessment Sections**
각 레벨의 시험은 다음 5개 영역으로 구성:

#### 📖 Part 1: Reading Comprehension
- CEFR 레벨에 맞춘 authentic texts
- Main idea, detail comprehension, inference questions
- 레벨별 3-12문항

#### 📚 Part 2: Vocabulary
- Context-based vocabulary questions
- Collocations, word formation, precision
- 레벨별 8-15문항

#### 💬 Part 3: Conversation
- Pragmatic appropriacy assessment
- Response selection in dialogues
- 레벨별 5-8문항

#### ✏️ Part 4: Grammar
- Level-appropriate grammar points
- Sentence structure, tense, agreement
- 레벨별 7-12문항

#### 📝 Part 5: Writing
- Task-based writing assessment
- Rubric-scored (0-4 scale)
- 레벨별 맞춤형 과제

### 3. **Scientific Item Design Principles**

모든 문항은 다음 원칙을 준수:

✅ **Choice Length Balance Protocol v2.0**
- 정답과 오답의 길이 균형 유지
- 구조적 편향 제거
- 정답이 항상 최장/최단이 아님

✅ **Answer Distribution Balance**
- A, B, C, D 선택지 분포 균등
- 예측 가능성 제거
- 통계적 신뢰도 보장

✅ **Evidence-Based Difficulty Setting**
- 예상 정답률 사전 설정
- 변별도 조절
- 매력적 오답 설계

### 4. **20-Criteria Assessment Rubric**

각 학생은 20개 항목으로 평가:

**Reading (4 criteria)**
- R1: Main Idea Comprehension
- R2: Detail Comprehension
- R3: Inference Skills
- R4: Vocabulary in Context

**Vocabulary (4 criteria)**
- V1: Vocabulary Range
- V2: Vocabulary Precision
- V3: Collocations and Idioms
- V4: Word Formation

**Grammar (4 criteria)**
- G1: Sentence Structure
- G2: Verb Tenses
- G3: Subject-Verb Agreement
- G4: Articles and Determiners

**Conversation (4 criteria)**
- C1: Pragmatic Appropriacy
- C2: Turn-Taking and Interaction
- C3: Register and Formality
- C4: Conversational Strategies

**Writing (4 criteria)**
- W1: Task Achievement
- W2: Coherence and Cohesion
- W3: Grammatical Accuracy
- W4: Lexical Resource

각 항목은 0-4점 척도로 평가:
- **0**: Not Demonstrated
- **1**: Developing
- **2**: Adequate
- **3**: Proficient
- **4**: Exemplary

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/your-org/cefr-level-test.git
cd cefr-level-test
pip install -r requirements.txt
```

### Deploy to GitHub Pages

1. GitHub 저장소에서 `Settings > Pages`에 들어가 Source 를 **GitHub Actions** 로 설정합니다.
2. 기본 브랜치 이름이 `main`이 아니라면 `.github/workflows/pages.yml` 의 `branches: [main]` 부분을 브랜치명으로 바꿉니다.
3. 저장소에 푸시하면 워크플로우가 실행되어 샘플 HTML/PDF를 생성하고 GitHub Pages에 자동 배포합니다. 배포 결과 URL은 Actions 로그와 Pages 설정 화면에서 확인할 수 있습니다.

### Usage

#### 1. Generate a Single Level Test

```bash
python3 main.py --mode generate --level A2 --output-dir ./outputs/
```

#### 2. Generate All Level Tests

```bash
python3 main.py --mode batch --output-dir ./outputs/
```

#### 3. Evaluate a Student Test

```python
from main import CEFRTestSystem

system = CEFRTestSystem(output_dir='./outputs')

# 학생 답안
student_answers = {
    'R1': 'A', 'R2': 'B', 'R3': 'C',
    'V1': 'A', 'V2': 'B', 'V3': 'C',
    'G1': 'A', 'G2': 'B', 'G3': 'C',
    'C1': 'A', 'C2': 'B'
}

# 정답
correct_answers = {
    'R1': 'A', 'R2': 'C', 'R3': 'C',
    'V1': 'A', 'V2': 'B', 'V3': 'D',
    'G1': 'B', 'G2': 'B', 'G3': 'C',
    'C1': 'A', 'C2': 'C'
}

# 평가 실행
result_file = system.evaluate_test(
    level='A2',
    student_name='John Doe',
    student_answers=student_answers,
    correct_answers=correct_answers,
    writing_sample="Your writing sample here...",
    llm_feedback={'W1': {'score': 3, 'feedback': '...'}}
)
```

---

## 📁 Output Files

### 시험지 (Test Paper)
- **Format**: HTML (프린트 가능)
- **Location**: `outputs/tests/`
- **Content**: 
  - Student information section
  - All test sections with questions
  - Answer sheets
  - Writing space

### 정답지 (Answer Key)
- **Format**: HTML
- **Location**: `outputs/answer_keys/`
- **Content**:
  - Quick reference answer grid
  - Detailed explanations
  - Difficulty indicators
  - Skill tags

### 결과지 (Result Report)
- **Format**: HTML + PDF
- **Location**: `outputs/results/`
- **Content**:
  - Overall score and level determination
  - 20-criteria checklist with scores
  - Category breakdown chart
  - Strengths and weaknesses
  - Learning recommendations

### 데이터 (Test Data)
- **Format**: JSON
- **Location**: `outputs/tests/`
- **Content**: Structured test data for analysis

---

## 🔧 Customization

### Adjust Question Counts

```python
custom_counts = {
    'reading': 10,
    'vocabulary': 15,
    'conversation': 10,
    'grammar': 15,
    'writing': 1
}

system.generate_test(level='B1', question_counts=custom_counts)
```

### Integrate LLM Feedback

작문 평가를 위해 LLM API 연동:

```python
# Example with OpenAI API
import openai

def get_writing_feedback(writing_sample, level):
    prompt = f"""
    Evaluate this {level} level writing sample using these 4 criteria:
    1. Task Achievement (0-4)
    2. Coherence and Cohesion (0-4)
    3. Grammatical Accuracy (0-4)
    4. Lexical Resource (0-4)
    
    Writing: {writing_sample}
    
    Return JSON format with scores and feedback.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return json.loads(response.choices[0].message.content)

# Use in evaluation
llm_feedback = get_writing_feedback(writing_sample, 'A2')
system.evaluate_test(..., llm_feedback=llm_feedback)
```

---

## 📈 Scoring System

### Objective Sections
- **Multiple Choice**: 1 point per question
- **Automatic scoring**
- **Answer distribution analysis**

### Writing Section
- **Rubric-based**: 0-4 per criterion (4 criteria)
- **LLM or human evaluation**
- **Detailed feedback generation**

### Total Score Calculation

```
Total Score = Σ(Category Score × Weight)

Weights:
- Reading: 30%
- Vocabulary: 20%
- Grammar: 20%
- Conversation: 15%
- Writing: 15%

Maximum: 80 points
```

### Level Determination

| Score Range | Level | Pass Threshold |
|-------------|-------|----------------|
| 0-30 | PRE-A1 | 24 |
| 31-45 | A1 | 36 |
| 46-58 | A2 | 48 |
| 59-70 | B1 | 60 |
| 71-80 | B2 | 72 |

---

## 🎨 HTML Output Features

### Responsive Design
- Mobile-friendly layout
- Print-optimized
- Professional styling

### Interactive Elements
- Radio buttons for answer selection
- Visual score charts
- Color-coded feedback

### Accessibility
- Clear typography
- High contrast ratios
- Semantic HTML structure

---

## 🔬 Psychometric Quality

### Validity
- **Content Validity**: Aligned with CEFR descriptors
- **Construct Validity**: Measures intended skills
- **Face Validity**: Professionally designed items

### Reliability
- **Internal Consistency**: Balanced difficulty
- **Test-Retest**: Consistent level determination
- **Inter-Rater**: Standardized rubrics

### Fairness
- **No Cultural Bias**: Neutral content
- **Balanced Distractors**: Scientific design
- **Equal Opportunity**: Clear instructions

---

## 📚 Reference Materials

### CEFR Official Documents
- [Council of Europe - CEFR](https://www.coe.int/en/web/common-european-framework-reference-languages)
- [CEFR Descriptors](https://www.coe.int/en/web/common-european-framework-reference-languages/table-1-cefr-3.3-common-reference-levels-global-scale)

### Lexile Framework
- Reading level alignment with US grade levels
- [Lexile Framework](https://lexile.com/)

### Assessment Standards
- ISO 29990: Learning services quality
- AERA Standards for Educational Testing

---

## 🛠️ Technical Stack

- **Language**: Python 3.8+
- **Output**: HTML5, CSS3
- **Data Format**: JSON
- **PDF Generation**: ReportLab (bundled; no headless browser needed)
- **LLM Integration**: OpenAI API, Anthropic API (optional)

---

## 📝 License

© 2024 CEFR Level Testing System. All rights reserved.

---

## 💬 Support

For questions or support:
- Review the documentation
- Check example outputs
- Consult CEFR reference materials

---

## 🔄 Version History

### v1.0.0 (2024-11-24)
- Initial release
- 5-level test generation (PRE-A1 to B2)
- 20-criteria assessment rubric
- HTML/PDF output support
- Comprehensive result reports

---

**Built with scientific rigor and educational expertise. 🎓**
