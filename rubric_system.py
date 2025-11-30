from __future__ import annotations

from typing import Dict, List

ASSESSMENT_CRITERIA: Dict[str, Dict[str, str]] = {
    "R1": {"criterion": "Main Idea Comprehension", "description": "Identify the main idea of a short text."},
    "R2": {"criterion": "Detail Comprehension", "description": "Locate key details within a passage."},
    "R3": {"criterion": "Inference Skills", "description": "Infer meaning or intent from context."},
    "R4": {"criterion": "Vocabulary in Context", "description": "Interpret vocabulary using textual clues."},
    "V1": {"criterion": "Vocabulary Range", "description": "Use a range of level-appropriate words."},
    "V2": {"criterion": "Vocabulary Precision", "description": "Choose precise words for meaning."},
    "V3": {"criterion": "Collocations and Idioms", "description": "Understand common collocations and idioms."},
    "V4": {"criterion": "Word Formation", "description": "Recognize derived forms and affixes."},
    "G1": {"criterion": "Sentence Structure", "description": "Construct well-formed sentences."},
    "G2": {"criterion": "Verb Tenses", "description": "Use tenses appropriate to context."},
    "G3": {"criterion": "Subject-Verb Agreement", "description": "Maintain agreement across subjects and verbs."},
    "G4": {"criterion": "Articles and Determiners", "description": "Use articles and determiners accurately."},
    "C1": {"criterion": "Pragmatic Appropriacy", "description": "Select responses suited to context."},
    "C2": {"criterion": "Turn-Taking and Interaction", "description": "Manage turns in dialogue politely."},
    "C3": {"criterion": "Register and Formality", "description": "Match register to the situation."},
    "C4": {"criterion": "Conversational Strategies", "description": "Use repair and clarification strategies."},
    "W1": {"criterion": "Task Achievement", "description": "Address the prompt fully."},
    "W2": {"criterion": "Coherence and Cohesion", "description": "Organize ideas logically with linking."},
    "W3": {"criterion": "Grammatical Accuracy", "description": "Maintain grammatical control in writing."},
    "W4": {"criterion": "Lexical Resource", "description": "Use varied and accurate vocabulary in writing."},
}

LEVEL_THRESHOLDS = [
    ("B2", 71),
    ("B1", 59),
    ("A2", 46),
    ("A1", 31),
    ("PRE-A1", 0),
]


def determine_level(total_score: float) -> str:
    """총점을 기준으로 CEFR 레벨을 판정한다."""
    for level, cutoff in LEVEL_THRESHOLDS:
        if total_score >= cutoff:
            return level
    return "PRE-A1"


def criteria_from_category(proportion: float) -> int:
    """카테고리 정답률을 0-4 루브릭 점수로 스케일한다."""
    proportion = max(0.0, min(1.0, proportion))
    return int(round(proportion * 4))


def recommend_from_categories(category_scores: Dict[str, float]) -> List[str]:
    """카테고리별 점수를 기반으로 간단한 개선 권장사항을 생성한다."""
    recommendations: List[str] = []
    low_categories = sorted(category_scores.items(), key=lambda kv: kv[1])[:3]
    for name, score in low_categories:
        if name == "writing":
            recommendations.append("Practice timed writing with 2-3 clear paragraphs and revise for grammar.")
        elif name == "reading":
            recommendations.append("Read short level-appropriate texts daily and summarize main ideas.")
        elif name == "vocabulary":
            recommendations.append("Grow vocabulary with spaced repetition and sentence-level usage.")
        elif name == "grammar":
            recommendations.append("Review target tenses and agreement; rewrite errors you spot.")
        elif name == "conversation":
            recommendations.append("Role-play dialogues focusing on polite, concise replies.")
    return recommendations


__all__ = ["ASSESSMENT_CRITERIA", "LEVEL_THRESHOLDS", "determine_level", "criteria_from_category", "recommend_from_categories"]
