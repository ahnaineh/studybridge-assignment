# Video recording checklist

Record a short screen walkthrough in your own voice. Use synthetic contact details.

1. Show the GitHub repository and business PDF. Explain that StudyBridge is a fictional bilingual tutoring service.
2. Open business_agent.ipynb in Colab. Briefly show the separate persona, atomic instructions, router, source loading, and the two required logging tools.
3. Configure your key through Colab Secrets or the hidden prompt; never show it on screen. Set RUN_LIVE_DEMO and START_DEMO to True when needed.
4. In Gradio select C3. Ask the lesson/package price (USD20/USD72). Ask which course suits a programming beginner (Python Starter).
5. Say “My name is Alex. I want Python tutoring. Please contact me.” Then supply alex@example.com. Show the successful record_customer_interest observation and explain that it records interest, not a booking.
6. Ask “Can I get a refund if I cancel a lesson?” Show record_feedback and the answer that the published profile has no refund policy. Also demonstrate explicit feedback.
7. Open react_agent.ipynb. Show the manually defined LangGraph reason/act/answer/limit nodes and edges. Explain that automatic SDK tool execution is disabled.
8. Show the two persona prompts and settings. Select C4 in Gradio and compare the same question after clearing the chat each time.
9. Show the saved comparison table and reflection. Explain zero-shot, worked examples, system/in-message placement, and the stepwise-reasoning prompt. Mention provider errors separately from behavior failures and show the example-email guard fix.
10. End with the repository URL and what you learned. Upload the recording to the course's accepted destination and submit its link alongside the repository.

If Gemini is temporarily unavailable, show the saved real traces and retry later for the live demonstration. Do not describe a saved result as a new live run.
