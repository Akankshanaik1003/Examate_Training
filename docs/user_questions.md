# CaneMitra: 10 User Questions

Real questions a sugarcane farmer might ask, checked against CaneMitra's data (`data/sample_records.json` with 16 MPKV records and `data/records.json` with 42 TNAU records).

**What the data contains:** variety name, release year (MPKV only), institute, recommended seasons (adsali / preseasonal / suru), cane yield in t/ha per season, duration in months per season, key traits (disease, drought, salinity, jaggery quality, ratooning), state and source URL.

**What it does not contain:** fertilizer doses, pest and disease control methods, weather, market price or FRP, factory dates, payments, planting calendar months for each season.

| # | Question | Who asks | Can our data answer? | Data source / gap |
|---|----------|----------|----------------------|-------------------|
| 1 | How many months does Phule 265 take if I plant suru season? | Farmer planning the harvest | **Yes** | V10 Phule 265: duration 12 to 14 months for suru (14 to 16 preseasonal, 16 to 18 adsali) |
| 2 | Which sugarcane variety is best for jaggery (gur) making in Maharashtra? | Farmer with a gur unit | **Yes** | V13 Phule 09057 (recommended for jaggery), V11 Co 92005 (higher jaggery yield than Co 86032 and Co 8014), V07 Mahalaxmi, V01 Co 419 (excellent jaggery quality) |
| 3 | Which variety can I grow in saline (khara) soil? | Farmer with salty soil | **Yes** | V10 Phule 265 and V12 Phule 10001 (saline tolerant), V02 Co 740 (salinity tolerant); TNAU T41 is saline tolerant but is a Tamil Nadu variety |
| 4 | What is the yield of Phule 265 in adsali compared to suru? | Farmer comparing seasons | **Yes** | V10: adsali 200 t/ha, preseasonal 164, suru 150 |
| 5 | Which varieties tolerate drought? | Farmer in a low-rainfall area | **Yes** | MPKV: V02, V06, V09, V12, V15 mention drought tolerance; TNAU also has several (for example T18, T27, T33) |
| 6 | What fertilizer dose (NPK) should I give Phule 265 per acre in medium-deep black soil? | Farmer with 4 acres near Kopargaon | **No** | Our records have no fertilizer or nutrient data. The records only describe variety traits. Needs an agronomy source (for example the MPKV package of practices) |
| 7 | Mere khet ka pani thoda khara hai, kaunsi variety lagau? | Farmer (Hindi/Hinglish) | **Yes** | Same as Q3: V10, V12, V02 (salinity or saline tolerant) |
| 8 | Preseasonal lagwad kadhi karaychi? | Farmer (Marathi, planting time) | **Partly** | We know which varieties suit preseasonal and how long they take, but the data has no planting months. The month rules in `day01_menu.py` are unverified |
| 9 | Mi Phule 265 October madhe lavla, todni kadhi karu? | Farmer asking for a harvest date | **Partly** | Duration is in the data (preseasonal 14 to 16 months), so a window can be worked out. A harvest-window feature is not built yet |
| 10 | Aaj sugarcane cha bhav / FRP kiti aahe? | Farmer checking price | **No** | No price or FRP data. This needs a live government or factory source |

