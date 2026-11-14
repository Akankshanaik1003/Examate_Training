# Prompt comparison: v1 vs v2

- **v1** (`prompts/system_v1.md`): short role prompt, asks for JSON, no rule about what to do when the records do not answer.
- **v2** (`prompts/system.md`): adds rules: use only the records, say "not in my records" instead of guessing, quote exact numbers, mark TNAU as Tamil Nadu, same language as the question, defined confidence levels.

Same 10 questions from `docs/user_questions.md`, same retrieved records, same model. Answers below were produced by running `python -m eval.prompt_compare`.

| # | Question | Data can answer? | v1 answer (confidence) | v2 answer (confidence) | Better | Why |
|---|----------|------------------|------------------------|------------------------|--------|-----|
| 1 | How many months does Phule 265 take if I plant suru season? | Yes | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 2 | Which sugarcane variety is best for jaggery (gur) making in Maharashtra? | Yes | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 3 | Which variety can I grow in saline (khara) soil? | Yes | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 4 | What is the yield of Phule 265 in adsali compared to suru? | Yes | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 5 | Which varieties tolerate drought? | Yes | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 6 | What fertilizer dose (NPK) should I give Phule 265 per acre in medium-deep black soil? | No | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 7 | Mere khet ka pani thoda khara hai, kaunsi variety lagau? | Yes | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 8 | Preseasonal lagwad kadhi karaychi? | Partly | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 9 | Mi Phule 265 October madhe lavla, todni kadhi karu? | Partly | ERROR: gemini timed out after 30s (-) | ERROR: gemini timed out after 30s (-) |  |  |
| 10 | Aaj sugarcane cha bhav / FRP kiti aahe? | No | ERROR: gemini timed out after 30s (-) | ERROR: gemini returned HTTP 429: You exceeded your current quota, please check your plan and billing details. For more information on this error, head to: https://aistudio.google.com/docs/rate-limits. To monitor your current usage, h (-) |  |  |

## My verdict

_Fill in after reading the table: which prompt is better, and what did Q6 and Q10 (not in the data) show?_
