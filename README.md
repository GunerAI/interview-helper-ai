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

---

## Install dependencies:

pip install -r requirements.txt

---

## ⚙️ Setup

---

## 1. Clone this repo:
   ```bash
   git clone https://github.com/<your-username>/interview-helper.git
   cd interview-helper
	```bash
---

## 2.	Create a virtual environment (recommended):
    ```bash
    git clone https://github.com/<your-username>/interview-helper.git
    cd interview-helper

## 3.	Install dependencies:
    ```bash
    pip install -r requirements.txt

## 4.	Add your OpenAI API key in .env:
    OPENAI_API_KEY=sk-your-key-here

## 5.	(Optional) Override the model in .env:
    OPENAI_MODEL=gpt-4o-mini

---

```markdown
## 🚀 Usage

Run from the terminal:

```bash
python app.py --temperature 0.7 --top_p 1.0 --max_tokens 1200

You’ll be guided to enter:
	•	Job Title
	•	Interviewer Title
	•	Job Description (multi-line, finish with Enter + Ctrl+D)
	•	Resume (multi-line, finish with Enter + Ctrl+D)

Outputs:
	•	plan.json → Planning phase (JSON)
	•	output.md → Final interview questions (Markdown)

---

## 📂 Example Inputs
```markdown
See [`examples/inputs.txt`](examples/inputs.txt) for sample sets.

### Example 1
- Job Title: Security Operations Analyst  
- Interviewer Title: Hiring Manager  
- Job Description:
  - Monitor SIEM alerts (Splunk/Sentinel), triage incidents, escalate as needed
  - Phishing investigation, EDR containment with Defender XDR
  - Create playbooks and improve detection coverage  
- Resume:
  - 2 years SOC Tier 1/2, Splunk SPL, Sentinel KQL
  - Phishing triage, malware sandboxing, Any.Run, URLScan, VirusTotal
  - XSOAR automation, Entra ID incident actions, endpoint isolation

## 📄 Example Output (Markdown)
```markdown
## Role Context
SOC Manager interviewing for Cyber Security Analyst role.

### Interview Questions
1. Can you walk me through how you triage alerts in Splunk or Sentinel?
2. How do you validate a suspicious IP or domain using OSINT tools?
...
10. How do you handle incident response in high-pressure situations?

### Next Steps
- Review recent phishing cases and practice explaining triage.
- Brush up on MITRE ATT&CK tactics related to your resume.
- Prepare concise examples of collaboration with SOC teams.

---

## 🛠 Development Notes
```markdown
- Uses the **OpenAI Responses API** (not the old Chat Completions API).
- Implements a **two-stage prompt chain**:
  1. Planning → JSON plan with steps, assumptions, success criteria.
  2. Answering → Markdown with 10 tailored questions.
- If JSON parsing fails in Chain 1, a one-time repair attempt is made.
- Outputs are saved automatically:
  - `plan.json` → Planning JSON
  - `output.md` → Final Markdown

## 🤝 Contributing
```markdown
Pull requests are welcome! Please:
1. Fork the repo
2. Create a feature branch
3. Submit a PR with clear description

## 📜 License
```markdown
MIT License © 2025 [Your Name]










    
  
