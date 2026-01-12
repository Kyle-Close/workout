def calculate_new_one_rep_max(current_one_rep_max: int, set_delta: int, rip: int):
    # set delta = amount of sets completed vs target. -2 would mean just 1 set completed if target is 3
    # rip = reps in reserve on last set
    percent_to_add = 0

    if set_delta == -1:
        percent_to_add = -0.02
    elif set_delta < -1:
        percent_to_add = -0.05
    elif rip == 1:
        percent_to_add = 0.01
    elif rip == 2:
        percent_to_add = 0.03
    elif rip > 2:
        percent_to_add = 0.05
    return current_one_rep_max * (1 + percent_to_add)
