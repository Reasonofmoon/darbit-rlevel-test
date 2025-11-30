from __future__ import annotations

import itertools
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from llm_adapter import LLMNotConfigured, llm_generate_questions

# 기본 레벨 설정: 시험 시간과 권장 문항 수
LEVEL_CONFIG: Dict[str, Dict[str, int]] = {
    "PRE-A1": {"duration": 45, "reading": 5, "vocabulary": 8, "conversation": 5, "grammar": 7, "writing": 1},
    "A1": {"duration": 50, "reading": 6, "vocabulary": 10, "conversation": 6, "grammar": 10, "writing": 1},
    "A2": {"duration": 55, "reading": 8, "vocabulary": 12, "conversation": 7, "grammar": 10, "writing": 1},
    "B1": {"duration": 60, "reading": 10, "vocabulary": 12, "conversation": 8, "grammar": 12, "writing": 1},
    "B2": {"duration": 60, "reading": 12, "vocabulary": 15, "conversation": 8, "grammar": 12, "writing": 1},
}

SECTION_LABELS = {
    "reading": ("R", "Part 1: Reading Comprehension"),
    "vocabulary": ("V", "Part 2: Vocabulary"),
    "conversation": ("C", "Part 3: Conversation"),
    "grammar": ("G", "Part 4: Grammar"),
    "writing": ("W", "Part 5: Writing"),
}

# 간단한 섹션별 지문/문장 템플릿
SECTION_STEMS = {
    "reading": "Read the short passage and choose the best answer.",
    "vocabulary": "Choose the word that best completes the sentence.",
    "conversation": "Select the most appropriate reply for the situation.",
    "grammar": "Choose the grammatically correct option.",
    "writing": "Write a response following the prompt.",
}


def _correct_choice(idx: int) -> str:
    """A, B, C, D 순환으로 정답 분포 균형을 맞춘다."""
    return "ABCD"[idx % 4]


def _question_text(section: str, level: str, idx: int) -> Tuple[str, List[Dict[str, str]], str]:
    """섹션별 예시 질문과 선택지를 생성한다."""
    prompt = SECTION_STEMS.get(section, "Choose the best option.")
    base = f"[{level}] {prompt} (Q{idx + 1})"
    options = [
        {"label": "A", "text": f"Option A for {section} Q{idx + 1}"},
        {"label": "B", "text": f"Option B for {section} Q{idx + 1}"},
        {"label": "C", "text": f"Option C for {section} Q{idx + 1}"},
        {"label": "D", "text": f"Option D for {section} Q{idx + 1}"},
    ]
    correct = _correct_choice(idx)
    return base, options, correct


def _writing_prompt(level: str) -> str:
    return (
        f"Write an email for the {level} level audience. "
        "State your purpose clearly, include at least two supporting details, and close politely."
    )


def generate_test_data(
    level: str,
    question_counts: Optional[Dict[str, int]] = None,
    use_llm: bool = False,
    llm_provider: str = "openai",
    llm_model: Optional[str] = None,
    context: Optional[str] = None,
) -> Dict:
    """
    레벨별 시험 데이터를 생성한다.
    반환 값은 HTML/결과 생성에 바로 사용할 수 있는 구조화된 dict이다.
    """
    if level not in LEVEL_CONFIG:
        raise ValueError(f"Unknown level: {level}")

    config = LEVEL_CONFIG[level].copy()
    question_counts = question_counts or {}
    config.update({k: v for k, v in question_counts.items() if k in config})

    sections: Dict[str, Dict] = {}
    answer_key: Dict[str, str] = {}
    total_questions = 0

    llm_status = {"enabled": use_llm, "provider": llm_provider, "model": llm_model, "fallback": False, "error": ""}

    for section in ["reading", "vocabulary", "conversation", "grammar"]:
        prefix, title = SECTION_LABELS[section]
        count = config[section]
        questions = []

        llm_items: List[Dict] = []
        if use_llm:
            try:
                llm_items = llm_generate_questions(llm_provider, level, section, count, model=llm_model, context=context)
            except (LLMNotConfigured, Exception) as exc:  # fallback to templates on any failure
                llm_status["fallback"] = True
                llm_status["error"] = str(exc)
                llm_items = []

        if llm_items:
            for idx, item in enumerate(llm_items[:count]):
                qid = f"{prefix}{idx + 1}"
                questions.append(
                    {
                        "id": qid,
                        "text": item.get("text", ""),
                        "options": item.get("options", []),
                        "correct": item.get("correct", "A"),
                        "section": section,
                    }
                )
                answer_key[qid] = item.get("correct", "A")
        else:
            for idx in range(count):
                text, options, correct = _question_text(section, level, idx)
                qid = f"{prefix}{idx + 1}"
                questions.append({"id": qid, "text": text, "options": options, "correct": correct, "section": section})
                answer_key[qid] = correct

        sections[section] = {"title": title, "questions": questions}
        total_questions += count

    # Writing 섹션
    w_prefix, w_title = SECTION_LABELS["writing"]
    writing_prompt = _writing_prompt(level)
    writing_question = {"id": f"{w_prefix}1", "prompt": writing_prompt, "section": "writing"}
    sections["writing"] = {"title": w_title, "questions": [writing_question]}
    total_questions += config["writing"]

    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    generated_at = ts.replace("+00:00", "Z")
    metadata = {
        "level": level,
        "duration": config["duration"],
        "generated_at": generated_at,
        "total_questions": total_questions,
        "llm": llm_status,
    }

    return {"metadata": metadata, "sections": sections, "answer_key": answer_key}


def export_test_data(data: Dict, path) -> None:
    """JSON 포맷으로 시험 데이터를 저장한다."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def level_names() -> List[str]:
    return list(LEVEL_CONFIG.keys())


__all__ = ["generate_test_data", "export_test_data", "level_names", "LEVEL_CONFIG", "SECTION_LABELS"]
