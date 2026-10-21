from datetime import datetime
from pybaseball import statcast, playerid_lookup
from hitter_metrics import (
    calculate_avg_exit_velocity,
    calculate_hard_hit_rate,
    calculate_avg_launch_angle,
    calculate_barrel_rate
)

def get_date_range():
    while True:
        start_date = input("Enter start date (YYYY-MM-DD): ")
        end_date = input("Enter end date (YYYY-MM-DD): ")

        try:
            start_date_check = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_check = datetime.strptime(end_date, "%Y-%m-%d")

            if end_date_check < start_date_check:
                print("\nEnd date cannot be before start date. Try again.\n")
                continue

            return start_date, end_date

        except ValueError:
            print("\nInvalid date. Please use YYYY-MM-DD format.\n")

def get_player_id():
    first_name = input("Enter player first name: ")
    last_name = input("Enter player last name: ")

    player_lookup = playerid_lookup(
        last_name,
        first_name
    )

    if player_lookup.empty:
        print(f"\nNo player found for {first_name.title()} {last_name.title()}.")
        return None

    player_id = player_lookup.iloc[0]["key_mlbam"]

    return player_id, first_name, last_name

def generate_hitter_report(player_data, first_name, last_name):
    if player_data.empty:
        print(
            f"\n{first_name.title()} {last_name.title()} "
            "has no data in the selected date range."
        )
        return
    
    avg_ev = calculate_avg_exit_velocity(player_data)
    hard_hit_rate = calculate_hard_hit_rate(player_data)
    avg_launch_angle = calculate_avg_launch_angle(player_data)
    barrel_rate = calculate_barrel_rate(player_data)

    batted_ball_count = len(
        player_data[player_data["launch_speed"].notna()]
    )

    print("\nDIAMONDIQ HITTER REPORT")
    print("-----------------------")
    print(f"Player: {first_name.title()} {last_name.title()}")
    print(f"Batted Balls: {batted_ball_count}")
    print(f"Average EV: {avg_ev:.1f} mph")
    print(f"Hard-Hit Rate: {hard_hit_rate:.1f}%")
    print(f"Barrel Rate: {barrel_rate:.1f}%")
    print(f"Average Launch Angle: {avg_launch_angle:.1f} degrees")

def main():
    start_date, end_date = get_date_range()

    print("\nDownloading Statcast data...")

    data = statcast(
        start_dt=start_date,
        end_dt=end_date
    )

    print("Download complete!")

    player_result = get_player_id()

    if player_result is None:
        return

    player_id, first_name, last_name = player_result

    player_data = data[
        data["batter"] == player_id
    ]

    generate_hitter_report(
        player_data,
        first_name,
        last_name
    )

if __name__ == "__main__":
    main()