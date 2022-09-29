import tkinter as tk
from datetime import datetime, timedelta
import time
#import chime
import threading
import sys, os, shutil
import math
import logging
from wakepy import set_keepawake, unset_keepawake
sys.path.append(r"./json_file_reader.py")

global alarm_bool


"""
The tkinter library is imported for creating the graphics user interface.

Datetime and time modules are imported to monitor the time activities of the app.

The chime module is imported to give the alarm tone.

The threading module is used to peel off the alarm process from the main program.

The sys module is used to include the path to the shift reader file in this module.

The math module is imported to perform basic mathematical operations.

wakepy is used to keep the laptop awake because logging back into a laptop when the application was previously running
messes with the programming

"""




#MAKING LOG FILE
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





    


    




try:
    from json_file_reader import dict_from_json

except ModuleNotFoundError as e:
    logger.critical(f"""Module json_file_reader is missing from file path\n
The python base error message is {e}""")
    
    if os.path.exists("./tutor_shifts.json"):
        logger.critical("The json file tutor_shifts.json is in path\n")

    else:
        logger.critical("The json file tutor_shifts.json is NOT in path\n")
    sys.exit()

except FileNotFoundError as e:
    logger.critical(f"""File json_file_reader is missing from file path\n
The python base error message is {e}""")
    







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

    #This condition block is used to ensure that the start time format chosen on the application is in the proper format to be processed.
    if start_time.endswith("PM"):
        start_time = str(int(start_time[:-2]) + 12)
        print(f"The new start time is {start_time}")

    elif start_time.endswith("AM"):
        start_time = start_time[:-2]

    if start_time == "12":
        start_time = "00"
        print(f"The new start time is {start_time}")

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
            shift = night_shifts[letter.upper()][week_day - 1]
        else:
            shift = night_shifts[letter.upper()][week_day]
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

            sys.exit()

        if color == "red":
            global alarm_bool
            alarm_bool = True
            break_thread = threading.Thread(target = chime_alarm)
            break_thread.daemon = True
            break_thread.start()
            


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
        set_keepawake(keep_screen_awake = False)
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

                    color = "orange"

                    work_time = start_time_list[i]

                    print(f"\nThe new work time is {work_time}")

                    end_of_phase = work_time + timedelta(hours = shift_hour)
                    
                    #end_of_phase_timestamp = datetime.timestamp(end_of_phase)

                    print(f"This shift will end by {end_of_phase}")

                    print(f"\nThe last hour of this shift is : {end_of_phase.hour},while the current hour is : {current_hour}")
                    
                    set_shift_status(shift_batch, shift_batch_list, "Running", indexer = i/2)
                    
                    clock_starter(current_time, end_of_phase, color, clock_use, shift_size, i)

                    set_shift_status(shift_batch, shift_batch_list, "Finished", indexer = i/2)

                    

                elif i % 2 != 0 and i < shift_size:
                    
                    color = "red"
                    
                    break_time = start_time_list[i]

                    breaktime_end = break_time + timedelta(hours = shift_hour)
                
                    
                    print(f"\n Break time starts now at {break_time}")
                    print(f"\nBreak time ends at {breaktime_end}")
                    print(f"\n current time starts now at {current_time}")
                    #start_hour = datetime.timestamp(in_lobby_time) + (shift_hour * 3600)

                    #breaktime_timestamp = datetime.timestamp(breaktime)

                    

                    clock_starter(current_time, breaktime_end, color, clock_use, shift_size, i)

                    

                elif i >= shift_size:
                    print("I will break away now")
                    set_shift_status(shift_batch, shift_batch_list, "Finished", indexer = i/2)
                    break


        else:
            #LOGGING INFO
            print("Please wait while your shift begins...")
            logger.info("The shift has not yet begun")
            
            time_left = (start_time - current_time)/timedelta(hours=1)
            

            print(f"Waiting for {time_left * 60 * 60} seconds")

            time.sleep(time_left * 60 *60)
            hour_left = math.ceil(time_left)
            minutes_left = time_left * 60
            print(f"You have time left of: {hour_left} hours, {minutes_left} minutes")  
            shift_times_var.set(f"Time before shift begins: {hour_left} hours, {minutes_left} minutes\nPlease wait while your shift begins...\n")
        current_time = datetime.now()

    #LOGGING INFO
    print(f"shift completed by {current_time}")
    logger.info(f"shift completed by {current_time}")
    color = "blue"
    radio_color_update(color)
    var.set(color)
    unset_keepawake()
    sys.exit()
    

    total_shift_run = total_shift_run - 1
    




    
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
            for i, minute in enumerate(range(minutes, -1, -1)):
                if i == 0:
                
                    for second in range(seconds - 1, -1, -1):
                        
                        clock_setter(hour, minute, second)

                elif i > 0:
                    for second in range(59, -1, -1):

                        clock_setter(hour, minute, second)


        elif j > 0 and clock_use > 1:
            for i, minute in enumerate(range(59, -1, -1)):
                if i == 0:
                    for second in range(seconds, -1, -1):
                            
                        clock_setter(hour, minute, second)

                elif i > 0:
                    for second in range(59, -1, -1):

                        clock_setter(hour, minute, second)



        elif j > 0 or clock_use > 1:
            for i, minute in enumerate(range(minutes, -1, -1)):
                if i == 0:
                    for second in range(seconds, -1, -1):
                        
                        clock_setter(hour, minute, second)

                elif i > 0:
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
    #sys.exit()
    t_thread = threading.Thread(target = shift_controller)
    t_thread.daemon = True

    #This is actually the code that starts the whole application. And it is started on a thread.
    t_thread.start()




def chime_alarm():
    """
    This is a function that starts the alarm whenever a break time has ended. The alarm will continue to ring unless it is stopped because it is in a while loop.
    The sound of the alarm is gotten from the chime module. The alarm is controlled by toggling a global variable called alarm_bool, which is a boolean value.
    If the alarm_bool is True, the alarm will keep ringing. To turn it off, we need to set the alarm_bool to False. This is why a global varible is needed so that we can apply another
    function to change the value of this alarm_bool, and effectively turn off the alarm.

    """
    global alarm_bool
    import winsound
    while alarm_bool:

        #The name of the sound is called the info sound in the chime module
        #chime.info(sync = True)
        winsound.Beep(1000, 1000)
        #The sound is regulated to be at 1 beep per second using the sleep method of the time module.
        time.sleep(1)

        #The alarm_bool value is checked to see if it has been changed. If it has break out of the while loop that restarts the chime.info() sound, else continue the chime.info() sound.
        if not alarm_bool:
            break


def alarm_off():
    """
    This is the function that helps to toggle the alarm_bool value to False. This function is called whenever the "Alarm Off" button is clicked. When this button is clicked, the global
    variable, alarm_bool whose value is True if the alarm is on, will be toggled to False. Once this value is False, the while loop from the chime_alarm() function ends and the alarm goes
    off
    """
    global alarm_bool
    alarm_bool = False






















window = tk.Tk()
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
letter_dropdown= tk.OptionMenu(frame_left, letter_menu, "A", "B", "C", "D", "E","F", "G", "H", "I", "J",
                 "k", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V",
                 "W", "X")



#Entry/Label Creation: Start time
label_time = tk.Label(master = frame_left, text = "Start time")
entry_time = tk.Entry(master = frame_left, width = 5)
start_time_menu= tk.StringVar()
start_time_menu.set("Choose Time")

#Create a dropdown Menu
time_dropdown= tk.OptionMenu(frame_left, start_time_menu, "12AM", "1AM", "2AM", "3AM", "4AM", "5AM",
                 "1PM", "2PM", "3PM", "4PM", "5PM", "6PM", "7PM", "8PM", "9PM", "10PM",
                 "11PM")



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
