# Validation record

Final submission checks were completed on 20 October 2026 (Beirut time; 19 October
UTC). The core used for the completed C4 study has SHA-256
`507c32c1584c35387b924e3c09335fd65d3e27766f5729b65a847c5978a6227b`.
Each final-study source snapshot uses that same core. A later C3-only reflection
reviewer-prompt fix is documented in `evidence/c3-reflection/REPORT.md`; the C4
execution path and the historical comparison evidence are unchanged.

## Live C4 behavior and comparisons

The final matched matrix contains 47 setup/case pairs. It returned 43 answers on
the initial pass. Three unanswered 503 cases and one unanswered 500 INTERNAL case
were repeated successfully, giving 51 conversation attempts and 47 returned answers.
The original failed attempts are retained. Individual generation retries inside a
conversation are recorded separately; 51 is not the number of API requests.

Both personas have returned answers for the same three cases in each prompt
condition. Both seven-case baselines passed all seven expected tool checks,
including lead collection, missing-email handling, unknown questions, explicit
feedback and history-based collection. The temperature-only control also has
three returned answers.

Across all 47 returned answers, 46 passed the automated tool check. Friendly Advisor
with in-message instructions proposed an example-only email. The runtime rejected
the save, and the final answer asked for the missing email without claiming a save.
The attempted action is kept as a model error. No answered behavioral failure was
repeated to obtain a better score.

See `evidence/c4/EXPERIMENT_REPORT.md` for matched comparisons, explicit qualitative
review notes, raw CSV/JSONL, source snapshots, recovery selections and limits.
The original 68-attempt study and interrupted sequential pilot remain separate
from these final-study totals. Exported original evidence was restored locally
and verified against `evidence/c4/balanced/files_sha256.json`.

## Software and notebook checks

All 11 offline regression tests passed again in Colab with the real SDK's
Content/Part objects and scripted model responses. They cover native signatures,
user-role function observations, multiple/unknown calls, required contacts,
example-data rejection, bounded loops, history, per-turn deduplication and a
transient generation retry that does not repeat an already persisted action.
The output is in `evidence/final-offline-tests.txt`.

Both final notebooks executed in independent fresh Python kernels on the existing
Colab VM, in saved-evidence mode:

| Notebook | Executed code cells | Error outputs |
|---|---:|---:|
| `business_agent.ipynb` | 15/15 | 0 |
| `react_agent.ipynb` | 18/18 | 0 |

Live demonstration, full experiment rerun and Gradio launch flags were off during
this notebook check. It verifies setup, definitions, source loading, result display
and saved traces; it is separate from the real model study above. The setup now
keeps an already-open project instead of switching into an older extracted ZIP.
The original execution record is `evidence/final-notebook-validation.json`.
Both notebooks and the same 11 tests were rerun after the C3 reflection update;
see `evidence/c3-reflection/notebook-validation.json` and
`evidence/c3-reflection/offline-tests.txt` for the current checks.
The C3 notebook now executes a display of the two saved reflection examples.

Every Python file and notebook code cell passes a syntax check. The published
aggregates are reproducible with `python summarize_results.py` from the original
rows and the disclosed review annotations. All 47 returned answers were reviewed
against the business facts and actual tool observations; the ratings are assisting-
agent judgments, not independent human evaluation.

## C3 and the recorded interface

Earlier real C3 Colab checks completed published pricing, catalog recommendation,
two-turn lead collection using history, unknown refund-policy logging and explicit
feedback logging. Their original outputs and paced retries remain in `evidence/`.
The Gradio interface was also used for the actual recorded demonstration.

`media/studybridge_demo.mp4` is the final silent H.264 recording: 1280×720, 30 fps,
about 2 minutes 11 seconds. It shows prices, asking for an email, saving interest
using history, logging an unknown policy question, logging feedback and a C4
Python Starter recommendation. Typing was retimed about 33% faster on average,
with varied pace; idle API waits were shortened. Text and model responses are
actual captured app content. File metadata and SHA-256 are in
`media/recording-details.json`.

The business PDF was checked against the summary and visually inspected; it was
not changed during this final evaluation. Published contact details are synthetic.
A private-key scan of the curated export passed. No `.env`, API key or browser
credential is included in the repository.

## Submission boundary and prototype limits

The repository contains both notebooks, business files, implementation, evidence,
reflection and video. `submission_link.txt` links to the repository, each assignment
notebook, the video and the C4 report. The user will upload its Desktop copy to
both Moodle assignment pages; Moodle submission is not claimed here.

The project records interest rather than booking or payment. Logs and short-term
history do not provide a production database or global deduplication. A tool write
can precede a provider failure, so a new user request can create a duplicate record.
Provider availability and some unsupported callback wording remain observed limits.
One repetition per condition does not establish a general winning prompt.
The optional C3 reflection pass now has live original/revised evidence and a
controlled correction test; see `evidence/c3-reflection/REPORT.md`. Optional Hugging
Face Spaces hosting is not claimed.
