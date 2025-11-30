from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from main import CEFRTestSystem
from test_generator import LEVEL_CONFIG


def run_gui(default_output: str = "outputs") -> None:
    root = tk.Tk()
    root.title("CEFR Test Generator")
    root.geometry("520x520")

    level_var = tk.StringVar(value=list(LEVEL_CONFIG.keys())[0])
    output_var = tk.StringVar(value=default_output)
    use_llm_var = tk.BooleanVar(value=False)
    provider_var = tk.StringVar(value="openai")
    model_var = tk.StringVar(value="")

    count_vars = {
        "reading": tk.StringVar(value=str(LEVEL_CONFIG[level_var.get()]["reading"])),
        "vocabulary": tk.StringVar(value=str(LEVEL_CONFIG[level_var.get()]["vocabulary"])),
        "conversation": tk.StringVar(value=str(LEVEL_CONFIG[level_var.get()]["conversation"])),
        "grammar": tk.StringVar(value=str(LEVEL_CONFIG[level_var.get()]["grammar"])),
        "writing": tk.StringVar(value=str(LEVEL_CONFIG[level_var.get()]["writing"])),
    }

    def sync_counts(*_):
        cfg = LEVEL_CONFIG[level_var.get()]
        for key, var in count_vars.items():
            var.set(str(cfg[key]))

    def browse_output():
        path = filedialog.askdirectory()
        if path:
            output_var.set(path)

    def log(msg: str):
        text.configure(state="normal")
        text.insert("end", msg + "\n")
        text.see("end")
        text.configure(state="disabled")

    def on_generate():
        try:
            counts = {k: int(v.get()) for k, v in count_vars.items()}
        except ValueError:
            messagebox.showerror("Invalid input", "Question counts must be integers.")
            return
        level = level_var.get()
        system = CEFRTestSystem(output_dir=output_var.get())
        context_val = context_text.get("1.0", "end-1c").strip()
        try:
            result = system.generate_test(
                level,
                question_counts=counts,
                use_llm=use_llm_var.get(),
                llm_provider=provider_var.get(),
                llm_model=model_var.get() or None,
                context=context_val or None,
            )
        except Exception as exc:
            messagebox.showerror("Generation failed", str(exc))
            log(f"[error] {exc}")
            return
        log(f"[ok] {level} generated.")
        log(f"  Test: {result['test_file']}")
        log(f"  Answer: {result['answer_key_file']}")
        log(f"  Data: {result['data_file']}")
        if result["test_data"]["metadata"].get("llm", {}).get("fallback"):
            log(f"  LLM fallback: {result['test_data']['metadata']['llm'].get('error','')}")

    # Layout
    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Level").grid(row=0, column=0, sticky="w")
    ttk.OptionMenu(frm, level_var, level_var.get(), *LEVEL_CONFIG.keys(), command=sync_counts).grid(row=0, column=1, sticky="ew")

    ttk.Label(frm, text="Output Dir").grid(row=1, column=0, sticky="w")
    out_entry = ttk.Entry(frm, textvariable=output_var)
    out_entry.grid(row=1, column=1, sticky="ew")
    ttk.Button(frm, text="Browse", command=browse_output).grid(row=1, column=2, padx=4)

    ttk.Separator(frm, orient="horizontal").grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

    row = 3
    for key, label in [("reading", "Reading"), ("vocabulary", "Vocabulary"), ("conversation", "Conversation"), ("grammar", "Grammar"), ("writing", "Writing")]:
        ttk.Label(frm, text=f"{label} count").grid(row=row, column=0, sticky="w")
        ttk.Entry(frm, width=10, textvariable=count_vars[key]).grid(row=row, column=1, sticky="w")
        row += 1

    ttk.Separator(frm, orient="horizontal").grid(row=row, column=0, columnspan=3, pady=10, sticky="ew")
    row += 1

    ttk.Checkbutton(frm, text="Use LLM for questions", variable=use_llm_var).grid(row=row, column=0, columnspan=2, sticky="w")
    row += 1
    ttk.Label(frm, text="Provider").grid(row=row, column=0, sticky="w")
    ttk.OptionMenu(frm, provider_var, provider_var.get(), "openai", "anthropic", "gemini").grid(row=row, column=1, sticky="w")
    row += 1
    ttk.Label(frm, text="Model (optional)").grid(row=row, column=0, sticky="w")
    ttk.Entry(frm, textvariable=model_var).grid(row=row, column=1, sticky="ew")
    row += 1

    ttk.Label(frm, text="Custom Context (optional)").grid(row=row, column=0, sticky="nw", pady=5)
    context_text = tk.Text(frm, height=4, width=40)
    context_text.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)
    row += 1

    ttk.Button(frm, text="Generate", command=on_generate).grid(row=row, column=0, pady=10, sticky="w")

    text = tk.Text(frm, height=12, state="disabled")
    text.grid(row=row + 1, column=0, columnspan=3, sticky="nsew", pady=6)

    frm.columnconfigure(1, weight=1)
    frm.rowconfigure(row + 1, weight=1)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
