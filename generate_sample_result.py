from __future__ import annotations

import random
from typing import Dict, Optional

from main import CEFRTestSystem


def _sample_student_answers(answer_key: Dict[str, str], rng: random.Random) -> Dict[str, str]:
    answers: Dict[str, str] = {}
    for qid, correct in answer_key.items():
        # 75% 정답, 25% 오답으로 샘플 생성
        if rng.random() > 0.25:
            answers[qid] = correct
        else:
            distractors = [c for c in "ABCD" if c != correct]
            answers[qid] = rng.choice(distractors)
    return answers


def run_sample(system: Optional[CEFRTestSystem] = None):
    rng = random.Random(42)
    system = system or CEFRTestSystem()

    generated = system.generate_test(level="A2")
    answer_key = generated["answer_key"]

    student_answers = _sample_student_answers(answer_key, rng)
    writing_sample = (
        "Dear Teacher,\n"
        "I am writing to thank you for your help this semester. "
        "I improved my reading and vocabulary, but I want to practice conversation more.\n"
        "Sincerely,\nJohn"
    )
    llm_feedback = {
        "W1": {"score": 3, "feedback": "Task achieved with clear purpose."},
        "W2": {"score": 3, "feedback": "Logical flow with basic transitions."},
        "W3": {"score": 2, "feedback": "Some grammar slips but meaning is clear."},
        "W4": {"score": 3, "feedback": "Vocabulary is varied enough for the level."},
    }

    result = system.evaluate_test(
        level="A2",
        student_name="John Smith",
        student_answers=student_answers,
        correct_answers=answer_key,
        writing_sample=writing_sample,
        llm_feedback=llm_feedback,
        test_metadata=generated["metadata"],
    )

    print("[ok] Sample A2 test, answer key, and result have been generated.")
    print(f"  Test paper: {generated['test_file']}")
    print(f"  Answer key: {generated['answer_key_file']}")
    print(f"  Result HTML: {result['result_file']}")
    print(f"  Result PDF:  {result.get('result_pdf','-')}")
    return result


if __name__ == "__main__":
    run_sample()
