"""BANA 409 Assignment 4 Part 1: daily playlist curation decision dashboard."""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Daily Playlist Curation | BANA409", page_icon="🎧", layout="wide")
DATA = Path(__file__).resolve().parent


@st.cache_data
def load_data():
    metadata = pd.read_csv(DATA / "track_metadata.csv", parse_dates=["release_date"])
    audio = pd.read_csv(DATA / "audio_features.csv")
    chart = pd.read_csv(DATA / "chart_longevity_panel.csv")
    for name, df in [("metadata", metadata), ("audio", audio), ("chart", chart)]:
        if df.track_id.isna().any() or df.track_id.duplicated().any():
            raise ValueError(f"Invalid track_id values in {name}")
    tracks = metadata.merge(audio, on="track_id", validate="one_to_one")
    tracks = tracks.merge(chart, on="track_id", validate="one_to_one")
    tracks["duration_min"] = (tracks.duration_ms / 60000).round(1)
    return tracks


df = load_data()
st.title("🎧 Daily Playlist Curation Dashboard — Team Zhang–Wang–Chen–Zhou")
st.caption("BANA409 · Team members: Zhang Jiayuan · Wang Sihan · Chen Jiayi · Zhou Zhenchen")
st.caption("For a music playlist curator choosing songs to shortlist for the next Daily Recommendations playlist")
st.info("**Decision:** Identify songs with strong historical reach and staying power, then review the shortlisted tracks before programming the playlist.")
st.caption(
    f"**Dataset:** Frozen snapshot of {len(df):,} tracks with release dates "
    f"{df.release_date.min():%b %Y}–{df.release_date.max():%b %Y}. "
    "Chart metrics are historical aggregates, **not current-day trends**. "
    "**Production proposal:** nightly refresh; curator review each morning. "
    "**This demo does not refresh automatically.**"
)

with st.sidebar:
    st.header("Curator filters")
    genres = sorted(df.genre.unique().tolist())
    chosen_genres = st.multiselect("Genres to consider", genres, default=genres)
    allow_explicit = st.checkbox("Include explicit tracks", value=True)
    min_weeks = st.slider("Minimum weeks in Top 100", 5, int(df.weeks_on_top_100.max()), 20)
    min_streams = st.slider("Minimum total streams (million)", 0, 1500, 200, step=25)
    st.caption("Thresholds are editorial preferences, not statistically trained recommendations.")

subset = df[df.genre.isin(chosen_genres)].copy()
if not allow_explicit:
    subset = subset[subset.is_explicit == 0]
qualified = subset[
    (subset.weeks_on_top_100 >= min_weeks)
    & (subset.total_streams_mil >= min_streams)
].copy()

# No learned model: transparent, auditable ordering by longevity then reach.
qualified = qualified.sort_values(
    ["weeks_on_top_100", "total_streams_mil", "track_id"],
    ascending=[False, False, True],
).reset_index(drop=True)
qualified.insert(0, "Shortlist rank", range(1, len(qualified) + 1))

k1, k2, k3 = st.columns(3)
k1.metric("Eligible songs", f"{len(qualified):,}", help="Songs meeting all selected editorial thresholds")
k2.metric(
    "Median chart weeks",
    f"{qualified.weeks_on_top_100.median():.0f}" if not qualified.empty else "—",
    help="Median historic weeks in the Top 100 among eligible songs",
)
k3.metric(
    "Median lifetime streams",
    f"{qualified.total_streams_mil.median():,.1f}M" if not qualified.empty else "—",
    help="Median historical aggregate streams among eligible songs (millions)",
)

st.subheader("Why these songs? Compare historical strength")
left, right = st.columns(2)
if qualified.empty:
    st.warning("No tracks match these filters. Try relaxing the thresholds or choosing more genres.")
else:
    genre_summary = (
        qualified.groupby("genre", as_index=False)
        .agg(median_streams=("total_streams_mil", "median"), eligible_songs=("track_id", "count"))
        .sort_values("median_streams", ascending=False)
    )
    with left:
        st.markdown("**Median lifetime streams by genre**")
        bars = alt.Chart(genre_summary).mark_bar(color="#3a9e87").encode(
            x=alt.X("median_streams:Q", title="Median historical streams (million)", scale=alt.Scale(zero=True)),
            y=alt.Y("genre:N", sort="-x", title=None),
            tooltip=[alt.Tooltip("genre:N", title="Genre"), alt.Tooltip("median_streams:Q", title="Median streams (M)", format=".1f"), "eligible_songs:Q"],
        ).properties(height=290)
        st.altair_chart(bars, use_container_width=True)
    with right:
        st.markdown("**Chart longevity vs. total streams**")
        dots = alt.Chart(qualified).mark_circle(opacity=0.65, size=65).encode(
            x=alt.X("weeks_on_top_100:Q", title="Historical weeks in Top 100", scale=alt.Scale(zero=False)),
            y=alt.Y("total_streams_mil:Q", title="Lifetime streams (million)", scale=alt.Scale(zero=False)),
            color=alt.Color("genre:N", title="Genre"),
            tooltip=["track_title:N", "artist_name:N", "genre:N", "weeks_on_top_100:Q", alt.Tooltip("total_streams_mil:Q", format=".1f")],
        ).properties(height=290)
        st.altair_chart(dots, use_container_width=True)
    st.caption("Both charts describe only the **filtered eligible songs**. Streams are accumulated totals; older tracks had longer to accrue them. Chart weeks and streams do not establish future recommendation success.")

st.subheader("Prioritized shortlist for editorial review")
st.caption("Ranked by **weeks in Top 100 (descending)**, then **total historical streams (descending)**. This is a simple editorial sorting rule, not a prediction or a personalized user score.")
show_cols = {
    "Shortlist rank": "Priority", "track_title": "Track", "artist_name": "Artist",
    "genre": "Genre", "release_date": "Released", "weeks_on_top_100": "Top 100 weeks",
    "total_streams_mil": "Streams (M)", "peak_chart_rank": "Best chart rank",
    "danceability": "Danceability", "energy": "Energy", "is_explicit": "Explicit (1=yes)",
}
top_n = st.selectbox("Rows to display", [10, 20, 50, 100], index=0)
st.dataframe(
    qualified[list(show_cols)].head(top_n).rename(columns=show_cols),
    use_container_width=True, hide_index=True,
    column_config={"Released": st.column_config.DateColumn(format="YYYY-MM-DD"), "Streams (M)": st.column_config.NumberColumn(format="%.1f"), "Danceability": st.column_config.NumberColumn(format="%.2f"), "Energy": st.column_config.NumberColumn(format="%.2f")},
)
st.download_button(
    "Download all eligible tracks (CSV)",
    qualified.to_csv(index=False).encode("utf-8"),
    file_name="daily_playlist_candidates.csv", mime="text/csv",
    disabled=qualified.empty,
)
st.caption("**Editorial caution:** Track and artist names appear anonymized/generic. Verify identity, rights, market fit, and recent listening behavior before publishing any actual playlist. No user-level preferences, skips, completion rates, or daily streams are available.")
