# C4 reflection

## 1. Which persona was most helpful or natural?

Friendly Advisor felt more natural for a student who is unsure where to start. Its
recommendations were usually short, warm and easy to follow. Course Specialist was
more useful for comparing the business's services because it gave structured scope,
pricing and delivery details. For this business I prefer the specialist with two
worked examples, especially when answering questions about missing policies. This
is a preference based on the recorded answers, not a claim that its temperature is
always better.

## 2. Which prompt and configuration combination performed best?

My preferred tested setup is Course Specialist with system instructions, two examples,
temperature 0.2, top-p 0.8 and top-k 20. It passed all three common tool checks and
received 8/8 in the qualitative review. The refund example produced a clear answer
that admitted the missing policy without promising an unarranged callback. Several
advisor setups also scored 8/8, so there is a tie rather than one proven winner.
The specialist's zero-shot answer was accurate but rather long. Raising only its
temperature to 0.7 did not improve the common-case average or tool checks.

The final matrix contains 47 setup/case pairs. Four unanswered provider-error cases
were repeated, giving 51 conversation attempts and 47 returned answers. Every setup
now has the same three comparison cases. The earlier study had too many missing
responses for a balanced comparison, so I kept it separately. Ratings were supplied
by the assisting coding agent from the answers and traces; they are not independent
human judgments. One repetition is not enough for strong statistical conclusions.

The preferred configuration can be selected with
`c4_reply(message, persona="Course Specialist", fewshot_extra=True)`.
The Gradio interface demonstrates the one-example baseline, while the notebook and
experiment runner expose the other tested conditions.

## 3. How well did the agent reason and use tools?

The LangGraph loop detects native function calls, executes the named tool, returns
its observation and continues until there is a final answer. Both personas correctly
used history to combine an earlier name and Python interest with a newly supplied
email. They saved the lead and explained that this was not a booking. The catalog
trace also shows recovery from an empty “programming” search by searching for “Python”.
Direct and stepwise recommendation conditions both returned correct matched answers;
this sample does not show that the reasoning prompt was necessary.

The most useful failure was Friendly Advisor with in-message instructions. It tried
to save the example email when the student had supplied none. The runtime rejected
that call, and the model then asked for the missing email. I kept the proposed action
as a failure even though the final response was helpful: 46 of 47 returned answers
passed the tool check. The earlier unguarded failure is also retained. This taught
me to inspect tool arguments and observations, not only the final wording. The
stepwise treatment requests internal deliberation; I evaluate public actions and
answers rather than collecting private chain-of-thought or claiming to switch the
provider's underlying thinking mechanism.

## 4. Did the instructions block change behavior?

The instructions make the expected inputs, outputs, lead fields and unknown-policy
handling explicit. The worked refund example made those replies more focused in
both personas. However, removing the detailed block still left the business sources,
tool descriptions, persona and validation in place. Both ablated personas passed
the three tool checks, so I cannot say that the instruction block alone caused the
correct behavior. Some setups implied that the team would follow up without contact
details; those replies lost review points. The example-email attempt also shows that
written instructions need support from validation at the tool boundary.

## 5. What were the biggest implementation challenges?

Native tool-response formatting was the first challenge: Gemini needed observations
in user-role Content, and the original model Content had to be preserved with its
identifiers and signatures. Gradio also required structured history handling. Service
availability made evaluation slow. I used request pacing, bounded generation retries,
a shared request-start lock for independent conversations, and explicit recovery of
unanswered server-error cases. I did not repeat answered behavioral failures to obtain
a better score. Every original attempt, configuration and public trace remains visible.

The contact-provenance guard was another important fix. It checks that a proposed
name and email occur in actual student messages before persisting a lead. Eleven
offline regression tests passed again, and the final live matrix exercised that guard.
The system is still a coursework prototype: JSONL logs and recent chat history do not
provide a booking system, permanent conversation memory or global deduplication. A
larger repeated study would be needed to make stronger claims about prompt quality.
