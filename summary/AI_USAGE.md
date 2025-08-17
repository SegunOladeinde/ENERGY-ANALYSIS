## AI Tools Used

- ChatGPT (OpenAI GPT-5) — main tool used for coding support, debugging, and documentation.

- Gemini Code Assist (VS Code extension) — used for code auto-completion inside VS Code.


 ## Good Prompt Example I Used:

"I need to create a Python function that fetches weather data from NOAA API
for multiple cities, handles rate limiting, implements exponential backoff
for retries, and logs all errors. The function should return a pandas
DataFrame with consistent column names regardless of the city."


"Create src/data_fetcher.py.

Load API keys from .env, city info from config/config.yaml.

Fetch last 90 days NOAA weather (TMAX/TMIN → °F) & EIA energy (daily totals).

Retry (exponential backoff), log errors to logs/pipeline.log.

Save to data/raw/:

Weather → date, city, tmax_f, tmin_f

Energy → date, city, energy_mwh

Use funcs: fetch_noaa_weather(), fetch_eia_energy(), save_raw_data().

Libraries: pandas, requests, logging, dotenv."


"Create src/analysis.py. Load cities from config/config.yaml, read each city’s processed weather & energy CSVs, merge on datetime, compute descriptive stats + correlation (temp vs energy). Structure with reusable functions (analyze_city), log progress, handle errors, use pandas. Save/print results."


"Create dashboards/app.py (Streamlit). Load processed CSVs from data/processed/, add sidebar city selector, show avg temp, avg energy, correlation, and plots (temp trend, energy over time, optional scatter). Use matplotlib/plotly + basic Streamlit styling."




## AI Mistakes Found & Fixed
Below are some of the issues i encounterd and how i fixed them.

### Issue:

. AI generated code that didn’t handle missing NOAA weather data correctly.

. It returned empty DataFrames without proper logging.

### Fix:

. I added explicit checks and warnings when API calls returned no data.

### Issue:

. AI initially suggested placing API keys directly in the Python scripts.

. This is insecure and not best practice.

### Fix:

. I corrected this by moving API keys into a .env file and loading them securely with dotenv.

### Issue:

. AI generated code didn’t follow the exact folder structure from the project documentation.

### Fix:

I reorganized the files (pipeline.py, analysis.py, dashboards/app.py) to match the required format.

## Time Saved

AI helped me cut down 65–75% of development time by writing boilerplate code, suggesting functions, and speeding up documentation. I spent the saved time on debugging, testing, and polishing the project.

## What I Learned

. AI is great for speed, but you can’t just copy-paste. You need to read, test, and debug.

. Debugging AI-generated code helped me understand error handling, environment variables, and structured project design.

. AI can accelerate learning, but real problem-solving still depends on me.






This way, my AI_USAGE.md shows that I didn’t just use AI — I learned from it, debugged it, and made the project production-ready.