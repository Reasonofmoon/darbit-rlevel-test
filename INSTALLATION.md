# CEFR 레벨 테스트 시스템 - 설치 및 실행 가이드

이 문서는 프로젝트를 로컬 환경에 설치하고 바로 시험지/정답지/결과지를 생성할 수 있도록 단계별로 정리했습니다. 예시는 PowerShell(Windows)과 bash(macOS/Linux) 모두 제공하며, 기본 출력 경로는 `./outputs/` 입니다.

---

## ✅ 사전 요구사항
- OS: Windows 10+, macOS, 또는 최신 Linux
- Python 3.8 이상 (권장: 3.10+), `pip` 사용 가능
- 브라우저(HTML 열기용) 또는 WeasyPrint 등 PDF 변환 도구
- 선택: OpenAI/Anthropic/Gemini API 키 (작문 자동 평가용)
- 선택: `git` (저장소 클론용)

> 프로젝트 루트에 `main.py`, `test_generator.py` 등 핵심 스크립트가 포함된 배포본이 준비되어 있어야 합니다. 문서만 보유한 경우 배포 ZIP 또는 소스 저장소를 내려받으세요.

---

## 📦 디렉토리 구조
```
<project-root>/
├── main.py                   # 메인 실행 파일
├── test_generator.py         # 시험지 생성 엔진
├── rubric_system.py          # 평가 루브릭
├── html_generator.py         # HTML/PDF 생성기
├── generate_sample_result.py # 샘플 결과 생성
├── README.md                 # 시스템 개요
├── USER_GUIDE.md             # 사용자 가이드
└── INSTALLATION.md           # 설치 안내 (본 문서)

outputs/                      # 기본 출력 경로 (직접 생성)
├── tests/
├── answer_keys/
└── results/
```

---

## 🛠️ 설치 절차
아래는 PowerShell 기준 예시입니다. macOS/Linux에서는 `${VAR}` 대신 `$VAR`로, 경로 구분자는 `/`로 변경해 실행하세요.

1) 프로젝트 내려받기  
```pwsh
git clone <repo-url> cefr-level-test
cd cefr-level-test
```

2) (선택) 가상환경 생성  
```pwsh
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

3) 의존성 설치  
- 핵심 동작은 표준 라이브러리로 동작합니다.  
- PDF/데이터 분석/LLM 평가를 쓰려면 추가 패키지를 설치하세요.
```pwsh
# 필요한 것만 선택적으로 설치 (LLM 사용 시 openai/anthropic/google-generativeai 포함)
pip install weasyprint pandas matplotlib openai anthropic google-generativeai
```

4) 출력 디렉토리 준비  
```pwsh
New-Item -ItemType Directory -Force -Path outputs, outputs/tests, outputs/answer_keys, outputs/results > $null
```

5) (선택) API 키 환경 변수 설정  
```pwsh
$env:OPENAI_API_KEY="sk-..."
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:GEMINI_API_KEY="..."
```

6) 설치 확인 (A2 시험지 생성)  
```pwsh
python main.py --mode generate --level A2 --output-dir .\outputs
```
완료 후 `outputs/tests/`와 `outputs/answer_keys/`에 HTML이 생성되면 정상입니다.

---

## 🚀 실행 예시
- 모든 레벨 시험지/정답지 생성  
```pwsh
python main.py --mode batch --output-dir .\outputs
```

- 특정 레벨만 생성 (예: A2)  
```pwsh
python main.py --mode generate --level A2 --output-dir .\outputs
```

- 샘플 시험+결과 한 번에 생성 (A2, John Smith)  
```pwsh
python main.py --mode sample --output-dir .\outputs
```

- GUI로 레벨/문항수/LLM 설정 후 생성  
```pwsh
python main.py --mode gui --output-dir .\outputs
```

- 샘플 결과지 생성  
```pwsh
python generate_sample_result.py --output-dir .\outputs
```

---

## 📂 생성물 활용
- 시험지: `outputs/tests/test_paper_[LEVEL]_[TIMESTAMP].html`  
  - 브라우저로 열기 → `Ctrl/Cmd + P` → PDF로 저장 → 배포
- 정답지: `outputs/answer_keys/answer_key_[LEVEL]_[TIMESTAMP].html`  
  - 채점용, 난이도/해설 포함
- 결과지: `outputs/results/result_[NAME]_[LEVEL]_[TIMESTAMP].html`  
  - 총점, 레벨 판정, 20개 항목 체크리스트, 강·약점/권장사항

> LLM 문항 생성: `--use-llm` 플래그(또는 GUI 체크)를 켜고 `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` 중 하나를 환경 변수로 설정하세요. 설치가 안 된 패키지나 키가 없으면 자동으로 템플릿 기반 문항으로 폴백합니다.

---

## 🔧 커스터마이징 요약
- 문항 수 조정: `system.generate_test(level, question_counts=...)`
- 루브릭 수정: `rubric_system.py`의 `ASSESSMENT_CRITERIA` 업데이트
- LLM 연동: 환경 변수로 API 키 설정 후 `llm_feedback` 인자로 전달
- 데이터 분석: `outputs/tests/test_data_*.json`을 `pandas`/`matplotlib`로 처리

---

## ⚠️ 자주 묻는 문제
- **파일이 생성되지 않음**: 출력 경로 권한/존재 여부 확인 → `outputs/` 하위 폴더를 직접 생성 후 다시 실행  
- **HTML이 깨져 보임**: UTF-8 지원 브라우저(Chrome/Firefox) 사용  
- **PDF 변환 실패**: `pip install weasyprint` 후 다시 시도하거나 브라우저 인쇄 → PDF 사용  
- **LLM API 오류**: API 키 유효성/쿼터 확인, 요청 속도 제한 확인

---

## 🎯 다음 단계
1. `python main.py --mode batch`로 전체 레벨 시험지 생성 후 샘플 출력 검토  
2. 실제 학생 답안을 입력해 결과지를 생성하고 루브릭 적합성 확인  
3. 필요 시 루브릭/문항 수 조정 및 PDF 자동화(WeasyPrint) 적용  
4. 결과 JSON을 수집해 반 편성·진단용 통계 대시보드로 확장
