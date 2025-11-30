from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from html_generator import (
    export_result_pdf,
    generate_result_charts,
    render_answer_key,
    render_result_report,
    render_test_paper,
)
from rubric_system import (
    ASSESSMENT_CRITERIA,
    criteria_from_category,
    determine_level,
    recommend_from_categories,
)
from test_generator import LEVEL_CONFIG, export_test_data, generate_test_data, level_names


class CEFRTestSystem:
    def __init__(self, output_dir: str = "outputs") -> None:
        self.output_dir = Path(output_dir)
        self.paths = {
            "tests": self.output_dir / "tests",
            "answer_keys": self.output_dir / "answer_keys",
            "results": self.output_dir / "results",
        }
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        ts = ts.replace("+00:00", "Z")
        return ts.replace(":", "-")

    def generate_test(
        self,
        level: str,
        question_counts: Optional[Dict[str, int]] = None,
        use_llm: bool = False,
        llm_provider: str = "openai",
        llm_model: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict:
        data = generate_test_data(level, question_counts, use_llm=use_llm, llm_provider=llm_provider, llm_model=llm_model, context=context)
        ts = self._timestamp()
        base_name = f"{level}_{ts}"

        test_html = render_test_paper(data)
        answer_html = render_answer_key(data)

        test_path = self.paths["tests"] / f"test_paper_{base_name}.html"
        answer_path = self.paths["answer_keys"] / f"answer_key_{base_name}.html"
        data_path = self.paths["tests"] / f"test_data_{base_name}.json"

        test_path.write_text(test_html, encoding="utf-8")
        answer_path.write_text(answer_html, encoding="utf-8")
        export_test_data(data, data_path)

        return {
            "metadata": data["metadata"],
            "answer_key": data["answer_key"],
            "test_data": data,
            "test_file": str(test_path),
            "answer_key_file": str(answer_path),
            "data_file": str(data_path),
        }

    def evaluate_test(
        self,
        level: str,
        student_name: str,
        student_answers: Dict[str, str],
        correct_answers: Dict[str, str],
        writing_sample: Optional[str] = None,
        llm_feedback: Optional[Dict] = None,
        test_metadata: Optional[Dict] = None,
    ) -> Dict:
        ts = self._timestamp()
        safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", student_name).strip("_") or "student"
        meta = {
            "generated_at": ts,
            "level": level,
            "writing_sample": writing_sample or "",
        }
        category_weights = {
            "reading": 24.0,  # 30% of 80
            "vocabulary": 16.0,  # 20%
            "grammar": 16.0,  # 20%
            "conversation": 12.0,  # 15%
            "writing": 12.0,  # 15%
        }

        prefix_map = {
            "reading": ("R", ["R1", "R2", "R3", "R4"]),
            "vocabulary": ("V", ["V1", "V2", "V3", "V4"]),
            "grammar": ("G", ["G1", "G2", "G3", "G4"]),
            "conversation": ("C", ["C1", "C2", "C3", "C4"]),
        }

        category_scores: Dict[str, float] = {}
        criteria_scores: Dict[str, int] = {}
        total_score = 0.0

        for cat, (prefix, criteria_codes) in prefix_map.items():
            qids = [q for q in correct_answers if q.startswith(prefix)]
            total = len(qids)
            correct = sum(1 for q in qids if student_answers.get(q) == correct_answers.get(q))
            proportion = (correct / total) if total else 0.0
            score = proportion * category_weights[cat]
            category_scores[cat] = score
            total_score += score
            crit_value = criteria_from_category(proportion)
            for code in criteria_codes:
                criteria_scores[code] = crit_value

        # Writing: use provided LLM feedback if available, otherwise neutral midpoint
        writing_scores = llm_feedback or {}
        writing_total = sum(item.get("score", 0) for item in writing_scores.values()) if writing_scores else 8  # midpoint 2/4 * 4
        writing_max = 16  # 4 criteria * 4
        writing_proportion = writing_total / writing_max if writing_max else 0
        writing_score = writing_proportion * category_weights["writing"]
        category_scores["writing"] = writing_score
        total_score += writing_score
        for code in ["W1", "W2", "W3", "W4"]:
            score_val = writing_scores.get(code, {}).get("score", 2)
            criteria_scores[code] = int(score_val)

        determined_level = determine_level(total_score)

        strengths = [f"{c}: {ASSESSMENT_CRITERIA[c]['criterion']}" for c, _ in sorted(criteria_scores.items(), key=lambda kv: kv[1], reverse=True)[:5]]
        weaknesses = [f"{c}: {ASSESSMENT_CRITERIA[c]['criterion']}" for c, _ in sorted(criteria_scores.items(), key=lambda kv: kv[1])[:5]]
        recommendations = recommend_from_categories(category_scores)

        result_data = {
            "student_name": student_name,
            "level": level,
            "total_score": total_score,
            "determined_level": determined_level,
            "category_scores": category_scores,
            "category_weights": category_weights,
            "criteria_scores": criteria_scores,
            "criteria_meta": ASSESSMENT_CRITERIA,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "metadata": meta,
            "test_metadata": test_metadata or {},
        }

        chart_images = generate_result_charts(result_data)
        result_html = render_result_report(result_data, chart_images)
        result_path = self.paths["results"] / f"result_{safe_name}_{level}_{ts}.html"
        result_path.write_text(result_html, encoding="utf-8")
        pdf_path = self.paths["results"] / f"result_{safe_name}_{level}_{ts}.pdf"
        export_result_pdf(result_data, pdf_path, chart_images)
        result_data["result_file"] = str(result_path)
        result_data["result_pdf"] = str(pdf_path)
        return result_data


def _parse_question_counts(raw: Optional[str]) -> Optional[Dict[str, int]]:
    if not raw:
        return None
    try:
        return {k: int(v) for k, v in json.loads(raw).items()}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON for --question-counts: {exc}") from exc


def cli() -> None:
    parser = argparse.ArgumentParser(description="CEFR Level Test System")
    parser.add_argument("--mode", required=True, choices=["generate", "batch", "sample", "gui"], help="generate|batch|sample|gui")
    parser.add_argument("--level", help="CEFR level (e.g., A2)")
    parser.add_argument("--output-dir", default="outputs", help="Output directory (default: outputs)")
    parser.add_argument("--question-counts", help="Override counts as JSON, e.g. '{\"reading\":10}'")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM to draft questions (requires API key/env)")
    parser.add_argument("--llm-provider", default="openai", help="LLM provider: openai|anthropic|gemini")
    parser.add_argument("--llm-model", help="Override model name for the provider")
    args = parser.parse_args()

    system = CEFRTestSystem(output_dir=args.output_dir)

    if args.mode == "generate":
        if not args.level:
            raise SystemExit("--level is required for generate mode")
        counts = _parse_question_counts(args.question_counts)
        result = system.generate_test(
            args.level,
            question_counts=counts,
            use_llm=args.use_llm,
            llm_provider=args.llm_provider,
            llm_model=args.llm_model,
        )
        print(f"[ok] Generated test for {args.level}")
        print(f"  Test paper:     {result['test_file']}")
        print(f"  Answer key:     {result['answer_key_file']}")
        print(f"  Test data JSON: {result['data_file']}")
    elif args.mode == "batch":
        for level in level_names():
            result = system.generate_test(
                level,
                use_llm=args.use_llm,
                llm_provider=args.llm_provider,
                llm_model=args.llm_model,
            )
            print(f"[ok] {level}: {result['test_file']}")
    elif args.mode == "sample":
        from generate_sample_result import run_sample

        run_sample(system)
    elif args.mode == "gui":
        from gui_app import run_gui

        run_gui(default_output=args.output_dir)
    else:
        raise SystemExit(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    cli()
