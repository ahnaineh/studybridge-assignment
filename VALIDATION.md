# Validation record

Validation was performed on 13 October 2026. This record separates real model
behavior from simulated checks and notebook execution.

## Real Colab behavior

C3 completed five behavior checks: published prices, a catalog recommendation,
two-turn lead collection using history, an unknown refund-policy question and
explicit feedback. The first price/recommendation attempts encountered service
or minute-quota errors; their successful paced retries remain in evidence/.
The full Flash request endpoint reported a newer backend version; its daily
quota was exhausted before the C4 study. These C3 calls are not a controlled
comparison against C4's model.

C3's Gradio browser test returned USD20 for an individual lesson and USD72 for
the package. C4's browser test recommended Python Starter and returned the
published scope/prices after an initial provider failure and UI retry.

The primary C4 study used requested/reported `gemini-3.5-flash-lite` throughout:
60 attempted conversations, 20 answers and 40 provider errors. Nineteen returned
answers passed the tool-name check. A worked-example email leak caused the
remaining behavioral failure. It is retained in the original CSV and traces;
the final code adds a student-message provenance check before recording a lead.
The eight-case extension returned five answers, all passing the tool check, and three provider errors. Across both studies: 68 attempts, 25 returned answers and 43 provider failures. See the experiment report for scores and limitations.

## Software checks

Eleven offline regression tests passed with the real SDK's Content/Part objects
and scripted model responses. They cover native signatures, function observations
using the user role, multiple calls, unknown calls, missing contact validation,
example-data rejection, bounded loops, turn-level deduplication, and a transient
generation retry that does not duplicate a persisted action.

The Gradio component tree constructs successfully with the pinned dependencies.
Notebook schema and every code cell's Python syntax validate. Both notebooks were
executed in independent fresh Python kernels on the existing Colab VM, using their
saved-evidence mode. Live demonstration and full experiment rerun flags were off;
this check verifies setup, definitions, source loading and result-display cells,
not a new full live behavior run or a new Colab VM.

Business PDF text was checked against the summary, and the one-page rendered
profile was visually inspected. The submitted package contains synthetic contact
details only. No key, .env, private contact record or persistent browser credential
is included.

## Scope and limits

The SDK/manual-loop protocol and UI fixes were verified through actual Colab use.
The later lead-provenance fix passed regression checks and a targeted live Colab
check: the example-email call was rejected, and the model asked for the missing
email. The earlier primary experiment was not rerun in full after that patch. Provider failures remain a real
runtime limitation and are surfaced honestly in the UI. A retry may follow a tool
write that already succeeded; users should inspect logs before resubmitting.

The project is a coursework prototype with local JSONL logging and short-term
memory. Optional C3 reflection bonus and Hugging Face deployment were not claimed.
The student still needs to record and submit the required video.
