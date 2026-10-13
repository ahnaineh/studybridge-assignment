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
