import os
import sys
import json


sys.path.append(r"..")

print("passed the append stage")

from Resources.Txt_to_Json_Converter import txt_to_json_converter
#print("done")
from Resources.file_change_detectorr import FileChangeDetector as fcd
#print("done")



def dict_from_json(jsonfilename):
    
    with open(f'./{jsonfilename}', 'r') as json_file:
        shifts = json.loads(json_file.read())

    day_alphas = eval(shifts[0][12:-1])
    night_alphas = eval(shifts[1][14:-1])
    day_shifts = eval(shifts[3][13:-1])
    night_shifts = eval(shifts[6][15:-1])

    return day_alphas, night_alphas, day_shifts, night_shifts


if not os.path.isfile("./tutor_shifts.json"):
    tutor_shifts_path = os.path.abspath("./tutor_shifts.txt")
    txt_to_json_converter(tutor_shifts_path)
    #dict_from_json("tutor_shifts.json")
