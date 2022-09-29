import json



def dict_from_json(jsonfilename):
    
    with open(f'{jsonfilename}', 'r') as json_file:
        shifts = json.loads(json_file.read())

    day_alphas = eval(shifts[0][12:-1])
    night_alphas = eval(shifts[1][14:-1])
    day_shifts = eval(shifts[3][13:-1])
    night_shifts = eval(shifts[6][15:-1])

    return day_alphas, night_alphas, day_shifts, night_shifts



day_alphas, night_alphas, day_shifts, night_shifts = dict_from_json("tutor_shifts.json")

