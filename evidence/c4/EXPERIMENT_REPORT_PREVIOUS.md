# C4 experiment report

The primary experiment ran in Google Colab on 13 October 2026 using the fixed
requested/reported model `gemini-3.5-flash-lite`, Google Gen AI SDK 1.75.0,
LangGraph 1.2.15 and a 13-second minimum request interval. There was one repetition.
The original source snapshot is included under `primary/source/`.

Of 60 attempted conversations, 20 returned answers and 40 ended with provider
503/504 errors. Of the 20 returned answers, 19 passed the automated tool-name
check. Provider-error rows have blank quality scores; they are not counted as
persona mistakes. Partial tool writes could precede an API failure.

| Setup | Responses / attempts | Tool passes among responses | Mean quality /8 |
|---|---:|---:|---:|
| Friendly Advisor / baseline | 2/7 | 2/2 | 6.50 |
| Friendly Advisor / zero-shot | 3/7 | 3/3 | 7.33 |
| Friendly Advisor / planning cue | 1/7 | 1/1 | 6.00 |
| Friendly Advisor / in-message | 3/7 | 2/3 | 6.00 |
| Friendly Advisor / instruction ablation | 1/2 | 1/1 | 6.00 |
| Course Specialist / baseline | 5/7 | 5/5 | 8.00 |
| Course Specialist / zero-shot | 3/7 | 3/3 | 8.00 |
| Course Specialist / planning cue | 1/7 | 1/1 | 8.00 |
| Course Specialist / in-message | 1/7 | 1/1 | 8.00 |
| Course Specialist / instruction ablation | 0/2 | — | — |

Quality scores are an assisting-agent review of answers and action observations
using the four 0–2 criteria in README.md. They are not independent human ratings.
`primary_scored.csv` adds scores without changing the original raw CSV.

Course Specialist's successful answers are generally concise and avoid the
advisor's unsupported promises of quick follow-up. Its baseline is a reasonable
prototype default, but unequal case coverage prevents a statistically reliable
ranking. Zero-shot often succeeded too; this sample does not prove an example
improves performance. The ablation retains sources/tool documentation and has
only one returned answer, so instruction effectiveness cannot be quantified here.

The important behavioral failure is Friendly Advisor / in-message / missing_email.
It saved the example email even though the student had supplied none. The final
answer asked for an email and concealed the save. The trace, rather than fluent
wording, exposed this issue. The submitted implementation adds a source-provenance
check before a lead save. The raw old failure remains visible, and its regression
check rejects that attempted action. The primary evaluation is of the earlier
implementation; it is not presented as a full rerun of the final patch.

A separate focused extension covers two worked examples and explicit internal
stepwise reasoning. Its source snapshot and original rows are retained separately.
No private chain-of-thought is collected. Provider thinking configuration is held
unchanged; the condition changes the prompt, not the underlying thinking budget.

## Focused extension results

The extension attempted eight conversations on the same fixed Flash Lite model,
with bounded generation retries introduced after the primary run. Five returned
answers and three ended with provider 503 errors. All five returned answers passed
the tool-name check and received 8/8 in the qualitative review. The final
lead-provenance guard was added after the extension source snapshot, so these
runs also do not constitute a complete reevaluation of the final patch.

| Condition | Case | Friendly Advisor | Course Specialist |
|---|---|---|---|
| Two-example few-shot | Complete lead | Correct lead; no booking claim | Correct lead; no booking claim |
| Two-example few-shot | Unknown refund policy | Provider error | Provider error |
| Internal stepwise reasoning | Beginner recommendation | Python Starter; correct catalog call | Empty search recovered; correct catalog answer |
| Internal stepwise reasoning | Unknown refund policy | Provider error | Original question logged; no invented refund policy |

For Course Specialist's complete-lead case, zero-shot, one-example baseline and
two-example few-shot all returned correct results. This matched example does not
show an advantage from adding examples. Both stepwise recommendation answers used
the catalog, and the specialist recovered from an empty “programming” search by
querying “Python”. However, the primary non-stepwise recommendation attempts all
ended with provider errors. There is no matched successful baseline answer from
which to infer a reasoning-prompt improvement. The planning-cue condition had
successful missing-email/unknown-policy answers but very limited coverage.

Across both runs there are 68 attempts, 25 returned answers, 43 provider failures
and 24 tool-check passes among returned answers. The original runs are not merged
into an apparent single identical procedure: retry policy changed for the
extension. One repetition, unequal coverage, assistant-assigned scores and
provider instability limit causal conclusions. A practical default is the
specialist's full system instructions; a strong experimental winner is not established.

## Live check of the final patch

A separate post-patch Colab conversation used Friendly Advisor with in-message
instructions and the same missing-email request. Gemini again attempted to save
alex@example.com from the example. The runtime rejected the call because the email
was absent from actual student messages. After receiving that error observation,
the model asked for the missing email and did not claim that a lead had been saved.
One 503 retry occurred during the final generation; it did not repeat the action.
The trace is in `evidence/final-contact-check.json`. This confirms the protective
behavior on the demonstrated live case; it does not establish that the model
stopped hallucinating arguments. This check is separate from the 68-study totals.
