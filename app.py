#!/usr/bin/env python3
import os
import json
import argparse
import textwrap
from typing import Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv

# =========================
# Config
# =========================
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-chat-latest")  # set via env or keep this default

SYSTEM_PLANNER = """You are a precise planning assistant.
Given the user's inputs for an Interview Helper (job title, interviewer title, job description, resume),
produce a compact execution plan in STRICT JSON with EXACTLY these keys:
{
  "steps": ["...", "..."],          // 3–6 short, clear steps
  "assumptions": ["...", "..."],    // bullet list of assumptions
  "success_criteria": ["...", "..."]// what success looks like
}
Rules:
- Return STRICT JSON only. No markdown, no commentary.
- Keep steps actionable and specific to turning inputs into 10 tailored interview questions.
"""

SYSTEM_ANSWERER = """You are an interview-prep assistant.
Using the user's original inputs AND the provided planning JSON, produce a final response in MARKDOWN that:
- Includes a brief overview section (who the interviewer is, what the role needs).
- Presents EXACTLY **10** tailored interview questions (mix: role/technical, behavioral, resume-based follow-ups).
- Uses clear headings and bullet points.
- Ends with a short **Next Steps** list (3–5 bullets).
- Be concise, specific, and avoid duplication.
"""

PLANNER_USER_TEMPLATE = """INPUTS:
JOB TITLE: {role}

INTERVIEWER TITLE: {interviewer_title}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
"""

ANSWER_USER_TEMPLATE = """ORIGINAL INPUTS:
JOB TITLE: {role}

INTERVIEWER TITLE: {interviewer_title}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

PLANNING JSON:
{plan_json}
"""

# =========================
# Helpers
# =========================
def prompt_multiline(label: str) -> str:
    print(f"\nEnter {label}. End with an empty line, then press Ctrl+D (macOS/Linux) to finish:")
    print("-" * 80)
    try:
        lines = []
        while True:
            line = input()
            if line.strip() == "" and len(lines) > 0:
                break
            lines.append(line)
    except EOFError:
        pass
    finally:
        print("-" * 80)
    return "\n".join(lines).strip()

def call_openai_responses(
    client: OpenAI,
    model: str,
    system: str,
    user: str,
    temperature: float,
    top_p: float,
    max_tokens: int
) -> str:
    """
    Calls the Responses API and returns the text output.
    """
    resp = client.responses.create(
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_tokens,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
    )
    return resp.output_text

def try_parse_json_once(raw_text: str) -> Tuple[Optional[dict], Optional[str]]:
    """
    Try to parse JSON from model output. If it fails, attempt a quick local repair:
    - Extract substring from first '{' to last '}'.
    Returns (data, error_message).
    """
    try:
        return json.loads(raw_text), None
    except json.JSONDecodeError as e1:
        # quick substring heuristic
        if "{" in raw_text and "}" in raw_text:
            candidate = raw_text[raw_text.find("{"): raw_text.rfind("}") + 1]
            try:
                return json.loads(candidate), None
            except json.JSONDecodeError as e2:
                return None, f"JSON parsing failed (initial + substring): {e2}"
        return None, f"JSON parsing failed: {e1}"

def attempt_model_repair(client: OpenAI, model: str, broken_text: str,
                         temperature: float, top_p: float, max_tokens: int) -> Tuple[Optional[dict], Optional[str]]:
    """
    One-time repair: ask the model to return valid JSON only.
    If it still fails, return None with error text.
    """
    instruction = (
        "The following text was supposed to be STRICT JSON but isn't. "
        "Repair it to valid JSON that matches this schema:\n"
        "{\n"
        '  "steps": ["...", "..."],\n'
        '  "assumptions": ["...", "..."],\n'
        '  "success_criteria": ["...", "..."]\n'
        "}\n"
        "Return STRICT JSON only. No commentary."
    )
    fix_input = f"{instruction}\n\nBROKEN TEXT:\n{broken_text}"
    repaired = call_openai_responses(
        client, model, "You repair JSON. Output strict JSON only.", fix_input,
        temperature, top_p, max_tokens
    )
    data, err = try_parse_json_once(repaired)
    if data:
        return data, None
    else:
        return None, f"Repair attempt failed. Raw repair output:\n{repaired}\n\nParse error: {err}"

# =========================
# Main
# =========================
def main():
    # CLI
    parser = argparse.ArgumentParser(description="Interview Helper – two-stage prompt chaining CLI")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default: 0.7)")
    parser.add_argument("--top_p", type=float, default=1.0, help="Nucleus sampling top_p (default: 1.0)")
    parser.add_argument("--max_tokens", type=int, default=1000, help="Max output tokens per call (default: 1000)")
    args = parser.parse_args()

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found. Put it in .env (OPENAI_API_KEY=...)")
        return

    global MODEL
    # allow override via env OPENAI_MODEL if set
    MODEL = os.getenv("OPENAI_MODEL", MODEL)

    client = OpenAI(api_key=api_key)

    # Input collection
    print("\n=== Interview Helper (Two-Stage) ===")
    role = input("Step 1 — Enter Job Title: ").strip()
    interviewer_title = input("Step 1 — Enter Interviewer Title (Hiring Manager or Recruiter): ").strip()
    job_description = prompt_multiline("Step 2 — Job Description")
    resume_text = prompt_multiline("Step 3 — Resume")

    if not (role and interviewer_title and job_description and resume_text):
        print("Error: All inputs are required.")
        return

    # ------------- Chain 1: Planner (JSON) -------------
    planner_user = PLANNER_USER_TEMPLATE.format(
        role=role,
        interviewer_title=interviewer_title,
        job_description=job_description,
        resume_text=resume_text,
    )

    print("\n[Chain 1] Creating plan...")
    try:
        plan_raw = call_openai_responses(
            client=client,
            model=MODEL,
            system=SYSTEM_PLANNER,
            user=planner_user,
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
        )
    except Exception as e:
        print(f"OpenAI error during planning: {e}")
        return

    plan_data, parse_err = try_parse_json_once(plan_raw)
    repaired = False
    if not plan_data:
        print("[Chain 1] Plan JSON parse failed. Attempting a one-time repair...")
        plan_data, repair_err = attempt_model_repair(
            client, MODEL, plan_raw, args.temperature, args.top_p, args.max_tokens
        )
        repaired = plan_data is not None
        if not plan_data:
            print("Plan repair failed.")
            print(repair_err or "")
            print("\nRaw plan output:\n", plan_raw)
            return

    # Save plan
    with open("plan.json", "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2, ensure_ascii=False)
    print("[Chain 1] Plan ready. Saved to plan.json" + (" (repaired)" if repaired else ""))

    # ------------- Chain 2: Answer (Markdown) -------------
    print("[Chain 2] Generating final Markdown answer...")
    plan_json_compact = json.dumps(plan_data, ensure_ascii=False)

    answer_user = ANSWER_USER_TEMPLATE.format(
        role=role,
        interviewer_title=interviewer_title,
        job_description=job_description,
        resume_text=resume_text,
        plan_json=plan_json_compact
    )

    try:
        final_md = call_openai_responses(
            client=client,
            model=MODEL,
            system=SYSTEM_ANSWERER,
            user=answer_user,
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
        )
    except Exception as e:
        print(f"OpenAI error during answering: {e}")
        return

    # Display + Save
    print("\n========== FINAL ANSWER (Markdown) ==========\n")
    print(final_md)
    print("\n=============================================\n")

    with open("output.md", "w", encoding="utf-8") as f:
        f.write(final_md)
    print("Saved Markdown to output.md")

if __name__ == "__main__":
    main()