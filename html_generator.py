from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _base_css() -> str:
    return """
    <style>
      :root {
        --bg: #0f172a;
        --card: #111827;
        --ink: #e5e7eb;
        --muted: #9ca3af;
        --accent: #38bdf8;
      }
      * { box-sizing: border-box; }
      body { font-family: "Segoe UI", Arial, sans-serif; background: var(--bg); color: var(--ink); margin: 0; padding: 24px; }
      h1, h2, h3 { margin: 0 0 12px; }
      .card { background: var(--card); border: 1px solid #1f2937; border-radius: 12px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); }
      .meta { display: flex; gap: 16px; flex-wrap: wrap; color: var(--muted); font-size: 14px; }
      .question { margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid #1f2937; }
      .question:last-child { border-bottom: none; }
      .options { margin-left: 12px; }
      .option { margin: 4px 0; }
      .tag { display: inline-block; padding: 4px 10px; border-radius: 999px; background: rgba(56,189,248,0.15); color: var(--accent); font-weight: 600; font-size: 12px; }
      table { width: 100%; border-collapse: collapse; color: var(--ink); }
      th, td { padding: 8px 10px; border-bottom: 1px solid #1f2937; text-align: left; }
      th { color: var(--muted); font-weight: 600; }
      .pill { padding: 4px 10px; border-radius: 999px; background: rgba(255,255,255,0.07); }
      .highlight { color: var(--accent); font-weight: 700; }
      .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
      .list-item { padding: 10px 12px; border-radius: 8px; background: rgba(255,255,255,0.05); }
      .muted { color: var(--muted); }
      .charts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
      .chart { background: rgba(255,255,255,0.03); border: 1px solid #1f2937; border-radius: 12px; padding: 10px; }
      .chart img { width: 100%; display: block; border-radius: 8px; }
      .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }
      .stat { padding: 10px 12px; border-radius: 10px; background: rgba(56,189,248,0.08); border: 1px solid rgba(56,189,248,0.25); }
      .stat .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
      .stat .value { font-size: 20px; font-weight: 700; }
    </style>
    """


def _style_axes(fig, ax):
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#ffffff")
    for spine in ax.spines.values():
        spine.set_color("#d1d5db")
    ax.tick_params(colors="#111827", labelcolor="#111827")
    ax.yaxis.label.set_color("#4b5563")
    ax.xaxis.label.set_color("#4b5563")
    ax.title.set_color("#111827")


def _fig_to_data_url(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{data}"


def _category_bar_chart(result: Dict) -> str:
    labels = list(result["category_scores"].keys())
    scores = [result["category_scores"][k] for k in labels]
    max_scores = [result["category_weights"].get(k, 0) for k in labels]
    x = np.arange(len(labels))
    width = 0.38
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    _style_axes(fig, ax)
    ax.bar(x - width / 2, scores, width, label="Score", color="#38bdf8")
    ax.bar(x + width / 2, max_scores, width, label="Max", color="#cbd5e1")
    ax.set_xticks(x)
    ax.set_xticklabels([k.title() for k in labels], rotation=18, ha="right")
    ax.set_ylabel("Points")
    ax.set_title("Category Scores vs Max")
    ax.legend(facecolor="#ffffff", edgecolor="#d1d5db")
    ax.grid(axis="y", color="#e5e7eb", linestyle="--", alpha=0.8)
    return _fig_to_data_url(fig)


def _category_radar_chart(result: Dict) -> str:
    labels = list(result["category_scores"].keys())
    values = [
        (result["category_scores"].get(k, 0) / result["category_weights"].get(k, 1)) if result["category_weights"].get(k) else 0
        for k in labels
    ]
    labels_cycle = labels + labels[:1]
    values_cycle = values + values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles_cycle = angles + angles[:1]
    fig, ax = plt.subplots(subplot_kw={"polar": True}, figsize=(5, 5))
    _style_axes(fig, ax)
    ax.set_ylim(0, 1)
    ax.plot(angles_cycle, values_cycle, color="#38bdf8", linewidth=2)
    ax.fill(angles_cycle, values_cycle, color="#38bdf8", alpha=0.25)
    ax.set_xticks(angles)
    ax.set_xticklabels([k.title() for k in labels], color="#111827")
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.5", "0.75", "1.0"], color="#6b7280")
    ax.grid(color="#e5e7eb", linestyle="--", alpha=0.8)
    ax.set_title("Category Performance (0-1)", pad=14)
    return _fig_to_data_url(fig)


def _criteria_bar_chart(result: Dict) -> str:
    codes = list(result["criteria_meta"].keys())
    scores = [result["criteria_scores"].get(code, 0) for code in codes]
    y_pos = np.arange(len(codes))
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    _style_axes(fig, ax)
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(codes)))
    ax.barh(y_pos, scores, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(codes, color="#111827")
    ax.invert_yaxis()
    ax.set_xlabel("Score (0-4)")
    ax.set_title("20-Criteria Checklist Scores")
    ax.set_xlim(0, 4.2)
    ax.grid(axis="x", color="#e5e7eb", linestyle="--", alpha=0.8)
    return _fig_to_data_url(fig)


def generate_result_charts(result: Dict) -> Dict[str, str]:
    """Generate base64 chart images for the result report."""
    try:
        return {
            "categories_bar": _category_bar_chart(result),
            "categories_radar": _category_radar_chart(result),
            "criteria_bar": _criteria_bar_chart(result),
        }
    except Exception:
        # If chart generation fails, return empty dict so HTML still renders.
        return {}


def _image_from_data_url(data_url: str, max_width: float) -> Image | None:
    if not data_url:
        return None
    try:
        payload = data_url.split(",", 1)[-1]
        img_bytes = base64.b64decode(payload)
        buf = io.BytesIO(img_bytes)
        img = Image(buf)
        aspect = img.imageHeight / float(img.imageWidth or 1)
        img.drawWidth = max_width
        img.drawHeight = max_width * aspect
        return img
    except Exception:
        return None


def export_result_pdf(result: Dict, output_path: str | Path, chart_images: Dict[str, str] | None = None) -> str:
    """Create a PDF report with charts and return the saved path."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chart_images = chart_images or generate_result_charts(result)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()
    muted = ParagraphStyle(name="Muted", parent=styles["BodyText"], fontSize=9, textColor=colors.HexColor("#6b7280"))
    story: List = []

    story.append(Paragraph(f"Result Report — {result['student_name']}", styles["Title"]))
    meta_line = " | ".join(
        [
            f"Level Tested: {result['level']}",
            f"Determined Level: {result['determined_level']}",
            f"Total Score: {result['total_score']:.1f} / 80",
            f"Generated: {result['metadata'].get('generated_at', '')}",
        ]
    )
    story.append(Paragraph(meta_line, muted))
    story.append(Spacer(1, 12))

    category_scores = result["category_scores"]
    best_cat = max(category_scores.items(), key=lambda kv: kv[1]) if category_scores else ("-", 0)
    worst_cat = min(category_scores.items(), key=lambda kv: kv[1]) if category_scores else ("-", 0)

    stats_table = Table(
        [
            ["Total Score", f"{result['total_score']:.1f} / 80"],
            ["Determined Level", result["determined_level"]],
            ["Top Category", f"{best_cat[0].title()} ({best_cat[1]:.1f})"],
            ["Needs Work", f"{worst_cat[0].title()} ({worst_cat[1]:.1f})"],
        ],
        colWidths=[140, 340],
    )
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#e5e7eb")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1f2937")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#1f2937")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(Paragraph("Snapshot", styles["Heading2"]))
    story.append(stats_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("Visual Summary", styles["Heading2"]))
    chart_specs = [
        ("categories_bar", "Category Scores vs Max", "Points earned in each category compared to the maximum."),
        ("categories_radar", "Normalized Category Performance", "Performance scaled 0-1 for quick shape view."),
        ("criteria_bar", "20-Criteria Checklist", "Scores for each rubric criterion (0-4 scale)."),
    ]
    for key, title, desc in chart_specs:
        img = _image_from_data_url(chart_images.get(key, ""), max_width=460)
        if img:
            story.append(Paragraph(title, styles["Heading3"]))
            story.append(img)
            story.append(Paragraph(desc, muted))
            story.append(Spacer(1, 10))

    story.append(Paragraph("Category Breakdown", styles["Heading2"]))
    cat_data = [["Category", "Score", "Max"]]
    for name, score in category_scores.items():
        cat_data.append([name.title(), f"{score:.1f}", f"{result['category_weights'][name]:.1f}"])
    cat_table = Table(cat_data, colWidths=[180, 90, 90])
    cat_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#9ca3af")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#e5e7eb")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1f2937")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#1f2937")),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#0f172a")),
            ]
        )
    )
    story.append(cat_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("20-Criteria Checklist", styles["Heading2"]))
    crit_data = [["Code", "Criterion", "Score (0-4)"]]
    for code in result["criteria_meta"]:
        crit_data.append(
            [
                code,
                result["criteria_meta"][code]["criterion"],
                str(result["criteria_scores"].get(code, 0)),
            ]
        )
    crit_table = Table(crit_data, colWidths=[60, 360, 90])
    crit_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#9ca3af")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#e5e7eb")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1f2937")),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#1f2937")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#0f172a")),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
            ]
        )
    )
    story.append(crit_table)
    story.append(Spacer(1, 12))

    def _add_list(title: str, items: List[str]):
        story.append(Paragraph(title, styles["Heading2"]))
        if items:
            for item in items:
                story.append(Paragraph(f"• {item}", styles["BodyText"]))
        else:
            story.append(Paragraph("No data", muted))
        story.append(Spacer(1, 8))

    _add_list("Strengths", result.get("strengths", []))
    _add_list("Weaknesses", result.get("weaknesses", []))
    _add_list("Recommendations", result.get("recommendations", []))

    doc.build(story)
    return str(output_path)


def render_test_paper(test_data: Dict) -> str:
    metadata = test_data["metadata"]
    sections = test_data["sections"]
    html_parts: List[str] = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<title>CEFR Test Paper</title>",
        _base_css(),
        "</head><body>",
        f"<h1>CEFR Level Test — {metadata['level']}</h1>",
        f"<div class='meta'><div>Duration: {metadata['duration']} minutes</div><div>Generated: {metadata['generated_at']}</div></div>",
    ]

    for section_key in ["reading", "vocabulary", "conversation", "grammar", "writing"]:
        section = sections[section_key]
        html_parts.append("<div class='card'>")
        html_parts.append(f"<h2>{section['title']}</h2>")
        if section_key != "writing":
            for q in section["questions"]:
                html_parts.append("<div class='question'>")
                html_parts.append(f"<div><span class='tag'>{q['id']}</span> {q['text']}</div>")
                html_parts.append("<div class='options'>")
                for opt in q["options"]:
                    html_parts.append(f"<div class='option'>({opt['label']}) {opt['text']}</div>")
                html_parts.append("</div></div>")
        else:
            prompt = section["questions"][0]["prompt"]
            html_parts.append(f"<p>{prompt}</p>")
            html_parts.append("<div class='list-item' style='min-height:160px;'>[Write your response here]</div>")
        html_parts.append("</div>")

    html_parts.append("</body></html>")
    return "".join(html_parts)


def render_answer_key(test_data: Dict) -> str:
    metadata = test_data["metadata"]
    answer_key = test_data["answer_key"]
    rows = "".join(
        f"<tr><td>{qid}</td><td>{ans}</td></tr>"
        for qid, ans in sorted(answer_key.items(), key=lambda kv: (kv[0][0], int(kv[0][1:])))
    )
    html = f"""<!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Answer Key {metadata['level']}</title>{_base_css()}</head>
    <body>
      <h1>Answer Key — {metadata['level']}</h1>
      <div class='meta'><div>Generated: {metadata['generated_at']}</div><div>Total Questions: {metadata['total_questions']}</div></div>
      <div class='card'>
        <table>
          <thead><tr><th>Question</th><th>Answer</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </body></html>
    """
    return html


def render_result_report(result: Dict, chart_images: Dict[str, str] | None = None) -> str:
    meta = result["metadata"]
    chart_images = chart_images or generate_result_charts(result)
    total_possible = 80.0
    overall_pct = (result["total_score"] / total_possible * 100) if total_possible else 0
    writing_score = result["category_scores"].get("writing", 0.0)
    reading_score = result["category_scores"].get("reading", 0.0)
    grammar_score = result["category_scores"].get("grammar", 0.0)
    conversation_score = result["category_scores"].get("conversation", 0.0)
    vocabulary_score = result["category_scores"].get("vocabulary", 0.0)
    category_scores = result["category_scores"]
    best_cat = max(category_scores.items(), key=lambda kv: kv[1]) if category_scores else ("-", 0)
    worst_cat = min(category_scores.items(), key=lambda kv: kv[1]) if category_scores else ("-", 0)
    cat_rows = "".join(
        f"<tr><td>{name.title()}</td><td>{score:.1f} / {result['category_weights'][name]:.1f}</td></tr>"
        for name, score in result["category_scores"].items()
    )
    crit_rows = "".join(
        f"<tr><td>{code}</td><td>{info['criterion']}</td><td>{score}</td></tr>"
        for code, info, score in [
            (c, result["criteria_meta"][c], result["criteria_scores"].get(c, 0))
            for c in result["criteria_meta"]
        ]
    )
    strengths = "".join(f"<div class='list-item'>{item}</div>" for item in result.get("strengths", []))
    weaknesses = "".join(f"<div class='list-item'>{item}</div>" for item in result.get("weaknesses", []))
    recs = "".join(f"<div class='list-item'>{item}</div>" for item in result.get("recommendations", []))

    html = f"""<!DOCTYPE html>
    <html><head><meta charset="utf-8"><title>Result Report</title>{_base_css()}</head>
    <body>
      <h1>Result Report — {result['student_name']}</h1>
      <div class='meta'>
        <div>Level Tested: {result['level']}</div>
        <div>Determined Level: <span class='highlight'>{result['determined_level']}</span></div>
        <div>Total Score: <span class='highlight'>{result['total_score']:.1f} / 80</span> ({overall_pct:.1f}%)</div>
        <div>Generated: {meta['generated_at']}</div>
      </div>

      <div class='card'>
        <h2>Performance Snapshot</h2>
        <div class='stat-grid'>
          <div class='stat'><div class='label'>Total Score</div><div class='value'>{result['total_score']:.1f} / {total_possible:.0f}</div></div>
          <div class='stat'><div class='label'>Determined Level</div><div class='value'>{result['determined_level']}</div></div>
          <div class='stat'><div class='label'>Top Category</div><div class='value'>{best_cat[0].title()} ({best_cat[1]:.1f})</div></div>
          <div class='stat'><div class='label'>Needs Work</div><div class='value'>{worst_cat[0].title()} ({worst_cat[1]:.1f})</div></div>
          <div class='stat'><div class='label'>Writing</div><div class='value'>{writing_score:.1f} / {result['category_weights'].get('writing', 0):.0f}</div></div>
          <div class='stat'><div class='label'>Reading</div><div class='value'>{reading_score:.1f} / {result['category_weights'].get('reading', 0):.0f}</div></div>
          <div class='stat'><div class='label'>Vocabulary</div><div class='value'>{vocabulary_score:.1f} / {result['category_weights'].get('vocabulary', 0):.0f}</div></div>
          <div class='stat'><div class='label'>Grammar</div><div class='value'>{grammar_score:.1f} / {result['category_weights'].get('grammar', 0):.0f}</div></div>
          <div class='stat'><div class='label'>Conversation</div><div class='value'>{conversation_score:.1f} / {result['category_weights'].get('conversation', 0):.0f}</div></div>
        </div>
      </div>

      <div class='card'>
        <h2>Visual Summary</h2>
        <div class='charts'>
          <div class='chart'>
            <img src="{chart_images.get('categories_bar', '')}" alt="Category bar chart">
            <div class='muted'>Category scores vs maximum points</div>
          </div>
          <div class='chart'>
            <img src="{chart_images.get('categories_radar', '')}" alt="Category radar chart">
            <div class='muted'>Normalized performance (0-1 scale)</div>
          </div>
          <div class='chart'>
            <img src="{chart_images.get('criteria_bar', '')}" alt="Criteria bar chart">
            <div class='muted'>20-criteria checklist scores</div>
          </div>
        </div>
      </div>

      <div class='card'>
        <h2>Category Breakdown</h2>
        <table>
          <thead><tr><th>Category</th><th>Score</th></tr></thead>
          <tbody>{cat_rows}</tbody>
        </table>
      </div>

      <div class='card'>
        <h2>20-Criteria Checklist</h2>
        <table>
          <thead><tr><th>Code</th><th>Criterion</th><th>Score (0-4)</th></tr></thead>
          <tbody>{crit_rows}</tbody>
        </table>
      </div>

      <div class='card'>
        <h2>Strengths</h2>
        <div class='grid'>{strengths or "<div class='muted'>No data</div>"}</div>
      </div>

      <div class='card'>
        <h2>Weaknesses</h2>
        <div class='grid'>{weaknesses or "<div class='muted'>No data</div>"}</div>
      </div>

      <div class='card'>
        <h2>Recommendations</h2>
        <div class='grid'>{recs or "<div class='muted'>No data</div>"}</div>
      </div>
    </body></html>
    """
    return html


__all__ = ["render_test_paper", "render_answer_key", "render_result_report", "generate_result_charts", "export_result_pdf"]
