import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import time
import chime
import threading
import sys, os, shutil
import math
import logging
import numpy as np
from thefuzz import fuzz, process
import pyautogui
import pytesseract
from wakepy import set_keepawake, unset_keepawake
import cv2

from PIL import ImageGrab

from pytesseract import Output

import smtplib, ssl

import urllib, socket

from email.message import EmailMessage



sys.path.append(r"./Resources/moving_tesseract.py")
sys.path.insert(0, r"./Resources/moving_tesseract.py")
from Resources import moving_tesseract

sys.path.append(r"./Resources/json_file_reader.py")
sys.path.append(r"./Resources/file_change_detector.py")
sys.path.append(r"./Resources/Txt_to_Json_Converter.py")


alarm_bool = False



"""
The tkinter library is imported for creating the graphics user interface.

Datetime and time modules are imported to monitor the time activities of the app.

The chime module is imported to give the alarm tone.

The threading module is used to peel off the alarm process from the main program.

The sys module is used to include the path to the shift reader file in this module.

The math module is imported to perform basic mathematical operations.

"""




#MAKING LOG DIRECTORIES AND FILES
def make_directory(dir_name):
    if os.path.isdir(dir_name):
        pass
    else:
        os.mkdir(dir_name)
    

log_paths = ("./LOGS", "./LOGS/WARNINGS/", "./LOGS/DEBUGS/")

for directory in log_paths:
    make_directory(directory)




logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger("MonitorLogger")

today = datetime.today()
warning_filename = f".\LOGS\WARNINGS\WARNING_BASE LOG {today.day:02d}-{today.month:02d}-{today.year}.log"
warning_file_handler = logging.FileHandler(warning_filename)
warning_file_handler.setLevel(logging.WARNING)

debug_filename = f".\LOGS\DEBUGS\DEBUG_BASE LOG {today.day:02d}-{today.month:02d}-{today.year}.log"
debug_file_handler = logging.FileHandler(debug_filename)
debug_file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s: %(levelname)s | Function Name: %(funcName)s | Logger Name: %(name)s \nMessage: %(message)s")

warning_file_handler.setFormatter(formatter)
debug_file_handler.setFormatter(formatter)

logger.addHandler(warning_file_handler)
logger.addHandler(debug_file_handler)





def network_check():
    try:
        urllib.request.urlopen("http://google.com")
        print("No network issue, thus, network_issue variable is false")
        logger.info("No network issue, thus, network_issue variable is false")
        return False

    except:
        print("Network issue, thus, network_issue variable is true")
        logger.info("Network issue, thus, network_issue variable is true")
        return True


network_issue = network_check()
network_issue_list = []
network_issue_list.append(network_issue)
    

#Importing json_file_reader used to read the shifts from the .json file. It uses the dict_from_json function to convert the json values into python dictionaries
#Importing FileChangeDetector used to detect any changes made to the tutor_shifts.txt file. Once any changes are detected, the shifts are updated and the new shift is used for the application.

try:
    from Resources.json_file_reader import dict_from_json
    from Resources.file_change_detectorr import FileChangeDetector
    
except ModuleNotFoundError as e:
    logger.critical(f"""Module json_file_reader/tutor_shift.txt is missing from file path\n
The python base error message is {e}""")
    print(e)
    
    messagebox.showerror("File(s) missing", "json_file_reader or tutor_shift.txt missing from path")
    if os.path.exists("./tutor_shifts.json"):
        logger.critical("The json file tutor_shifts.json is in path\n")

    else:
        logger.critical("The json file tutor_shifts.json is NOT in path\n")
    sys.exit()
    window.destroy()

    os._exit(0)

    



concurrent_threads = []
mouse_positions = []

#Detecting changes to tutor_shifts.txt file. This is done by checking if the timestamp recorded in the timestamp.txt file is still the same.

if os.path.exists("./tutor_shifts.txt"):
        logger.info("The tutor_shifts.txt file is in path\n")
        detect_change = FileChangeDetector("tutor_shifts.txt", "./Resources/timestamp.txt")

        message = detect_change.detect()

        logger.info(message)


else:
    logger.critical("The tutor_shifts.txt file is NOT in path\n")
    root = tk.Tk()
    root.title("File Missing")
    label = tk.Label(root, text="tutor_shift.txt missing from path")
    label.pack(side="top", fill="both", expand=True, padx=20, pady=20)
    button = tk.Button(root, text="OK", command=lambda: root.destroy())
    button.pack(side="bottom", fill="none", expand=True)
    root.mainloop()
    
    os._exit(0)




#The day and night alphabets are read from the tutor shifts .json file
#The day and night shifts are read from the tutor shifts .json file
#The shifts are in lists such that the shifts are given as a list that records the number of hours a tutor works, followed by the number of breaks, then, the number of hours to be worked after resumption, then the number of hours of breaks after than and so on.
#If a tutor works from 8PM to 11PM, goes on break for an hour till 12AM, and then resumes to complete the shift by 5AM; For this example, it will be [3, 1, 5]

 
day_alphas, night_alphas, day_shifts, night_shifts = dict_from_json("tutor_shifts.json")


def _start_time_setter():
    """This gets the letter and the start time entered in the entry boxes of the application"""
    letter = letter_menu.get()
    start_time = start_time_menu.get()
    print(type(start_time))

    if letter not in letter_list:
        messagebox.showwarning("Letter Selection Warning", "Please select your letter")
        restart_program()

    elif start_time not in time_list:
        messagebox.showwarning("Time Selection Warning", "Please select the start time")
        restart_program()

    #This condition block is used to ensure that the start time format chosen on the application is in the proper format to be processed.
    if start_time.endswith("PM"):
        start_time = str(int(start_time[:-2]) + 12)
        print(f"The new start time is {start_time}")

    if start_time.endswith("AM"):
        start_time = start_time[:-2]
        if start_time == "12":
            start_time = "00"
            print(f"The new start time is {start_time}")

        start_time = str(datetime.now().date()) + " " + start_time + ":00:00"
        print(start_time)
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    

    else:

        print(start_time)

        #The next 4 lines of code are necessary for comparing times of two different days.
        #The reason for this is: If the application is started by 1am in the night, perhaps after break time, the datetime.now() would get the date and time of the current day
        #when in fact the shift began a day earlier, at night. Thus, it is necessary to deduct 1 full day from the datetime.now() result in this scenario.

        #This scenario is obviously valid only during valid work hours, between 12am and 5am and this concession is taken care of by the first if statement.

        twelveAm = str(datetime.now().date()) + " " + "00:00:00"
        twelveAm = datetime.strptime(twelveAm, "%Y-%m-%d %H:%M:%S")

        fiveAm = str(datetime.now().date()) + " " + "05:00:00"
        fiveAm = datetime.strptime(fiveAm, "%Y-%m-%d %H:%M:%S")


        if datetime.now() >= twelveAm and datetime.now() <= fiveAm:
            yesterday = datetime.now() - timedelta(days = 1)
            start_time = str(yesterday.date()) + " " + start_time + ":00:00"
            
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
     
        else:
            start_time = str(datetime.now().date()) + " " + start_time + ":00:00"
            print(start_time)
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

    #LOGGING INFO: START TIME AND LETTER CHOSEN

    logger.info(f"Start time: {start_time}\nLetter: {letter}\n")

    return start_time, letter



def _end_time_setter(start_time, letter):
    """
    This takes the output of the start_time_setter function (start_time, letter) and uses the information to produce
    the time that a shift ends (end_time), the total hours of the shift, and the list of hours that need to be completed 

    """
    week_day = datetime.today().weekday()
    
    if letter.upper() in day_alphas:
        dayOrNight = "Day"
        
        #LOGGING WARNING: DAY NOT WEEKDAY. HANDLE INDEXERROR
        try:
            shift = day_shifts[letter.upper()][week_day]
        except IndexError as e:
            logger.warning(f"Today is {today.strftime('%A')}. No work!\n{e}\n")
            shift_times_var.set(f"Today is {today.strftime('%A')}. No work!")
            sys.exit()
            os._exit(0)
            
        total_hours = timedelta(hours = sum(shift))
        end_time = start_time + total_hours

        #LOGGING INFO
        logger.info("You are in Day shift for this week\n")
 #       f1(start_time, end_time, day_shifts[letter][week_day])


    elif letter.upper() in night_alphas:
        dayOrNight = "Night"
        twelveAm = str(datetime.now().date()) + " " + "00:00:00"
        twelveAm = datetime.strptime(twelveAm, "%Y-%m-%d %H:%M:%S")

        fiveAm = str(datetime.now().date()) + " " + "05:00:00"
        fiveAm = datetime.strptime(fiveAm, "%Y-%m-%d %H:%M:%S")
        if datetime.now() >= twelveAm and datetime.now() <= fiveAm:
            #LOGGING INFO: STARTING A SHIFT AT PAST 12AM
            logger.info("A shift at past 12AM\n")
            try:
                shift = night_shifts[letter.upper()][week_day - 1]
            except IndexError as e:
                logger.warning(f"Today is {today.strftime('%A')}. No work!\n{e}\n")
                shift_times_var.set(f"Today is {today.strftime('%A')}. No work!")
                sys.exit()
                os._exit(0)

        elif datetime.now() >= fiveAm and week_day >= 5:
            logger.warning(f"Today is {today.strftime('%A')}. No work!\n")
            shift_times_var.set(f"Today is {today.strftime('%A')}. No work!")
            sys.exit()
            os._exit(0)
        else:
            try:
                shift = night_shifts[letter.upper()][week_day - 1]
            except IndexError as e:
                logger.warning(f"Today is {today.strftime('%A')}. No work!\n{e}\n")
                shift_times_var.set(f"Today is {today.strftime('%A')}. No work!")
                sys.exit()
                os._exit(0)
                
        total_hours = timedelta(hours = sum(shift))
        end_time = start_time + total_hours
        print(f"Your end time is {end_time}")

        logger.info("You are in Night shift for this week\n")
#        f1(start, end, night_shifts[letter][week_day])


    else:
        print("Please enter a valid letter")
        shift_times_var.set("Please enter a valid letter")
        logger.info("Please enter a valid letter\n")

    #LOGGING INFO: SHIFT STARTS BY START TIME AND ENDS BY END TIME
    logger.info(f"Your shift is from: {start_time} to {end_time}\n")
    return end_time, total_hours, shift



def initiallizer():
    """
    This function is used to initialize the parameters used for the overall functioning of the application.
    It retrieves the shifts and the letters they correspond to.
    It also converts the shifts into a structure more useful for computation.
    Lastly, it outputs the shift, total hours a tutor uses both in lobby and on break, the start time, and the time the shift is meant to end


    """
    logger.info("Initializing the all systems and time calculations\n")
    start_time, letter = _start_time_setter()

    end_time, total_hours, shift = _end_time_setter(start_time, letter)

    return start_time, end_time, total_hours, shift




def radio_color_update(color):
    """
    This function operates on the radio button of the application. It is called in the shift_controller function.
    It works by enabling the shift_controller function to toggle between different colors of the radio button depending on the mode the tutor is in; work, break or end of work.
    When the tutor is working, the color is orange, when the tutor is on break, the color is red, and when the tutor has completed his shift, the color is blue. Every mode
    that is disabled at a particular time is greyed out.

    """
    if color == "orange":
        radio_work.config(foreground = color)
        radio_break.config(foreground = "grey")
        radio_end.config(foreground = "grey")

    elif color == "red":
        radio_work.config(foreground = "grey")
        radio_break.config(foreground = color)
        radio_end.config(foreground = "grey")

    else:
        radio_work.config(foreground = "grey")
        radio_break.config(foreground = "grey")
        radio_end.config(foreground = color)


def work_break_start_times(shift, timeval):
    """This list takes the start_time for work and break.

    This timeval is simply used to store the value of the start times for work and break. It does this by storing
    the shift hour and this enables us to add that shift hour to the start_time and that result is stored in the start_time_list
    This start_time_list contains all the times when work and break are to start"""

    start_time_list = []
    start_time_list.append(timeval)

    for i, shift_hour in enumerate(shift):
        timeval = timeval + timedelta(hours = shift_hour)
        start_time_list.append(timeval)
        timeval = start_time_list[-1]

    return start_time_list


def current_time_setter():
    """
    This function is used to set the current time. It is used by the shift controller function to help calibrate the
    current time, the number of minutes left till the end of that hour, the number of seconds left and the particular hour.
    """
    current_time = datetime.now()
    minutes_left = 60 - current_time.minute
    seconds_left = 60 - current_time.second

    particular_hour = current_time.hour
                
    return current_time, minutes_left, seconds_left, particular_hour


def clock_starter(current_time, end_of_phase, color, clock_use, shift_size, shift_number):
    """
    This function is used to start the count down clock of the application.
    It also governs over the color assignment of the time values in the application depending on the work phase.
    work = orange
    break = red
    blue = end

    It also helps to ensure that when the application moves from break time to work time, the alarm starts to ring but is not
    on the main thread of the computer, so that it can continue to operate while the alarm rings
    """
   
    print(f"current time is {current_time}")
    if end_of_phase < current_time:
        print("\nThis phase has ended")
        #LOGGING INFO
        logger.info(f"End of a work/break phase by {end_of_phase}\n")
        pass
    
    else:
        var.set(color)
        radio_color_update(color)

        new_shift_hour = math.ceil((end_of_phase - current_time)/timedelta(hours=1))
        t_secs = (end_of_phase - current_time).total_seconds()
        (minutes, div_seconds) = divmod(t_secs, 60)
        if color == "orange":
##            online_check_thread = threading.Thread(target = online_check_timer, args = [minutes])
##            online_check_thread.daemon = True
##            online_check_thread.start()
##            online_check_thread.join()
##            print("Online_check_thread killed")
##                
            try:
                online_check_thread = threading.Thread(target = online_check_timer, args = [minutes])
                online_check_thread.daemon = True
                print(f"{online_check_thread.name} Thread started for online check thread")
                concurrent_threads.append(online_check_thread)
                online_check_thread.start()
                
            except (KeyboardInterrupt, SystemExit, RuntimeError):
                online_check_thread.join()
                print("Online_check_thread killed")
                
        (hour, minutes) = divmod(minutes, 60)

        print("\nThe new shift hour is", new_shift_hour)
        #LOGGING INFO
        logger.info(f"There are {hour}:{minutes}:{div_seconds}  till the end of this shift phase\n")

        
        countdown_clock(new_shift_hour, int(minutes), int(div_seconds), color, clock_use)
        window.update()     

        if shift_size - 1 == shift_number:
            color = "blue"
            var.set(color)
            radio_color_update(color)
            entry_timeleft_hour.config(fg = color)
            entry_timeleft_minute.config(fg = color)
            entry_timeleft_second.config(fg = color)

            #sys.exit()

        if color == "red":
            global alarm_bool
            alarm_bool = True
            break_thread = threading.Thread(target = chime_alarm)
            break_thread.daemon = True
            concurrent_threads.append(break_thread)
            print(f"{break_thread.name} thread created for chime_alarm in clock_starter")
            break_thread.start()
##            if not alarm_bool:
##                break_thread.join()
##                print("Break thread killed")
##                logger.info("Break thread killed\n")

    #online_check_thread.join()
    #print("Online_check_thread killed")
    #break_thread.join()
    #print("Break thread killed")
    #logger.info("Break thread killed\n")
            


def set_shift_status(shift_batch, shift_batch_list, status, indexer):
    """
    This function is used to set the shift status. It takes the shift_batch dictionary and the shift_batch_list to achieve this.
    The shift_times_var StringVar() created changes the values of the status depending on where the running of the shift is.
    """
   
    shift_batch[shift_batch_list[int(indexer)]] = status
    shift_times_var.set("\n"+ str([str(shift_batch_list[0]) +" ⇒ " + str(shift_batch[shift_batch_list[0]]) if shift_batch_list[0] != " " else " "][0]) + "\n"
                                        + str([str(shift_batch_list[1]) +" ⇒ " + str(shift_batch[shift_batch_list[1]]) if shift_batch_list[1] != " " else " "][0]) + "\n"
                                        + str([str(shift_batch_list[2]) +" ⇒ " + str(shift_batch[shift_batch_list[2]]) if shift_batch_list[2] != " " else " "][0])
                                        )                 


def shift_controller():
    """
    This function is the master controller of the operations of the application. It applies almost all the functions written in this program.
    It takes

    """

    #Retrieving the start_time, end_time, total_hours, and shifts from the initializer function
    start_time, end_time, total_hours, shift = initiallizer()

    #Initializing the color which is used to represent the work mode: work = orange, break = red, end of work = blue
    color = None

    #This list takes the start_time for work and break.
    
    start_time_list = work_break_start_times(shift, start_time)
    current_time, _, _, current_hour = current_time_setter()

    print(start_time_list)
    #LOGGING INFO
    logger.info("Running shift_controller function")
    shift_batch = {}
    shift_batch_list = []
    start_time_list_v2 = [str(x.hour-12) + "PM" if x.hour >= 12 else str(x.hour) + "AM" for x in start_time_list]
    
    print(start_time_list_v2)
    for i in range(len(start_time_list_v2)):
        
        if i % 2 !=0:
            shift_batch[start_time_list_v2[i-1] + " to " + start_time_list_v2[i]] = "No Status"
            shift_batch_list.append(start_time_list_v2[i-1] + " to " + start_time_list_v2[i])

    while len(shift_batch_list) <= 4:
        shift_batch_list.append(" ")
        shift_batch[" "] = " "

    print(shift_batch)

    #LOGGING INFO
    print(f"\nThe current time is {current_time} while the start time is {start_time}")
    logger.info(f"\nThe current time is {current_time} while the start time is {start_time}")
    
    total_shift_run = 1
    while current_time < end_time and total_shift_run >= 1:
        print("\nI checked the first while loop")
        

        if current_time >= start_time:

            print(f"\nThe shift has begun at {start_time}")
            print(shift)
            shift_size = len(shift)
            for i, shift_hour in enumerate(shift):
                print(f"\nThe value of i is {i}")

                current_time, minutes, seconds, _ = current_time_setter()

                clock_use = i + 1
                
                if i % 2 == 0 and i < shift_size:

                    global online_bool

                    color = "orange"

                    work_time = start_time_list[i]

                    print(f"\nThe new work time is {work_time}")

                    end_of_phase = work_time + timedelta(hours = shift_hour)
                    
                    #end_of_phase_timestamp = datetime.timestamp(end_of_phase)

                    print(f"This shift will end by {end_of_phase}")

                    print(f"\nThe last hour of this shift is : {end_of_phase.hour},while the current hour is : {current_hour}")

                    online_bool = True
                    print(f"\nOnline Bool is {online_bool}")
                    
                    set_shift_status(shift_batch, shift_batch_list, "Running", indexer = i/2)
                    
                    clock_starter(current_time, end_of_phase, color, clock_use, shift_size, i)

##                    if i > 1:
##                        concurrent_threads[1].join()
##                        concurrent_threads.pop()

                    set_shift_status(shift_batch, shift_batch_list, "Finished", indexer = i/2)
                    

                    online_bool = False
                    print(f"\nOnline Bool is {online_bool} after clock starter function has run")

                    

                elif i % 2 != 0 and i < shift_size:

                    set_keepawake(keep_screen_awake = True)
                    
                    color = "red"
                    
                    break_time = start_time_list[i]

                    breaktime_end = break_time + timedelta(hours = shift_hour)
                    
                    
                    print(f"\n Break time starts now at {break_time}")
                    print(f"\nBreak time ends at {breaktime_end}")
                    print(f"\n current time starts now at {current_time}")
                    #start_hour = datetime.timestamp(in_lobby_time) + (shift_hour * 3600)

                    #breaktime_timestamp = datetime.timestamp(breaktime)                        screen_process = multiprocessing.Process(target = screen_awake, args = [breaktime_end])

                    clock_starter(current_time, breaktime_end, color, clock_use, shift_size, i)

                    unset_keepawake
                    
##                    concurrent_threads[1].join()
##                    concurrent_threads.pop()

                    #screen_thread.join()
                    #print(f"screen thread stopped? {screen_thread.is_alive()}")
                    

                elif i >= shift_size:
                    print("I will break away now")
                    set_shift_status(shift_batch, shift_batch_list, "Finished", indexer = i/2)
                    break


        else:
            #LOGGING INFO
            print("Please wait while your shift begins...")
            logger.info("Work has not yet begun")
            time_left = (start_time - current_time)/timedelta(hours=1)
  #          shift_times_var.set(f"Work has not yet begun.\nPlease wait while your shift begins...\nWaiting for {int(time_left * 60)} minutes")
            
            time_left = (start_time - current_time)/timedelta(hours=1)
            

            print(f"Waiting for {time_left * 60} minutes")

            time.sleep(time_left * 60 *60)
            hour_left = math.ceil(time_left)
            minutes_left = (time_left-hour_left) * 60

            print(f"You have time left of: {hour_left} hours, {minutes_left} minutes")  
            shift_times_var.set(f"Time before shift begins: {int(hour_left)} hrs, {int(minutes_left)} mins\nPlease wait while your shift begins...\n")
            
            
        current_time = datetime.now()

        

    #LOGGING INFO
    print(f"shift completed by {current_time}")
    logger.info(f"shift completed by {current_time}")
    color = "blue"
    radio_color_update(color)
    var.set(color)
    print(f"\nRadio color updated to {color} from end of shift_controller")
    online_bool = True

    

    for thread in concurrent_threads:
        try:
            thread.join()
            print(f"{thread.name} has been stopped")

        except RuntimeError as e:
            print("Threads already stopped")
            print("Thread alive?", thread.is_alive())
            print(f"{thread.name} is still alive")
        
            
    #total_shift_run = total_shift_run - 1
    
    sys.exit()
    
    total_shift_run -= 1
    
    

##
##def countdown_clock(hours, minutes, seconds, color, clock_use):
##    """
##    This is a countdown_clock operated by the shift_controller function. The countdown clock simply shows the amount of time left whether during work periods or during breaks.
##    It works by taking in the values for hour, minutes, seconds, and color. The clock counts down using python's sleep function. The color here changes in tandem with the color of the
##    radio button, which follows the work mode of the tutor: work, break, or end of work.
##
##    """
##    #Here we set the values of the hr, mins, and secs string variables. These are the string variables initialized from the tk module using tk.StringVar().
##    #They give us the ability to change the values of the entry box in real-time. Using ordinary variable will result in a static entry output on the application.
##    #They are initially set to "00" to indicate that no operation is on, depicting an initial phase of the clock.
##    
##    hr.set("00")
##    mins.set("00")
##    secs.set("00")
##
##    #A 5-second sleep is used here to aid transition from one phase to another. From no function to work mode, from work mode, to break mode and so on. It makes sense for transitions
##    #like these to have a time gap before operation commences.
##    time.sleep(5)
##
##    #This configures the hour, minute and second values to their correct color scheme which is dependent on their work mode.
##    entry_timeleft_hour.config(fg = color)
##    entry_timeleft_minute.config(fg = color)
##    entry_timeleft_second.config(fg = color)
##
##    
##
##
##    
##    #This is the operational part of the countdown_clock. It takes the hour value first along with an indexer, j using the enumerate function. The purpose of the indexer will be made
##    #apparent in a moment. Next, the minute value is taken in a range function just like the hour and decremented minute by minute as indicated by the "-1" in the range function. This is
##    #the same process for the hour for loop and the second for loop. The indexers j and i are used to take into account the fact that a particular person might start the countdown at a time
##    #that is not well rounded.
##    #For example, if the person starts the countdown at and has 2:15:30 to work for. Without the indexers, j and i, we would simply pass in the hours = 2, minutes = 15, seconds = 30.
##
##    #However, while this would work accurately for the first 30 seconds, the countdown clock would run down faster than it ought to because it is restarting the count of 1 minute after just
##    #30 seconds, recounting each hour after just 15 minutes. Thus, we need the indexers, j and i to solve the problem. What they do is to keep track of the number of times the loop has been
##    #executed. Using the same 2:15:30 example, when j = 0 (At the first loop), we can let the minute value in the for loop be 15 and a countdown from 15 would make sense.
##    #However, when the first hour is gone, the hour value is reduced to 1, but the minute value must be initialized to 60 minutes. With the indexer now greater than 0, we can instruct
##    #python to countdown from 60 minutes from now on, rather than 15 minutes. A similar thing is done with the seconds value using the i indexer. The seconds value could be easily dealt with by simply
##    #initializing all minutes to 60 seconds irrespective of the amount of seconds in that particular minute when the countdown clock was started. But for the sake of being as accurate as
##    #possible, the same process of preserving the correct minute value for each iteration is applied to the number of seconds.
##    for j, hour in enumerate(range(hours - 1, -1, -1)):
##        if j == 0 and clock_use <= 1:
##            for i, minute in enumerate(range(minutes, -1, -1)):
##                if i == 0:
##                
##                    for second in range(seconds - 1, -1, -1):
##                        
##                        clock_setter(hour, minute, second)
##
##                elif i > 0:
##                    for second in range(59, -1, -1):
##
##                        clock_setter(hour, minute, second)
##
##
##        elif j > 0 and clock_use > 1:
##            
##            for i, minute in enumerate(range(59, -1, -1)):
##                if i == 0:
##                    for second in range(seconds, -1, -1):
##                            
##                        clock_setter(hour, minute, second)
##
##                elif i > 0:
##                    for second in range(59, -1, -1):
##
##                        clock_setter(hour, minute, second)
##
##
##
##        elif j > 0 or clock_use > 1:
####            print("SETTING ALARM BOOL TO TRUE!!!")
####            global alarm_bool
####            alarm_bool = True
####            one_hour_thread = threading.Thread(target = chime_alarm)
####            one_hour_thread.daemon = True
####            concurrent_threads.append(one_hour_thread)
####            print(f"{one_hour_thread.name} thread created for chime_alarm in clock_starter")
####            one_hour_thread.start()
####          
####          
##            for i, minute in enumerate(range(minutes, -1, -1)):
##                if i == 0:
##                    for second in range(59, -1, -1):
##                        
##                        clock_setter(hour, minute, second)
##
##                elif i > 0:
##                    for second in range(59, -1, -1):
##
##                        clock_setter(hour, minute, second)
##
##

    
def countdown_clock(hours, minutes, seconds, color, clock_use):
    """
    This is a countdown_clock operated by the shift_controller function. The countdown clock simply shows the amount of time left whether during work periods or during breaks.
    It works by taking in the values for hour, minutes, seconds, and color. The clock counts down using python's sleep function. The color here changes in tandem with the color of the
    radio button, which follows the work mode of the tutor: work, break, or end of work.

    """
    #Here we set the values of the hr, mins, and secs string variables. These are the string variables initialized from the tk module using tk.StringVar().
    #They give us the ability to change the values of the entry box in real-time. Using ordinary variable will result in a static entry output on the application.
    #They are initially set to "00" to indicate that no operation is on, depicting an initial phase of the clock.
    
    hr.set("00")
    mins.set("00")
    secs.set("00")

    #A 5-second sleep is used here to aid transition from one phase to another. From no function to work mode, from work mode, to break mode and so on. It makes sense for transitions
    #like these to have a time gap before operation commences.
    time.sleep(5)

    #This configures the hour, minute and second values to their correct color scheme which is dependent on their work mode.
    entry_timeleft_hour.config(fg = color)
    entry_timeleft_minute.config(fg = color)
    entry_timeleft_second.config(fg = color)


    list_of_minutes = []
    if hours - 1 > 0:
        list_of_minutes.append(minutes)
        other_minutes = [59 for hour in range(hours - 1)]
        list_of_minutes.extend(other_minutes)
        

    else:
        list_of_minutes.append(minutes)


    
    #This is the operational part of the countdown_clock. It takes the hour value first along with an indexer, j using the enumerate function. The purpose of the indexer will be made
    #apparent in a moment. Next, the minute value is taken in a range function just like the hour and decremented minute by minute as indicated by the "-1" in the range function. This is
    #the same process for the hour for loop and the second for loop. The indexers j and i are used to take into account the fact that a particular person might start the countdown at a time
    #that is not well rounded.
    #For example, if the person starts the countdown at and has 2:15:30 to work for. Without the indexers, j and i, we would simply pass in the hours = 2, minutes = 15, seconds = 30.

    #However, while this would work accurately for the first 30 seconds, the countdown clock would run down faster than it ought to because it is restarting the count of 1 minute after just
    #30 seconds, recounting each hour after just 15 minutes. Thus, we need the indexers, j and i to solve the problem. What they do is to keep track of the number of times the loop has been
    #executed. Using the same 2:15:30 example, when j = 0 (At the first loop), we can let the minute value in the for loop be 15 and a countdown from 15 would make sense.
    #However, when the first hour is gone, the hour value is reduced to 1, but the minute value must be initialized to 60 minutes. With the indexer now greater than 0, we can instruct
    #python to countdown from 60 minutes from now on, rather than 15 minutes. A similar thing is done with the seconds value using the i indexer. The seconds value could be easily dealt with by simply
    #initializing all minutes to 60 seconds irrespective of the amount of seconds in that particular minute when the countdown clock was started. But for the sake of being as accurate as
    #possible, the same process of preserving the correct minute value for each iteration is applied to the number of seconds.
    for j, hour in enumerate(range(hours - 1, -1, -1)):
        if j == 0 and clock_use <= 1:
            for minutes in list_of_minutes:

                if minutes < 59:

                    for minute in range (minutes,-1, -1):

                        for second in range(59, -1, -1):

                            clock_setter(hour, minute, second)

                else:

                    for minute in range (minutes,-1, -1):

                        for second in range(59, -1, -1):

                            clock_setter(hour, minute, second)

                
                
        elif j > 0 and clock_use > 1:
            
            for minutes in list_of_minutes:

                if minutes < 59:

                    for minute in range (minutes,-1, -1):

                        for second in range(59, -1, -1):

                            clock_setter(hour, minute, second)

                else:

                    for minute in range (minutes,-1, -1):

                        for second in range(59, -1, -1):

                            clock_setter(hour, minute, second)

        elif j > 0 or clock_use > 1:
##            print("SETTING ALARM BOOL TO TRUE!!!")
##            global alarm_bool
##            alarm_bool = True
##            one_hour_thread = threading.Thread(target = chime_alarm)
##            one_hour_thread.daemon = True
##            concurrent_threads.append(one_hour_thread)
##            print(f"{one_hour_thread.name} thread created for chime_alarm in clock_starter")
##            one_hour_thread.start()
##          
##          
            for minutes in list_of_minutes:

                if minutes < 59:

                    for minute in range (minutes,-1, -1):

                        for second in range(59, -1, -1):

                            clock_setter(hour, minute, second)

                else:

                    for minute in range (minutes,-1, -1):

                        for second in range(59, -1, -1):

                            clock_setter(hour, minute, second)



                            

def clock_setter(hour, minute, second):
    time.sleep(1)
    print(f"The time is {hour,minute,second}")

    #Change the values of the string variables initialized by the tk() module. The hour value starts from hour - 1 because if you have 2 hours left, you actually have
    #1:59:59 left. And if you have 60 seconds left in a minute, you actually have 59 seconds to countdown from since the seconds value counts down to a zero.
    hr.set("{0:2d}".format(hour))
    mins.set("{0:2d}".format(minute))
    secs.set("{0:2d}".format(second))

    #The window needs to be updated each time these string variables are set. This is what ties all the operations of the above for loops together and displays the
    #real-time change of time on the countdown clock.                        
    window.update()


def program_starter():
    """
    This is a function that allows us to start the program. It is the function attached to the start button, such that when the button is clicked, the program starts working.
    It works by calling the shift_controller function in a thread. It is called in a thread because this allows us to run the application without halting the program on the computer's
    main counter. Thus, the application is able to run without crashing when we try to perform other tasks

    """
    #shift_controller()
    #sys.exit()
    t_thread = threading.Thread(target = shift_controller)
    t_thread.daemon = True
    concurrent_threads.append(t_thread)
    print(f"{t_thread.name} thread created in program_starter")
    #This is actually the code that starts the whole application. And it is started on a thread.
    t_thread.start()


def restart_program():
    
    #os.startfile("Schedule_Monitor.pyw")
    #os.execv(__file__,sys.argv)
    os.execv(sys.executable, ['python'] + sys.argv)
    #window.destroy()


def chime_alarm():
    import pygame
    """
    This is a function that starts the alarm whenever a break time has ended. The alarm will continue to ring unless it is stopped because it is in a while loop.
    The sound of the alarm is gotten from the chime module. The alarm is controlled by toggling a global variable called alarm_bool, which is a boolean value.
    If the alarm_bool is True, the alarm will keep ringing. To turn it off, we need to set the alarm_bool to False. This is why a global varible is needed so that we can apply another
    function to change the value of this alarm_bool, and effectively turn off the alarm.

    """
    global alarm_bool

    def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS2

            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)


    alarm_path = os.path.abspath(".\\Resources\\")
    logger.info("Break Alarm Ought to go off!!!")
    pygame.init()
    pygame.mixer.music.load(resource_path(fr"{alarm_path}\\alarm.wav"))

    try:
        while alarm_bool:
            logger.critical("Right after the alarm bool")

            #The name of the sound is called the info sound in the chime module
            #chime.info()
            #The sound is regulated to be at 1 beep per second using the sleep method of the time module.

                
            

            
            #playsound(resource_path(fr"{alarm_path}\\alarm.wav"))

            pygame.mixer.music.play()
            time.sleep(1)

            #The alarm_bool value is checked to see if it has been changed. If it has break out of the while loop that restarts the chime.info() sound, else continue the chime.info() sound.
            if not alarm_bool:
                break

    except FileNotFoundError as e:
        logger.critical(f"alarm.wav file is missing. The python error is {e}")


def alarm_off():
    """
    This is the function that helps to toggle the alarm_bool value to False. This function is called whenever the "Alarm Off" button is clicked. When this button is clicked, the global
    variable, alarm_bool whose value is True if the alarm is on, will be toggled to False. Once this value is False, the while loop from the chime_alarm() function ends and the alarm goes
    off
    """
    global alarm_bool
    alarm_bool = False


def online_check_timer(minutes):
    global online_bool
    num_checks = int(minutes/2.0)
    start = datetime.now()
    end = start + timedelta(minutes = minutes - 5)
    message_list = []

    if not online_bool:
        return

    if datetime.now() < end:
        for check in range(num_checks):
            print(f"The previous check's message_list is {message_list}")
            if len(message_list) > 0:
                message_list = [message_list[-1]]
                _,_,_,message_list = imageToString(message_list)
                time.sleep(int((minutes/num_checks)*60 + 0.05))
            else:
                _,_,_,message_list = imageToString(message_list)
                time.sleep(int((minutes/num_checks)*60 + 0.05))

            


def send_mail(message, tutor_name = "", counter = 0,
              secondary_counter = 0):

    _, letter = _start_time_setter()

    email_sender = "schedulemonitor439@gmail.com"

    email_password = "vwksznpudzayrhrr"

    email_receiver = "schedulemonitor439@gmail.com"



    subject = "PrepClass notification"

    body = tutor_name + f"| {letter}: " + message



    em = EmailMessage()

    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content(body)


    context = ssl.create_default_context()

    if counter > 1 or secondary_counter > 1:
        pass
        return None
    else:
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context = context) as smtp:
                logger.critical("Currently in the with!")
                smtp.login(email_sender, email_password)

                if len(network_issue_list) > 1:
                    if network_issue_list[-1] != network_issue_list[-2]:
                        message += ". Previously had no internet."
                        body = tutor_name + f"| {letter}: " + message
                        em.set_content(body)
                        logger.critical("Loggin in")
                        smtp.sendmail(email_sender, email_receiver, em.as_string())
                        network_issue_list.clear()

                else:    
                    logger.critical("Loggin in")
                    smtp.sendmail(email_sender, email_receiver, em.as_string())

                    logger.critical("Sending email")
                    
                    print("email sent!")
                    logger.info("Email sent!")
                    network_issue_list.clear()

        except (urllib.error.URLError, socket.gaierror) as e:
            
            logger.critical(f"No internet. Error message is {e}")
            print("Continue without sending email")
            logger.critical("Continue without sending email")




def masking_func():
    print("Taking screenshot")
    test_image = ImageGrab.grab(bbox = (0, 50, 2000, 1200))

    print("Converting to what cv2 can understand")
    test_image = cv2.cvtColor(np.array(test_image), cv2.COLOR_RGB2BGR)

    mask_vals = []
    chat_blue_mask_val = None

    test_colors ={

        "lobby_blue": [255,235,210],
        "second_chance_orange": [214, 243, 255],
        "first_chance_lemon": [237, 247, 227],
        "chat_blue": [246,179,79]

        }

    for color in test_colors:
        print(color)
        nominal_vals = test_colors[color]

        print(nominal_vals)
        
        min_vals = [x-5 for x in nominal_vals]
        max_vals = [x+5 for x in nominal_vals]

        low_color = np.array([min_vals])
        high_color = np.array([max_vals])

        print(low_color)
        print(high_color)
        
        if color == "chat_blue":
            chat_blue_mask_val = cv2.inRange(test_image, low_color, high_color)
            chat_blue_mask_val = chat_blue_mask_val.sum()
            print(chat_blue_mask_val)

        else:
            mask = cv2.inRange(test_image, low_color, high_color)
            mask_vals.append(mask.sum())
            print(mask_vals)


    sorted_masks = sorted(mask_vals)

    print(f"mask values are: {sorted_masks}\nchat_blue_value is {chat_blue_mask_val}")

    return mask_vals, chat_blue_mask_val

        

        
        

        
    

def color_detector(func):

    def wrapper(message_list, num_color_checks = 3):
        print("We are in the wrapper")

        
        update_message_list = [""]
        message = ""
        
        while num_color_checks > 0:
            normal_mask_val, chat_blue_mask_val = masking_func()
            print(f"Normal mask values are {normal_mask_val}")

            if normal_mask_val[0] > 150_000 or normal_mask_val[1] > 36_000_000 or normal_mask_val[2] > 2_500_000 or chat_blue_mask_val > 500_000:
                message = "Logged in"
                data = "No need for data"
                tutor_name = ""
                print("No need to use pytesseract")
                
                if update_message_list[-1] != "Logged in":
                    update_message_list.append("Logged in")
                    print(f"The list is {update_message_list}")

                    print("value change in update_message_list")
                    send_mail(message, tutor_name)
                
                return data, message,tutor_name,message_list

            num_color_checks -= 1

            print(f"I will now wait for 30 seconds. Checks have been decremented to {num_color_checks}")
                        

            time.sleep(30)

            

        else:
            logger.warning("\nUser probably not on Brainly Website. Going through pytesseract")

            data, message, tutor_name, message_list = func(message_list)

            return data, message, tutor_name, message_list

                    

    return wrapper
    
            


@color_detector
def imageToString(message_list):
    global online_bool
    global network_issue

    network_issue = network_check()
    
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    message = ""
    tutor_name = ""
    
    counter = secondary_counter = 0
    start = datetime.now()
    end = start + timedelta(minutes = 9)

    while datetime.now() <= end or message == "Logged in":

        if not online_bool:
            break

        screen = ImageGrab.grab(bbox = (0, 50, 2000, 1200))



        data = pytesseract.image_to_string(cv2.cvtColor(np.array(screen),
                                                        cv2.COLOR_BGR2GRAY),
                                           lang = "eng")

        print(data)

        logged_in_keywords = ["Finding a student who needs your help...", "You have 10 seconds to get started.", "Skipping 2 sessions in a row will automatically log you out.", "EDIT QUESTION", "Student goal", "Answer Chat", "START SESSION", "Skipping this session will log you out.", "Got you another session.", "We found a session for you!"]

        logged_in_similarities = []
        for clause in logged_in_keywords:
            similarity = fuzz.partial_ratio(clause, data)
            logged_in_similarities.append(similarity)

        logged_in_similarities.sort()


        logged_out_keywords = ["May you have a Brainly day", "logged out due to missing 2"]

        logged_out_similarities = []
        for clause in logged_out_keywords:
            similarity = fuzz.partial_ratio(clause, data)
            logged_out_similarities.append(similarity)

        logged_out_similarities.sort()

        
        if logged_in_similarities[-1] > 70: 
            print("Logged in")
            message = "Logged in"
            message_list.append(message)
            for page_info in data.split("\n"):
                if page_info.find("BRAIN") != -1:
                    print(f"The tutor's name is {page_info[11:]}")
                    tutor_name = page_info[11:]

                elif page_info.find("US ") != -1:
                    print(f"The tutor's name is {page_info[3:]}")
                    tutor_name = page_info[3:]

            if len(message_list) == 1 and message_list[0] == "Logged in":
                send_mail(message, tutor_name)
                

            elif len(message_list) > 1:
                if message_list[-2] != "Logged in" and message_list[-1] == "Logged in":
                    send_mail(message, tutor_name)

            try:
                return data, message, tutor_name, message_list
    
            except UnboundLocalError as e:
                print("Online_check_timer thread is dead")

            #break
                    
        
            #if "Logged in" in message_list and "Logged in" != message_list[0]:
            #return data, message, tutor_name, message_list

            #send_mail(message, tutor_name)

        elif logged_out_similarities[-1] > 55:
            print("Logged out")
            message = "Logged out"
            message_list.append(message)
            counter += 1
            secondary_counter = 0
            if len(message_list) == 1 and message_list[0] == "Logged out":
                print(f"Network issue = {network_issue}")
                print("Going into the delay block 1")
                start_delay_check = time.time()
                while network_issue:
                    network_issue = network_check()
                    network_issue_list.append(network_issue)
                    logger.critical("You have no internet")
                    time.sleep(3)
                end_delay_check = time.time()
                delta_delay = end_delay_check - start_delay_check
                if delta_delay > 10:
                    message += f". Delayed for {delta_delay} seconds"
                send_mail(message, tutor_name)

            elif len(message_list) > 1:
                if message_list[-2] != "Logged out" and message_list[-1] == "Logged out":

                    print(f"Network issue = {network_issue}")
                    print("Going into the delay block 2")

                    start_delay_check = time.time()
                    while network_issue:
                        network_issue = network_check()
                        network_issue_list.append(network_issue)
                        logger.critical("You have no internet")
                        time.sleep(3)
                    end_delay_check = time.time()
                    delta_delay = end_delay_check - start_delay_check
                    if delta_delay > 10:
                        message += f". Delayed for {delta_delay} seconds"
                    send_mail(message, tutor_name)


            
            try:
                return data, message, tutor_name, message_list
    
            except UnboundLocalError as e:
                print("Online_check_timer thread is dead")
        
#            break
                #send_mail(message, tutor_name, counter = counter)
                
            
        else:
            message = "Not on Brainly Website"
            print(message)
            message_list.append(message)
            secondary_counter +=1
            counter = 0
            print(f"The message list for Not on brainly website is {message_list}")
            
            if len(message_list) == 1 and message_list[0] == "Not on Brainly Website":
                print(f"Network issue = {network_issue}")
                print("Going into the delay block 3")

                start_delay_check = time.time()
                while network_issue:
                    network_issue = network_check()
                    network_issue_list.append(network_issue)
                    logger.critical("You have no internet")
                    time.sleep(3)
                end_delay_check = time.time()
                delta_delay = end_delay_check - start_delay_check
                if delta_delay > 10:
                    message += f". Delayed for {delta_delay} seconds"
                send_mail(message, tutor_name)


            elif len(message_list) > 1:
                if message_list[-2] != "Not on Brainly Website" and message_list[-1] == "Not on Brainly Website":
                    print(f"Network issue = {network_issue}")
                    print("Going into the delay block 4")
                
                    start_delay_check = time.time()
                    while network_issue:
                        network_issue = network_check()
                        network_issue_list.append(network_issue)
                        logger.critical("You have no internet")
                        time.sleep(3)
                    end_delay_check = time.time()
                    delta_delay = end_delay_check - start_delay_check
                    if delta_delay > 10:
                        message += f". Delayed for {delta_delay} seconds"
                    send_mail(message, tutor_name)

            #send_mail(message = message, tutor_name = tutor_name,
             #         secondary_counter = secondary_counter)

            
            try:
                return data, message, tutor_name, message_list
    
            except UnboundLocalError as e:
                print("Online_check_timer thread is dead")

#            break           
        
        time.sleep(60)

            
            
    try:
        return data, message, tutor_name, message_list
    
    except UnboundLocalError as e:
        print("Online_check_timer thread is dead")











































window = tk.Tk()
window.title("Schedule Monitor")

if os.path.exists(r".\\Resources\\P_logo.ico"):
    window.iconbitmap(r".\\Resources\\P_logo.ico")
    
window.geometry("500x400")


mins = tk.StringVar()
secs = tk.StringVar()
hr = tk.StringVar()

mins.set("00")
secs.set("00")
hr.set("00")

#Frame Creation
frame_left = tk.Frame(width = 50, height = 30)
frame_left.grid(row = 0, column = 0, padx = 15, pady = 1)

frame_right = tk.Frame(width = 200, height = 300)
frame_right.grid(row = 0, column = 50, padx = 15, pady = 20)

frame_center = tk.Frame(width = 3, height = 1)
frame_center.grid(row =0, column = 15, padx = 10)

frame_start = tk.Frame(width = 1, height = 1)
frame_start.grid(row = 1, column = 0, padx = 1, pady = 35)


frame_shifts = tk.Frame(width = 15, height = 15)
frame_shifts.grid(row = 15, column = 15, padx = 0, pady = 1)



#Entry/Label Creation: Enter your Letter
label_letter = tk.Label(master = frame_left, text = "Select your Letter", height = 1)
#entry_letter = tk.Entry(master = frame_left, width = 5)
#Set the Menu initially
letter_menu= tk.StringVar()
letter_menu.set("Letters")

#Create a dropdown Menu
letter_list = ["A", "B", "C", "D", "E","F", "G", "H", "I", "J",
                 "k", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                 "W", "X", "2", "5"]
letter_dropdown= tk.OptionMenu(frame_left, letter_menu, *letter_list)



#Entry/Label Creation: Start time
label_time = tk.Label(master = frame_left, text = "Start time")
entry_time = tk.Entry(master = frame_left, width = 5)
start_time_menu= tk.StringVar()
start_time_menu.set("Choose Time")

#Create a dropdown Menu
time_list = ["12AM", "1AM", "2AM", "3AM", "4AM", "5AM",
                 "1PM", "2PM", "3PM", "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM",
                 "11PM"]
time_dropdown= tk.OptionMenu(frame_left, start_time_menu, *time_list)



#Label for space Creation:
label_space = tk.Label(master = frame_left, text = " ")


#Entry/Label Creation: Time Left
label_timeleft = tk.Label(master = frame_center, text = "Time Left")
entry_timeleft_hour = tk.Entry(master = frame_center, width = 7, textvariable = hr)

#Label for Hours:Mins:Secs
label_timecolon1= tk.Label(master = frame_center, text = ":")

entry_timeleft_minute = tk.Entry(master = frame_center, width = 7, textvariable = mins)

#Label for Hours:Mins:Secs
label_timecolon2 = tk.Label(master = frame_center, text = ":")

entry_timeleft_second = tk.Entry(master = frame_center, width = 7, textvariable = secs)


label_info = tk.Label(master = frame_shifts, text = "Shift ⇒ Status")

shift_times_var = tk.StringVar()
label_shift_times = tk.Label(master= frame_shifts, textvariable = shift_times_var)




#Button Creation: Start    
button_start = tk.Button(master = frame_start, text = "Start", command =program_starter)


#Button Creation: Alarm Off

button_alarm = tk.Button(master = frame_right, text = "Alarm Off", command = alarm_off)
button_alarm.grid(pady = 15)

                         
#Radiobutton Creation: Work, Break, End
var = tk.StringVar()
var.set("grey")

radio_work = tk.Radiobutton(master = frame_right, text = "Work", variable = var, value = "orange", foreground = var.get())


radio_break = tk.Radiobutton(master = frame_right, text = "Break", variable = var, value = "red", foreground = var.get())



radio_end = tk.Radiobutton(master = frame_right, text = "End", variable = var, value = "blue", foreground = var.get())




label_letter.pack()
letter_dropdown.pack()
#entry_letter.pack()

label_space.pack(side = tk.TOP)

label_time.pack()
#entry_time.pack()
time_dropdown.pack()


label_timeleft.pack()
entry_timeleft_hour.pack(side =tk.LEFT)

label_timecolon1.pack(side = tk.LEFT)
entry_timeleft_minute.pack(side = tk.LEFT)

label_timecolon2.pack(side = tk.LEFT)
entry_timeleft_second.pack(side = tk.LEFT)


button_start.pack()
button_alarm.pack(side = tk.BOTTOM)


radio_work.pack()
radio_break.pack()
radio_end.pack()

label_info.pack()
label_shift_times.pack()



window.mainloop()
