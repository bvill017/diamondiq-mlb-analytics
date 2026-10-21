from datetime import datetime
from pybaseball import statcast_batter, playerid_lookup
from hitter_metrics import (
    get_batted_balls,
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

def get_player():
    first_name = input("Enter player first name: ")
    last_name = input("Enter player last name: ")
    player_id = input("Enter player MLBAM ID: ")

    try:
        player_id = int(player_id)
    except ValueError:
        print("\nPlayer ID must be a number.")
        return None

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

    batted_balls = get_batted_balls(player_data)
    batted_ball_count = len(batted_balls)

    if batted_ball_count < 25:
        sample_size = "Small Sample"
    elif batted_ball_count < 100:
        sample_size = "Moderate Sample"
    else:
        sample_size = "Large Sample"

    plate_appearances = player_data["events"].notna().sum()

    print("\nDIAMONDIQ HITTER REPORT")
    print("-----------------------")
    print(f"Player: {first_name.title()} {last_name.title()}")
    print(f"Plate appearances: {plate_appearances}")
    print(f"Batted Balls: {batted_ball_count}")
    print(f"Average EV: {avg_ev:.1f} mph")
    print(f"Hard-Hit Rate: {hard_hit_rate:.1f}%")
    print(f"Barrel Rate: {barrel_rate:.1f}%")
    print(f"Average Launch Angle: {avg_launch_angle:.1f} degrees")
    print(f"Sample Size: {sample_size}")

def main():
    player_result = get_player()

    if player_result is None:
        return

    player_id, first_name, last_name = player_result
    
    start_date, end_date = get_date_range()

    print("\nDownloading Statcast data...")

    player_data = statcast_batter(
        start_date,
        end_date,
        player_id
    )

    print("Download complete!")

    generate_hitter_report(
        player_data,
        first_name,
        last_name
    )

if __name__ == "__main__":
    main()