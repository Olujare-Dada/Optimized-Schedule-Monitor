import os
import sys

sys.path.append(r"..")
from Resources.Txt_to_Json_Converter import txt_to_json_converter


class FileChangeDetector:
    def __init__(self, filename,timestamp_file):
        self.filename = filename
        self.timestamp_file = timestamp_file
        #self.filename_2 = filename_2

    def detect(self):
        stamp = str(os.stat(self.filename).st_mtime)
        print(stamp)
        if os.path.isfile(self.timestamp_file):
            with open(self.timestamp_file, "r") as file:
                read_stamp = file.readline()
                print(f"value read is {read_stamp}")

        else:
            with open(self.timestamp_file, "w") as file:
                file.writeline(stamp)
            
        if stamp != read_stamp:
            print(f"stamp: {stamp}")
            print(f"read_stamp: {read_stamp}")
            with open(self.timestamp_file, "w+") as file:
                file.write(str(stamp))
            
            print("Changes detected!")
            message = "Changes to tutor_shifts.txt file detected!"
            txt_to_json_converter(self.filename)
            return message

        else:
            message = "No changes to tutor_shifts.txt file detected"
            return message

        

    

            
            
            
