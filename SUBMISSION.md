# StudyBridge submission guide

This repository contains both Agentic Systems assignments using the same fictional
StudyBridge tutoring business and Gemini. Submit the repository URL separately
through the C3 and C4 Moodle assignment links.

Repository: https://github.com/ahnaineh/studybridge-assignment

## C3 — Introduction to Agents

Start with [business_agent.ipynb](business_agent.ipynb). It includes the separate
persona and instructions, business PDF/TXT loading, three-intent router, required
lead and feedback tools, manual model/tool interaction, short-term history and
Gradio interface. Business identity files are in [me/](me/).

[Watch or download the silent functionality video](media/studybridge_demo.mp4).
The video shows prices, collecting a missing email, saving a lead using history,
logging an unknown refund question, recording feedback and a C4 course recommendation.
It records actual model responses. Typing is paced for readability and idle API waits
are shortened. There is no narration; the assignment PDF does not require it.

## C4 — Agent Personas and Thinking Mechanisms

Start with [react_agent.ipynb](react_agent.ipynb). The explicit LangGraph nodes and
conditional edges implement the tool/action/observation loop without a prebuilt
executor. Two personas have distinct prompts and sampling configurations. The
notebook includes the measured comparisons and answers to all five reflection questions.

See [the experiment report](evidence/c4/EXPERIMENT_REPORT.md),
[reflection.md](reflection.md), and [VALIDATION.md](VALIDATION.md) for measured
results, evidence and limitations. The reasoning experiment compares a direct
prompt against an internal stepwise-reasoning prompt, with public action/observation
traces. It does not request or publish private chain-of-thought.

## Moodle upload

Upload `submission_link.txt` to each assignment's Moodle page. The same repository
contains both assignments; the text file identifies the relevant notebook and video.
Check the assignment title before uploading. Moodle-specific deadlines and final
submission status are determined by the course platform.

## API key and optional work

A grader supplies a private Gemini key through Colab Secrets, the hidden prompt or
a local `.env`. Keys are deliberately absent from GitHub. All published contacts
are synthetic `example.com` details. Hugging Face hosting and C3 reflection-pass
bonus evidence are optional and are not claimed as completed bonuses.
