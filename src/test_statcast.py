import time
from datetime import datetime
from pybaseball import statcast, playerid_lookup
from hitter_metrics import (
    calculate_avg_exit_velocity,
    calculate_hard_hit_rate,
    calculate_avg_launch_angle,
    calculate_barrel_rate
)


while True:
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")

    try:
        start_date_check = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_check = datetime.strptime(end_date, "%Y-%m-%d")

        if end_date_check < start_date_check:
            print("\nEnd date cannot be before start date. Try again.\n")
            continue

        break
    except ValueError:
        print("\nInvalid date. Please use YYYY-MM-DD format.\n")

print("Downloading Statcast data...")
data = statcast(
    start_dt=start_date,
    end_dt=end_date
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
    
)

avg_fastball_velocity = avg_fastball_velocity[
    avg_fastball_velocity["count"] >= 10
]

avg_fastball_velocity = avg_fastball_velocity.sort_values(
    by="mean",
    ascending=False
)

print(avg_fastball_velocity.head(10))

avg_exit_velocity = calculate_avg_exit_velocity(data)

print("\nAverage Exit Velocity:")
print(f"{avg_exit_velocity:.1f} mph")

# hitters = (
#     data[data["launch_speed"].notna()]
#     .groupby("batter")
#     .size()
#     .sort_values(ascending=False)
# )

# print("\nHitters with the most batted balls:")
# print(hitters.head(10))

# hitter_ids = hitters.head(10).index.tolist()

# player_names = playerid_reverse_lookup(
#     hitter_ids,
#     key_type="mlbam"
# )

# print("\nPlayer lookup:")
# print(player_names)

hard_hit_rate = calculate_hard_hit_rate(data)

print("\nHard-Hit Rate:")
print(f"{hard_hit_rate:.1f}%")

first_name = input("\nEnter player first name: ")
last_name = input("Enter player last name: ")

lookup_start = time.time()

player_lookup = playerid_lookup(
    last_name,
    first_name
)

lookup_end = time.time()

print(f"\nPlayer lookup took {lookup_end - lookup_start:.2f} seconds.")

if player_lookup.empty:
    print(f"\nNo player found for {first_name.title()} {last_name.title()}.")
    exit()

player_id = player_lookup.iloc[0]["key_mlbam"]

player_data = data[data["batter"] == player_id]

if player_data.empty:
    print(
        f"\n{first_name.title()} {last_name.title()} "
        "has no data in the selected date range."
    )
    exit()

player_avg_ev = calculate_avg_exit_velocity(player_data)
player_hard_hit_rate = calculate_hard_hit_rate(player_data)
player_avg_launch_angle = calculate_avg_launch_angle(player_data)
player_barrel_rate = calculate_barrel_rate(player_data)

print("\nDIAMONDIQ HITTER REPORT")
print("-------------------------")
print(f"Player: {first_name.title()} {last_name.title()}")
print(f"Batted Balls: {len(player_data[player_data['launch_speed'].notna()])}")
print(f"Average EV: {player_avg_ev:.1f} mph")
print(f"Hard-Hit Rate: {player_hard_hit_rate:.1f}%")
print(f"Barrel Rate: {player_barrel_rate:.1f}%")
print(f"Average Launch Angle: {player_avg_launch_angle:.1f} degrees")