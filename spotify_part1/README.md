# Daily Playlist Curation Dashboard — BANA409 Assignment 4, Part 1

**Owner:** [YOUR NAME]  
**Team:** [YOUR TEAM NAME]  
**Live app:** [ADD YOUR DEPLOYED STREAMLIT URL]  
**Original Kaggle dataset page:** [ADD ORIGINAL DATASET URL — check with your team]

## Step 1 — Data and decision-maker

This dashboard serves a **music streaming platform's playlist curator**, the person who creates or refreshes the platform's general Daily Recommendations playlist. The specific decision is **which songs deserve manual review for tomorrow's playlist**; this is not an individualized recommendation algorithm.

The provided dataset contains 1,200 songs with release dates from January 2018 through June 2026. Each row represents one unique track, identified by `track_id`. Three tables are joined one-to-one: `track_metadata.csv` (track, artist, genre, release date, explicit flag, duration), `audio_features.csv` (danceability, energy, tempo and other features), and `chart_longevity_panel.csv` (peak chart rank, Top 100 weeks, cumulative streams and other chart metrics). There are eight genres. All 1,200 IDs match across files, and the supplied tables contain no missing values.

**Provenance limitation:** The supplied datasheet describes derived/aggregated analytics but does not identify the original streaming provider, acquisition procedure, chart territory, or exact measurement cutoff. Track titles and artist names are generic labels (e.g., “Hit Song 1”), suggesting the dataset may be synthetic or anonymized. We therefore use it to demonstrate a hypothetical curator's workflow and do not present results as verified live Spotify performance. The original dataset link needs to be filled in from the team's source page.

## Step 2 — Why an interactive dashboard?

The curator would consult the dashboard **each morning before drafting the next playlist**. The operating rule is: **If the curator sees a song with sustained Top 100 presence and substantial historical streams, they will shortlist it for editorial review; they will then check whether it fits the playlist's genre, content policy and current audience.**

Without a common view, the curator might switch between spreadsheets, sort performance measures separately, and accidentally shortlist a track that violates the playlist's explicit-content policy. A weekly email or a fixed report cannot easily answer different genre/content requirements each day; an interactive dashboard lets the curator adjust thresholds and inspect a consistent shortlist immediately. It is not a substitute for current engagement data or human editorial review.

## Step 3 — KPI, chart and filter choices

**Top: Three KPIs**

1. **Eligible songs:** size of the review queue after all filters. Helps judge whether thresholds are too strict or too broad.
2. **Median Top 100 weeks:** describes chart durability of the currently eligible pool. The median limits the impact of unusual long-running songs.
3. **Median cumulative streams (millions):** describes historical scale of reach of the same pool. Median is less skewed by blockbuster outliers.

**Middle: Two supporting charts**

- **Median historical streams by genre:** lets the curator check whether the candidate pool's historical reach differs by genre; accompanied by eligible-track counts on hover.
- **Top 100 weeks versus cumulative streams:** shows whether long-standing chart success coincides with large historical reach, and makes unusual candidates easier to spot. Each point is a track, colored by genre.

**Decision-relevant filters:** genre selection, an explicit-content toggle, minimum historical chart weeks, and minimum cumulative streams. These match plausible daily playlist constraints. All headline metrics and visualizations recalculate from eligible tracks.

**Bottom:** an exportable candidate table. The ordering is transparent: most historical Top 100 weeks first, with lifetime streams as a tie-breaker. Peak rank, danceability and energy are shown here for a closer manual check, not presented as an unvalidated single numerical “recommendation score.”

**Deliberately excluded:**

- **Tempo and musical key charts:** musically interesting but do not directly answer which broadly appealing tracks have demonstrated staying power; adding them would distract from the decision. Audio features are not treated as proof of fit for every listener.
- **`is_viral_hit` / `longevity_score` headline cards:** their calculation is not documented in the supplied data dictionary, making them easy to overinterpret as an independent prediction or objective recommendation metric.

**Potentially misleading information:** Cumulative streams and chart weeks are **historical totals**, not today's trending momentum; recently released songs have had less time to accumulate them. The dashboard explicitly labels those measures, shows dates and peak rank in the detail table, and warns against using the sort order as an unbiased forecast. There is no listening-level personalization, skip rate, or current engagement measurement. With anonymized/generic identifiers, specific songs also require external verification before real-world action.

**Page order:** A decision statement and data-freshness caveat come first; three headline metrics summarize the filtered opportunity pool; two charts provide comparison/context; an actionable ranked shortlist comes last for the curator who needs concrete tracks.

## Step 4 — Refresh, cadence, action trigger and stale-data risk

The **real production dashboard should refresh nightly**, after the previous day's streaming and chart data become available, because the curator assembles the next playlist in a daily cycle. The **curator reviews it each morning**; refreshing every minute would add complexity without changing that daily decision. The **current assignment CSV is frozen**: this demo never claims automatic live updates. The visible date span reflects **track release dates**, not a guaranteed end date for chart/stream measurements.

In a real deployment, I would add **prior-day and seven-day streams** and watch for a **20% week-over-week fall in seven-day streams for any song currently on the playlist**. That would trigger a same-day editorial review of the song for possible replacement; it is a proposed business rule, not something calculable from the available historical totals. If the daily feed were a day late, yesterday's unexpected breakout might be overlooked; if it were a week late, a declining track could remain featured through several daily releases. Because the current data lacks daily timestamps, **the trigger is documented, not implemented**.

## Step 5 — Run and deploy

Run locally:

```bash
uv init --bare .   # optional if creating a new project; do not overwrite existing files
uv venv --python 3.14
uv pip install -r requirements.txt
uv run --python 3.14 streamlit run app.py
```

Or, with an existing Python environment:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The repository needs `app.py`, the three CSV files, `requirements.txt`, `.python-version` and this `README.md`. Publish it under **your own GitHub account** and deploy from that repository under **your own Streamlit Community Cloud account**. Streamlit's **Main file path** is `app.py`; in Advanced settings use **Python 3.14**, as required by the assignment. Replace the placeholders in this README and the team-name caption in `app.py` before submitting. Put both URLs in the first Markdown cell of `phone-trade-in.ipynb` for the full Assignment 4 submission.

## Minimal EDA audit

The provided raw tables have 1,200 unique tracks each, one-to-one join keys and no missing cells. Genre sizes: Pop 318, Hip-Hop 221, Dance/Electronic 175, R&B 128, Indie/Alternative 124, Rock 109, Latin 66, K-Pop 59. Historic Top 100 weeks range from 5 to 102 (median 18); total streams range from 9.99M to 1,467.02M (median 280.99M). Top 100 weeks and lifetime streams have a weak sample Pearson correlation (~0.017), motivating the two-dimensional chart rather than assuming one automatically implies the other. The reproducible EDA script is `eda.py`.
