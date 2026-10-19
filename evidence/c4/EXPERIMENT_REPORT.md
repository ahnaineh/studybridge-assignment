# C4 experiment report

## Final-code matched study — 20 October 2026, Beirut

The study now has a returned answer for all **47 planned setup/case pairs**.
There were **51 conversation attempts**: the 47-case matrix and four targeted
recovery attempts. The main matrix returned 43 answers; three conversations ended
with provider 503 errors and one with a provider 500 INTERNAL error. Each unanswered
case succeeded on its follow-up attempt. Original failed rows remain in the raw
files. These are conversation totals, not counts of individual API requests;
bounded retries inside a conversation are recorded in its trace.

Of the 47 returned answers, **46 passed the automated tool check**. The remaining
case proposed an example-only email; the runtime rejected that action, and the
final answer correctly asked for the missing email. The failed proposed action
is retained and scored as a model error rather than rewritten as a pass.

## Procedure and controls

The agent core used for this study is the guarded implementation, SHA-256
`507c32c1584c35387b924e3c09335fd65d3e27766f5729b65a847c5978a6227b`.
A later change only to the optional C3 reflection-review prompt is documented in
[the C3 reflection report](../c3-reflection/REPORT.md); the C4 execution path is unchanged.
The requested and reported model is `gemini-3.5-flash-lite`. Both personas allow
2048 output tokens. Friendly Advisor uses temperature 0.7, top-p 0.95 and top-k 40;
Course Specialist uses 0.2, 0.8 and 20. Package versions and Python version are
recorded in `balanced/environment.json`.

Both personas receive the same three comparison questions: beginner recommendation,
missing email and unknown refund policy. Each is tested with a one-example system
baseline, zero-shot, two-example few-shot, explicit stepwise prompting, in-message
instructions, and a detailed-instructions ablation. This gives 36 matched prompt
cases. Each baseline additionally tests prices, complete leads, explicit feedback
and history-based lead collection, adding eight functional cases. Three further
cases change only the specialist's temperature from 0.2 to 0.7, keeping its prompt,
top-p and top-k fixed: **47 planned cases in total**.

There is one repetition per setup/case. Three independent conversation workers share
one 13-second request-start lock. Each conversation has separate history/state.
Wall time includes queueing and service retries, so it is not used to rank model speed.

Recovery selects only unanswered server-error cases. A previously returned answer,
including a behavioral failure, is never rerun to obtain a better score. The selected
comparison uses the first returned answer per setup/case. Both the initial failures
and recovery rows are available in `balanced_scored_all_attempts.csv`; the selected
47 are in `balanced_selected.csv`. Recovery selection files and source snapshots
identify exactly what was run.

## Results on the three common cases

The table uses the same three cases for every row; the extra baseline functional
cases do not inflate its mean. Four criteria are each scored 0–2: grounded,
helpful, natural and instruction-following. These are assisting-agent qualitative
ratings of answers and tool observations, not independent human ratings. All 47
returned answers have explicit review notes in `balanced_review_notes.json`.
Provider-error attempts have no quality score.

| Persona / setup | Matched answers | Tool checks | Reviewed quality /8 |
|---|---:|---:|---:|
| Friendly Advisor / baseline | 3/3 | 3/3 | 8.00 |
| Friendly Advisor / zero_shot | 3/3 | 3/3 | 7.33 |
| Friendly Advisor / in_message | 3/3 | 2/3 | 6.67 |
| Friendly Advisor / instructions_ablation | 3/3 | 3/3 | 7.33 |
| Friendly Advisor / two_example_few_shot | 3/3 | 3/3 | 8.00 |
| Friendly Advisor / stepwise_reasoning | 3/3 | 3/3 | 8.00 |
| Course Specialist / baseline | 3/3 | 3/3 | 7.33 |
| Course Specialist / zero_shot | 3/3 | 3/3 | 7.67 |
| Course Specialist / in_message | 3/3 | 3/3 | 7.33 |
| Course Specialist / instructions_ablation | 3/3 | 3/3 | 7.33 |
| Course Specialist / two_example_few_shot | 3/3 | 3/3 | 8.00 |
| Course Specialist / stepwise_reasoning | 3/3 | 3/3 | 7.33 |
| Course Specialist / temperature_only_0.7 | 3/3 | 3/3 | 7.33 |

Both baseline personas also completed all seven functional cases after the provider
recovery: correct published prices, catalog recommendation, complete lead, missing
email, unknown policy, feedback and history-based lead collection. Each baseline
passed all seven tool checks.

## What the comparisons show

**Personas and sampling.** The advisor usually gives a short, warm recommendation;
the specialist gives structured scope, delivery and price details. My practical
preference for business enquiries is Course Specialist with two worked examples
in the system instructions. It scored 8/8 on the three common cases, but it ties
with several advisor setups. There is no uniquely established statistical winner.
The specialist's temperature-only control and its 0.2 baseline both averaged 7.33
on the common cases and passed all three tool checks. This small sample shows no
benefit from raising temperature; persona wording/top-p/top-k effects remain bundled.

**Direct versus stepwise prompt.** Both personas now have successful matched direct
and stepwise recommendation answers. All four recommend Python Starter using the
catalog. The advisor baseline first searched “programming”, received an empty result,
then recovered with “Python”; its stepwise run searched “Python” directly. This is
an observed difference in tool use, not proof that stepwise prompting generally
improves reasoning. Both conditions use the same manual ReAct loop. The treatment
changes the reasoning prompt, not the provider's thinking configuration; no private
chain-of-thought is requested or collected. Public traces expose decisions through
tool requests, observations and final answers.

**Zero-shot versus few-shot.** Zero, one and two examples all support correct catalog
recommendations. The second example specifically demonstrates an unknown refund
policy. Both personas' two-example refund answers follow that concise pattern and
avoid promising an unarranged personal callback. Several other refund replies log
the question correctly but imply follow-up without asking for contact details;
those receive reduced helpfulness/instruction scores. The specialist's zero-shot
recommendation is accurate but unnecessarily long. Examples help focus some answers,
but the data do not establish a general few-shot advantage across all tasks.

**System versus in-message.** In-message instructions work for most tested requests.
The advisor's missing-email case is the important exception: it proposes
`alex@example.com` from the worked example. The tool returns an error because that
email is absent from actual student messages. The model then asks for the email
and does not claim a save. Its trace is still a tool-check failure because forbidden
attempts count, even when blocked. This demonstrates why fluent final wording is
insufficient evidence of correct actions. One stochastic case cannot establish that
all in-message prompts are inferior.

**Instructions ablation.** Both personas still pass the three expected tool checks
when the detailed instructions are removed. The sources, tool schemas, persona and
runtime validation remain, so this is not an entirely unguided model. The experiment
does not show that instructions are unnecessary. It shows that these simple cases
can also be handled with the remaining guidance, while explicit instructions alone
cannot guarantee safe arguments without runtime validation.

## Evidence, reproduction and limits

- `balanced/20261019T210733396620Z/`: original 47-case matrix, configurations, cases,
  CSV, full public action/observation traces, source snapshots and synthetic logs.
- `balanced/20261019T213302425318Z/`: three unanswered 503 cases repeated successfully.
- `balanced/20261019T213552348462Z/`: the unanswered 500 case repeated successfully.
- `balanced_summary.json`, `balanced_review_notes.json`, `balanced_selected.csv`,
  `balanced_scored_all_attempts.csv`: derived, transparent review artifacts.
- `balanced/files_sha256.json`: hashes of the exported original evidence files.

Run `python experiments.py --balanced --workers 3` to repeat the matrix with a private
Gemini key. `--retry-errors-from CSV [CSV ...]` repeats only unanswered provider
500/503/504 cases. Run `python summarize_results.py` to reproduce the published
aggregates from the raw rows and review notes. New live runs are written under
`results/`; they do not overwrite the submitted evidence.

The earlier 68-attempt study and its report remain in `primary/`, `extension/` and
`EXPERIMENT_REPORT_PREVIOUS.md`. An interrupted sequential pilot is retained under
`balanced_initial/`. These are separate from the 51-attempt final study totals.

The final study closes the earlier missing matched comparisons and evaluates the
final guarded core. It remains a small qualitative coursework experiment: one
repetition, three common cases, subjective ratings and a single model. Recovery
completes behavioral coverage; it does not establish uninterrupted service reliability.
A tool check verifies expected/forbidden names; factual accuracy and arguments need
separate review. Partial writes can precede provider failures, and new conversations
can create duplicate records. The prototype does not book lessons, process payments
or guarantee callback times.
