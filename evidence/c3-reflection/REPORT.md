# C3 optional reflection bonus

Completed on 20 October 2026 (Beirut time; 19 October UTC) using Gemini
`gemini-3.5-flash-lite` in Colab. The optional `c3_reply(..., reflection=True)`
pass reviews the original draft against the business sources and instructions
before returning a revised customer-facing answer. It writes both versions to
`reflection.jsonl`. The review has temperature 0.1 and no tools.

## Executed examples

1. **Natural live draft and live review:** [live-example.json](live-example.json).
   Both generations are actual Gemini outputs. The draft correctly calculated
   four individual lessons at USD 80 versus the USD 72 package, saving USD 8.
   Its “no booking required” wording was replaced with a distinction between
   expressing interest/booking a consultation and a confirmed lesson booking.
   This is a wording revision, not evidence of an arithmetic error in the live draft.
2. **Controlled error-correction test:** [controlled-correction.json](controlled-correction.json).
   The first draft was deliberately seeded with USD 100 for four individual
   lessons, USD 28 savings and an invented guaranteed refund. The real Gemini
   reflection corrected these to USD 80 and USD 8 and stated that refund details
   are not in the business profile. It asked whether to log the policy question;
   no feedback tool was executed and no save was claimed. This is a controlled
   test, not a naturally observed model failure.

The complete original and revised text is visible in the C3 notebook and the
linked JSON files. Raw post-fix logs are in [logs/reflection.jsonl](logs/reflection.jsonl)
and [logs/traces.jsonl](logs/traces.jsonl). No contact details or API keys are used.

## Initial test and narrow fix

The initial natural example only standardized currency wording. The initial
controlled test returned tool-call JSON as text instead of a public answer.
Both original records are retained in [pre-fix/](pre-fix/). The review inherited
the normal tool-routing instructions even though this final review cannot
execute tools. A review-specific instruction now states that tools are
unavailable, prohibits tool JSON/code, requires a plain customer-facing answer,
and tells it to correct unsupported facts without claiming unexecuted actions.
The two examples were then rerun once with the fix; the failed trial is not hidden.

Only the optional C3 reflection review prompt changed. The C4 execution path and
its recorded comparison results remain unchanged. The C4 source snapshots still
identify the exact code used for that study. The post-fix root core SHA-256 is
`2096efba06f16438737bf00e241ac0390d80aafad22f153ca2d4386900ce2525`.

## Repeat and limits

From the repository root, after configuring a private `GEMINI_API_KEY`, run:

```bash
python evidence/c3-reflection/run_reflection.py
```

This uses real API calls, preserves submitted evidence, and saves each repeat in
an ignored `logs/reflection-repeat-<timestamp>/` directory. Tool steps may require
additional calls. The controlled test uses a scripted first response and a live
review through the same unchanged reflection control flow. Results can vary.
These two examples demonstrate the optional pass; they do not prove that every
future factual or instruction error will be caught. The review cannot repair a
missed tool write, and it adds latency and API usage.
