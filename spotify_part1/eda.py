"""Run `python eda.py` to reproduce quick data audit and EDA figures."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
root = Path(__file__).resolve().parent
m = pd.read_csv(root/'track_metadata.csv', parse_dates=['release_date'])
a = pd.read_csv(root/'audio_features.csv')
c = pd.read_csv(root/'chart_longevity_panel.csv')
d = m.merge(a, on='track_id', validate='one_to_one').merge(c, on='track_id', validate='one_to_one')
print('Tables:', m.shape, a.shape, c.shape, 'Merged:', d.shape)
print('\nData types:\n', d.dtypes.to_string())
print('\nMissing counts:\n', d.isna().sum().to_string())
print('\nGenre breakdown:\n', d.genre.value_counts().to_string())
print('\nSummary:\n', d[['total_streams_mil','weeks_on_top_100','peak_chart_rank','danceability','energy']].describe().round(2))
print('\nCorrelation:\n', d[['total_streams_mil','weeks_on_top_100']].corr())
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
d.total_streams_mil.hist(bins=30, ax=axes[0]);axes[0].set(title='Cumulative streams distribution', xlabel='Million streams')
d.plot.scatter(x='weeks_on_top_100', y='total_streams_mil', alpha=.45, ax=axes[1]);axes[1].set(title='Longevity vs total streams', xlabel='Weeks in Top 100', ylabel='Streams (millions)')
fig.tight_layout();fig.savefig(root/'eda_overview.png', dpi=140)
print('Saved eda_overview.png')
