# Interview Helper (Python CLI)

A command-line tool that helps you prepare for job interviews by generating **10 tailored interview questions** based on:

- Job Title  
- Interviewer Title (Hiring Manager / Recruiter)  
- Job Description  
- Resume  

This app uses **prompt chaining** with the OpenAI API:  
1. **Planning Phase (JSON)** → Breaks down the request into clear steps, assumptions, and success criteria.  
2. **Answering Phase (Markdown)** → Uses the plan + inputs to generate structured interview questions in Markdown.

---

## ✨ Features
- Two-stage **Prompt Chaining**:
  - **Chain 1** → Planning (JSON with steps, assumptions, success criteria).
  - **Chain 2** → Answering (Markdown output with headings, 10 questions, Next Steps).
- **Configurable CLI flags**:  
  `--temperature`, `--top_p`, `--max_tokens`
- **Error handling**: One-time JSON repair attempt if model output breaks.
- Saves results to:
  - `plan.json` (planning stage)  
  - `output.md` (final Markdown response)

---

## 📦 Requirements
- Python 3.9+
- [OpenAI Python SDK](https://pypi.org/project/openai/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

Install dependencies:
```bash
pip install -r requirements.txt