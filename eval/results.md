# Day 8 eval results

| Config | Chunk size | Top-k | Chunks | Retrieval hit | Answer correct | Correct "I don't know" | With citations | Overall | Avg sec/question |
|---|---|---|---|---|---|---|---|---|---|
| A | 120 words | 3 | 139 | 6/12 (50%) | 4/12 (33%) | 3/3 (100%) | 5/12 (42%) | 7/15 (47%) | 5.35 |
| **B (winner)** | 250 words | 5 | 64 | 9/12 (75%) | 6/12 (50%) | 3/3 (100%) | 7/12 (58%) | 9/15 (60%) | 14.77 |

## Per question

| Row | Type | Question | A | B |
|---|---|---|---|---|
| q01 | answerable | Which sugarcane varieties are recommended for the adsali season? | FAIL | FAIL |
| q02 | answerable | Which variety is suitable for saline or alkaline soils? | pass | pass |
| q03 | answerable | Name a sugarcane variety that tolerates drought. | FAIL | FAIL |
| q04 | answerable | In which seasons is Phule 09057 recommended? | FAIL | FAIL |
| q05 | answerable | What is the duration of Phule 13007 in months? | FAIL | pass |
| q06 | unanswerable | What is today's sugarcane price per tonne at the Kolhapur market? | pass | pass |
| q07 | answerable | Which varieties are recommended for pre-seasonal planting? | FAIL | FAIL |
| q08 | answerable | What is the CCS percentage of Co 86032? | pass | pass |
| q09 | answerable | Which institute released the Phule sugarcane varieties? | pass | FAIL |
| q10 | unanswerable | Which fertilizer brand is giving the best discount this month? | pass | pass |
| q11 | answerable | Which varieties are resistant to red rot? | FAIL | pass |
| q12 | answerable | What yield does Phule 09057 give? | FAIL | pass |
| q13 | answerable | Which varieties are suitable for ratoon crops? | pass | pass |
| q14 | unanswerable | How do I grow wheat in Punjab? | pass | pass |
| q15 | answerable | Which varieties are suitable for waterlogged or flood-prone fields? | FAIL | FAIL |
