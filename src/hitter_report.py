from multiprocessing import Process, Queue, freeze_support
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from pybaseball import statcast, statcast_batter
from hitter_metrics import (
    get_batted_balls,
    calculate_avg_exit_velocity,
    calculate_hard_hit_rate,
    calculate_avg_launch_angle,
    calculate_barrel_rate,
    calculate_difference,
    classify_metric
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

def get_cache_path(start_date, end_date):
    cache_folder = Path("data/cache")

    cache_file = cache_folder / (
        f"mlb_{start_date}_{end_date}.csv"
    )

    return cache_file

def statcast_worker(
        start_date,
        end_date,
        result_queue
):
    try:
        data=statcast(
            start_date,
            end_date
        )

        result_queue.put(
            ("success", data)
        )

    except Exception as error:
        result_queue.put(
            ("error", str(error))
        )

def statcast_with_timeout(
        start_date,
        end_date,
        timeout_seconds=300
):
    result_queue = Queue()

    process = Process(
        target=statcast_worker,
        args=(
            start_date,
            end_date,
            result_queue
        )
    )

    process.start()

    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()

        raise TimeoutError(
            f"Statcast request timed out after "
            f"{timeout_seconds} seconds."
        )

    if result_queue.empty():
        raise RuntimeError(
            "Statcast process ended without returning data."
        )

    status, result = result_queue.get()

    if status == "error":
        raise RuntimeError(result)

def download_statcast_in_chunks(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current_start = start
    chunks = []

    while current_start <= end:
        current_end = min(
            current_start + timedelta(days=6),
            end
        )

        chunk_start = current_start.strftime("%Y-%m-%d")
        chunk_end = current_end.strftime("%Y-%m-%d")

        chunk_cache = Path(
            f"data/cache/mlb_{chunk_start}_{chunk_end}.csv"
        )

        if chunk_cache.exists():
            print(
                f"Loading cached chunk "
                f"{chunk_start} to {chunk_end}..."
            )

            chunk_data = pd.read_csv(chunk_cache)

        else:
            print(
                f"Downloading {chunk_start} "
                f"to {chunk_end}..."
            )

            for attempt in range (1, 4):
                try:
                    chunk_data = statcast_with_timeout(
                        chunk_start,
                        chunk_end
                    )

                    chunk_data.to_csv(
                        chunk_cache,
                        index=False
                    )

                    print("Chunk cached!")
                    break

                except Exception as error:
                    print(
                        f"\nChunk download attempt {attempt} "
                        f"failed: {error}"
                    )

                    if attempt < 3:
                        print(
                            "Trying this chunk again "
                            "in 5 seconds..."
                        )
                        time.sleep(5)
                    else:
                        print(
                            f"\nUnable to download "
                            f"{chunk_start} to {chunk_end}."
                        )
                        return None
                    
        chunks.append(chunk_data)

        current_start = current_end + timedelta(days=1)

    return pd.concat(
        chunks,
        ignore_index=True
    )

def get_league_hard_hit_rate(start_date, end_date):
    cache_file = get_cache_path(start_date, end_date)

    if cache_file.exists():
        print("\nLoading MLB benchmark data from cache...")

        league_data = pd.read_csv(cache_file)

    else:
        print("\nDownloading MLB benchmark data...")

    league_data = download_statcast_in_chunks(
        start_date,
        end_date
    )

    if league_data is None:
        return None

    league_data.to_csv(
        cache_file,
        index=False
    )

    print("MLB benchmark data cached!")

    league_hard_hit_rate = calculate_hard_hit_rate(
        league_data
    )

    return league_hard_hit_rate

def generate_hitter_report(
        player_data,
        first_name,
        last_name,
        start_date,
        end_date
        ):
    if player_data.empty:
        print(
            f"\n{first_name.title()} {last_name.title()} "
            "has no data in the selected date range."
        )
        return
    
    avg_ev = calculate_avg_exit_velocity(player_data)
    hard_hit_rate = calculate_hard_hit_rate(player_data)

    league_hard_hit_rate = get_league_hard_hit_rate(
        start_date,
        end_date
    )

    if league_hard_hit_rate is not None:
        hard_hit_difference = calculate_difference(
            hard_hit_rate,
            league_hard_hit_rate
        )

        hard_hit_rating = classify_metric(
                hard_hit_rate,
                league_hard_hit_rate
        )
    else:
        hard_hit_difference = None
        hard_hit_rating = None

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
    if league_hard_hit_rate is not None:
        print(
            f"Hard-Hit Rate: {hard_hit_rate:.1f}% "
            f"(MLB: {league_hard_hit_rate:.1f}%, "
            f"{hard_hit_difference:+.1f} pts, "
            f"{hard_hit_rating})"
        )
    else:
        print(
            f"Hard-Hit Rate: {hard_hit_rate:.1f}% "
            "(MLB benchmark unavailable)"
        )
    print(f"Barrel Rate: {barrel_rate:.1f}%")
    print(f"Average Launch Angle: {avg_launch_angle:.1f} degrees")
    print(f"Sample Size: {sample_size}")

def download_player_data(
        start_date,
        end_date,
        player_id,
        max_attempts=3
):
    for attempt in range(1, max_attempts + 1):
        try:
            return statcast_batter(
                start_date,
                end_date,
                player_id
            )

        except Exception as error:
            print(
                f"\nDownload attempt {attempt} "
                f"failed: {error}"
            )

            if attempt < max_attempts:
                print("Trying again in 5 seconds...")
                time.sleep(5)
            else:
                print(
                    "\nUnable to download player data "
                    "after 3 attempts."
                )
                return None

def main():
    player_result = get_player()

    if player_result is None:
        return

    player_id, first_name, last_name = player_result
    
    start_date, end_date = get_date_range()

    print("\nDownloading Statcast data...")

    player_data = download_player_data(
        start_date,
        end_date,
        player_id
    )

    if player_id is None:
        return

    print("Download complete!")

    generate_hitter_report(
        player_data,
        first_name,
        last_name,
        start_date,
        end_date
    )

if __name__ == "__main__":
    freeze_support()
    main()