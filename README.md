# Table of Content
>- Packages
>- Logging
>- Schedule Monitor Functions
>- GUI Layout

## Installation
The following are the installed packages required for the Schedule Monitor App:
- tkinter
- wakepy
- thefuzz
- pyautogui
- pytesseract
- email


## Usage
>- This simple application is used to monitor the schedule of a worker which may vary depending on the day the worker is working.
>- The workers are assigned a letter and are required to select the letter assigned to them before starting the application.
>- The worker is also required to select the exact time they are meant to start from the "start time" dropdown.
>- With the above selected, the schedule monitor can be started


## Features:
>- The schedule monitor operates in 3 modes given by the radiobutton that is on:<br>
> 1. Work: This is when the yellow radiobutton is on. It indicates that the worker should be working.
> 2. Break: This is when the red radiobutton is on. It indicates that the worker should be on break
> 3. Blue: This is when the blue radiobutton is on. It indicates that the worker should have completed his shift for the day<br>
>- When the worker is to come back from break, an alarm is sounded from the app. The alarm would not stop unless the "Alarm off" button is pressed. This ensures that if the worker is sleeping (in the case of night shift).
>- The shift status gives us how many hours left for a particular shift to be completed.
 
### Additional Features:
>- The app monitors the screen of the worker to ensure that they are not off the work environment for too long. If the worker is off the work environment screen for too long, it sends an email informing the supervisor that a worker might not be on the screen.


## About the code:
- The order of arrangement of the code blocks is given in the Table of Content above.
- The main file is the schedule_monitor(Beta).pyw
- The Tutor_shifts.json is a json file that gives the letters that correspond to each worker and the number of hours they are to work or be on break
- file_change_detectorr.py in the resources folder is used to detect a change in timestamp.txt file which is used to monitor if there are any changes in the Tutor_shifts.json file, so that the app can run according to the changes made in the Tutor_shifts.json file.
- json_file_reader.py is used to read json files and then give output required in the main file schedule_monitor(Beta).pyw.
- moving_tesseract.py is used to move the tesseract.exe file into the computer's path. This enables the app's ability to read the screen of the worker.
- Txt_to_json_converter.py is used to convert txt files to json
