def calculate_avg_exit_velocity(data):
    batted_balls = data[data["launch_speed"].notna()]

    avg_exit_velocity = batted_balls["launch_speed"].mean()

    return avg_exit_velocity

def calculate_hard_hit_rate(data):
    batted_balls = data[data["launch_speed"].notna()]

    hard_hit_balls = batted_balls[
        batted_balls["launch_speed"] >= 95
    ]

    hard_hit_rate = (
        len(hard_hit_balls) / len(batted_balls)
    ) * 100

    return hard_hit_rate

def calculate_avg_launch_angle(data):
    batted_balls = data[data["launch_angle"].notna()]
    
    avg_launch_angle = batted_balls["launch_angle"].mean()

    return avg_launch_angle

def calculate_barrel_rate(data):
    batted_balls = data[data["launch_speed_angle"].notna()]

    barrels = batted_balls[
        batted_balls["launch_speed_angle"] == 6
    ]

    barrel_rate = (
        len(barrels) / len(batted_balls)
    ) * 100

    return barrel_rate