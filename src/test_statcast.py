from pybaseball import statcast
print("Downloading Statcast data...")
data = statcast(
    start_dt="2026-06-01",
    end_dt="2026-06-02"
)
print("Download complete!")

print("\nFirst 5 rows:")
print(data.head())

print("\nDataset shape:")
print(data.shape)

print("\nColumns:")
print(data.columns.tolist())

print("\nFastest pitches:")

fastest_pitches = data[
    ["player_name", "pitch_type", "release_speed"]
].sort_values(
    by="release_speed",
    ascending=False
)

print(fastest_pitches.head(10))

print("\nHighest average four-seam velocity:")

four_seamers = data[data["pitch_type"] =="FF"]

avg_fastball_velocity= (
    four_seamers
    .groupby("player_name")["release_speed"]
    .agg(["mean", "count"])
    .sort_values(by="mean", ascending=False)
)

avg_fastball_velocity = avg_fastball_velocity[
    avg_fastball_velocity["count"] >= 10
]

print(avg_fastball_velocity.head(10))