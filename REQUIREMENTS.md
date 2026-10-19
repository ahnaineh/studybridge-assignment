# Assignment requirement map

Both assignments share StudyBridge's fictional tutoring business. This map points
to the implementation and evidence a reviewer can inspect. It is not a claim of
perfect model behavior or a guaranteed grade.

## C3 — Introduction to Agents

| Required item | Where to inspect |
|---|---|
| Business identity: name, mission, services, team and value proposition | `me/about_business.pdf`, `me/business_summary.txt` |
| Separate, labeled persona and operational instructions | `business_agent.ipynb`, `PERSONAS` and `INSTRUCTIONS_BASE` in `agent_core.py` |
| General / lead / feedback router before generation | `route_message`, `initial_state`, router demonstration in C3 notebook |
| `record_customer_interest(email, name, message)` | Validated local JSONL tool, explicit native function calls and observations |
| `record_feedback(question)` for feedback and unknown facts | Tool implementation, live unknown-policy and feedback evidence |
| MCP-style schema names, parameters and expected outputs | `TOOL_SCHEMAS`; these are local functions, not an MCP server |
| Answers use both PDF and TXT content | `load_sources` and `build_prompt` |
| Gemini conversation history and manual tool handling | `initial_state`, `model_step`, `execute_tools`, `c3_reply` |
| Gradio ChatInterface | `app.py`, notebook launch cell and recorded demonstration |
| GitHub repository and functionality video | This repository and `media/studybridge_demo.mp4` |
| API key private, project runs | `.env.example`, hidden Colab key setup, `VALIDATION.md` |

The summary filename follows the project structure and final checklist in the
brief (`business_summary.txt`). The other paragraph calls it `summary.txt`.
The permitted Gemini API is implemented with the Google Gen AI SDK.

Optional bonuses are separate: the reflection pass is implemented but its live
original/revised evidence is not claimed as completed; Hugging Face Spaces hosting
is not claimed.

## C4 — Agent Personas and Thinking Mechanisms

| Required item | Where to inspect |
|---|---|
| Use-case goal, audience, tools and limitations | Opening notebook summary, business profile, README |
| One approved framework | LangGraph `StateGraph` |
| Manual ReAct loop, no prebuilt executor | Explicit reason / act / answer / limit nodes and conditional edges in `build_graph` |
| System behavior and tool descriptions | `build_prompt`, persona/instructions blocks and schemas |
| Detect native model actions, execute tools and return observations | `model_step`, `execute_tools`, recorded action/observation traces |
| Parse a final answer and bound the loop | Text/function-call parsing, `MAX_MODEL_TURNS`, `finish` |
| At least two different personas and matching LLM configurations | Friendly Advisor and Course Specialist; temperature, top-p and top-k settings |
| With/without Chain-of-Thought prompting | Direct versus internal stepwise-reasoning prompt; public actions/observations and final answers are logged |
| Zero-shot vs. few-shot | Zero, one and two worked-example conditions |
| System prompts vs. in-message instructions | Same assembled content placed in either system instructions or the user message |
| Configuration experimentation, logs and comparison | `experiments.py`, raw CSV/JSONL/configurations, experiment report |
| Separate atomic instructions, input/output format and worked example | `INSTRUCTIONS_BASE`, `WORKED_EXAMPLE`, optional second example |
| All five reflection questions | `reflection.md` and `react_agent.ipynb` |

The reasoning comparison changes the prompt. It does not switch the provider's
thinking configuration, and private chain-of-thought is not requested or published.
The configuration list in the brief gives examples; this implementation varies
temperature/top-p/top-k rather than claiming to test every provider parameter.
The final matched study has 47 returned setup/case pairs across 51 conversation attempts; 46 tool checks pass and one forbidden proposed save is blocked. Results, source hashes and limitations are reported in `evidence/c4/EXPERIMENT_REPORT.md`.
