
# run.py
# -*- coding: utf-8 -*-
import os
import pygame
import obd
import csv
import datetime
import glob
import time
import cv2
from constants import *
from video_recorder import VideoCaptureThread
import video_recorder
from video_recorder import video_recorder_main
from threading import Thread
import threading

obd_connection = obd.Async()
current_time = datetime.datetime.now()
folder_path = "/home/pi/Desktop/OBD2 Car Data"
obd.logger.setLevel(obd.logging.DEBUG)


if raspberry_pi:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
else:
    screen = pygame.display.set_mode((800, 480), pygame.NOFRAME)

pygame.display.set_caption('maker by Kim Jun Young')

try:
    # OBD 연결 시도
    connection = obd.Async("/dev/rfcomm0")

    # OBD 연결 상태 확인
    if connection.is_connected():
        obd_connected = True
    else:
        obd_connected = False
        print("Failed to connect to OBD. Running without OBD connection.")
except Exception as e:
    obd_connected = False
    print(f"Error occurred while connecting to OBD: {e}")
    connection = None
    
# Text size for flash messages
textPopUp = 100

# GUI buttons
virtualDash = button(20, 20, "Virtual Dash", screen)
dtc = button(350, 20, "Read Codes", screen)
quit = button(670, 20, "Quit", screen)
go_home = button(20, 20, "Home", screen)
data_log_off = button(350, 20, "Data Log", screen)
data_log_on = button(350, 20, "Logging", screen)
record_button = button(350, 65, "Record", screen)
back_button = button(670, 65, "Stop", screen)

#############################
#      Global Values        #
#                           #
#############################

rpm = 0
load = 0
maf = 0.0
o2_trim = 0.0
timing_advance = 0.0
coolant_temp = 0
fuel_rail_press = 0.0
intake_temp = 0
afr = 0.0
speed = 0
throttle_pos = 0
rapid_acceleration_count = 0 
rapid_deceleration_count = 0
fuel_status = "" 
short_fuel_trim_1 = 0.0 
long_fuel_trim_1 = 0.0  
o2_sensors = ""  
o2_b1s1 = 0.0  
o2_b1s2 = 0.0  
fuel_status_display = ""
o2_sensors_display = ""
distance = 0
codes = []
driving_score = 100
engine_load = 0
previous_speed = 0
logging_start_time = None
safety_message = None
safety_message_start_time = None
message_display_time = 5
previous_driving_score = 100
previous_distance = 0
score_decreased = False
speed_conditions = []
rpm_conditions = []
load_conditions = []
recording = False 
obd_connection = None
logging_active = False
LOGGING_INTERVAL = 0.2  # seconds
last_logging_time = datetime.datetime.now()
is_recording = False

#############################
#    RPM GAUGE FUNCTIONS    #
#                           #
#############################

def rpm_gauge():
    rpm_gauge = pygame.transform.scale(gauge_image, (210,210))
    return rpm_gauge
def gauge_needle():
    needle = pygame.transform.scale(needle_image, (190, 2))
    return needle
def rotate_needle(needle, angle):
    rotated_needle = pygame.transform.rotozoom(needle, angle, 1)
    return rotated_needle

#############################
#      VIRTUAL DASH         #
#       FUNCTIONS           #
#############################

def virtualDashIntro():
    text = small_font.render("WELCOME TO VIRTUAL DASH", True, green)
    text_box = text.get_rect()
    text_box.center = (405, 80)
    screen.blit(text, text_box)

def virtDash():
    global driving_score, previous_speed, logging_active
    gauge = rpm_gauge()
    angle = 36 * (rpm * -.001) + 90
    needle_copy = gauge_needle()
    needle_rotated = rotate_needle(needle_copy, angle)
    screen.blit(gauge, (int(screen.get_width() / 2 - 105), 200))

    # Centering equation courtesy of DaFluffyPotato on Youtube: https://www.youtube.com/channel/UCYNrBrBOgTfHswcz2DdZQFA
    screen.blit(needle_rotated, (int(screen.get_width() / 2) - int(needle_rotated.get_width() / 2),
                                 305 - int(needle_rotated.get_height() / 2)))
    if rpm < 3500:
        display_rpm = rpm_font.render(str(rpm), True, green)
    else:
        display_rpm = rpm_font.render(str(rpm), True, red)
    screen.blit(display_rpm, (365, 430))
    screen.blit(rpm_text, (430, 435))

    screen.blit(coolant_temp_text, (510, 175))
    coolant_temp_display = font.render(str(coolant_temp), True, white)
    screen.blit(coolant_temp_display, (540, 210))
    screen.blit(deg_C, (595, 230))

    screen.blit(speed_text, (355, 100))
    speed_text_display = font.render(str(speed), True, white)
    screen.blit(speed_text_display, (380, 150))
    screen.blit(mph, (420, 148))

    screen.blit(intake_temp_text, (200, 175))  
    intake_temp_display = font.render(str(intake_temp), True, white)
    screen.blit(intake_temp_display, (210, 215))
    screen.blit(deg_C, (260, 230))

    screen.blit(throttle_pos_text, (205, 300))
    throttle_pos_display = font.render(str("{:.1f}".format(throttle_pos)), True, white)
    screen.blit(throttle_pos_display, (205, 340))
    screen.blit(percent, (275, 360))

    screen.blit(timing_text, (525, 300))
    timing_adv_display = font.render(str("{:.1f}".format(timing_advance)), True, white)
    screen.blit(timing_adv_display, (535, 340))
    deg = font.render(degree_sign, True, orange)
    screen.blit(deg, (595, 346))
    
    screen.blit(o2_sensors_text, (630, 120))
    
    screen.blit(o2_b1s1_text, (665, 160))
    o2_b1s1_display = font.render(str(o2_b1s1), True, white)
    screen.blit(o2_b1s1_display, (680, 190))

    screen.blit(o2_b1s2_text, (665, 220))
    o2_b1s2_display = font.render(str(o2_b1s2), True, white)
    screen.blit(o2_b1s2_display, (680, 250))

    screen.blit(fuel_status_text, (630, 310))

    screen.blit(short_fuel_trim_1_text, (620, 345))
    short_fuel_trim_1_display = font.render(str(short_fuel_trim_1), True, white)
    screen.blit(short_fuel_trim_1_display, (670, 380))

    screen.blit(long_fuel_trim_1_text, (620, 410))
    long_fuel_trim_1_display = font.render(str(long_fuel_trim_1), True, white)
    screen.blit(long_fuel_trim_1_display, (670, 445))
    
    screen.blit(engine_load_e, (20, 295))
    screen.blit(engine_load_l, (20, 335))
    engine_l_display = big_font.render(str(int(load)), True, white)
    screen.blit(engine_l_display, (20, 375))
    screen.blit(percent, (100, 400))
    
    check_and_update_driving_score()
        
    screen.blit(score_text, (20, 100))
    driving_score_display = big_font.render(str(int(driving_score)), True, white)
    screen.blit(driving_score_display, (20, 140))
    
    screen.blit(rapid_acceleration_text, (20, 200))
    rapid_acceleration_display = font.render(str(rapid_acceleration_count), True, white)
    screen.blit(rapid_acceleration_display, (140, 200))
    
    screen.blit(rapid_deceleration_text, (20, 240))
    rapid_deceleration_display = font.render(str(rapid_deceleration_count), True, white)
    screen.blit(rapid_deceleration_display, (140, 240))
    
    if not logging_active:
        if data_log_off.draw_button():
            logging_active = True
            logging_start_time = datetime.datetime.now()
            print("Logging started")
    elif logging_active:
        if data_log_on.draw_button():
            logging_active = False
            print("Logging stopped")

    if logging_active:
        logging_text = font.render("Logging Active", True, red)
    else:
        logging_text = font.render("Logging Stop", True, green)
    screen.blit(logging_text, (465, 30))
    
#############################
#   DATA LOGGING FUNCTIONS  #
#############################

logging_active = font.render("Logging Active", True, red)
filename = "/home/pi/Desktop/OBD2 Car Data/data_logging_" + current_time.strftime("%Y_%m_%d") + ".csv"

header = ['Timestamp',
          'RPM',
          'Speed',
          'Coolant Temp',
          'Intake Temp',
          'Throttle Pos',
          'Timing Advance',
          'Short Fuel Trim 1',
          'Long Fuel Trim 1',
          'O2 B1S1',
          'O2 B1S2',
          'Engine Load',
          'Safety Score',
          'Distance',
          'Rapid Acceleration',
          'Rapid Dceleration']
          
# 파일이 존재하지 않는 경우에는 새로운 파일 생성
if not os.path.isfile(filename):
    mode = "w"
else:
    mode = "a"

with open(filename, mode, newline="") as dl:
    writer = csv.writer(dl)

    if mode == "w":
        # 새로운 파일인 경우에는 헤더를 작성
        writer.writerow(header)

    # 데이터 추가하기
    row = [str(current_time), str(rpm), str(speed), str(coolant_temp), str(intake_temp), str(throttle_pos), str(timing_advance), str(short_fuel_trim_1), str(long_fuel_trim_1), str(o2_b1s1), str(o2_b1s2), str(load), str(driving_score), str(distance), str(rapid_acceleration_count), str(rapid_deceleration_count)]
    writer.writerow(row)
    
logging_start_time = None

def log_to_file(file_name):
    global logging_start_time, distance, last_logging_time
    
    current_time = datetime.datetime.now()
    elapsed_time = (current_time - last_logging_time).total_seconds()
    
    if elapsed_time < LOGGING_INTERVAL:
        return  # 아직 로깅할 시간이 되지 않았으면 함수를 종료
        
    def manage_disk_space(folder_path, max_size, max_files):
        files = glob.glob(os.path.join(folder_path, "*.csv"))
        total_size = sum(os.path.getsize(file) for file in files)

        while total_size > max_size or len(files) > max_files:
            oldest_file = min(files, key=os.path.getctime)
            os.remove(oldest_file)
            files.remove(oldest_file)
            total_size -= os.path.getsize(oldest_file)

    screen.blit(logging_active, (467, 30))
    
    if not logging_active:
        return  # 로깅이 활성화되지 않은 경우 함수를 빠져나감

    current_time = datetime.datetime.now()
    folder_name = f"/home/pi/Desktop/OBD2 Car Data/{current_time.strftime('%Y-%m-%d')}"
    file_path = os.path.join(folder_name, file_name)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        
    file_path = os.path.join(folder_name, file_name)

    # Check if the file already exists
    if os.path.isfile(file_path):
    # File exists, open in append mode
        mode = "a"
    else:
    # File doesn't exist, create a new file
        mode = "w"

    if logging_start_time is None:
        logging_start_time = datetime.datetime.now()

    row = [current_time.strftime("%H:%M:%S"), str(rpm), str(speed), str(coolant_temp), str(intake_temp),
            str(throttle_pos), str(timing_advance), str(short_fuel_trim_1), str(long_fuel_trim_1), str(o2_b1s1),
            str(o2_b1s2), str(load), str(driving_score), str(distance), str(rapid_acceleration_count),
            str(rapid_deceleration_count)]

    with open(file_path, mode, newline="") as dl:
        writer = csv.writer(dl)

        if mode == "w":
            # Write header if it's a new file
            writer.writerow(header)

        writer.writerow(row)
        manage_disk_space(folder_path, 10 * 1024 * 1024 * 1024, 20)
        
        # 안전 운전 메세지 표시 함수 호출
        display_safety_messages(driving_score)

        # 안전 운전 메세지 표시 시간 확인
        check_message_display_time()
        
        
        print(f"Logging data at {current_time}")  # 디버깅 메시지 추가
        last_logging_time = current_time 
        
def get_file_size(file_path):
    size = os.path.getsize(file_path)
    return size

def delete_file(file_path):
    os.remove(file_path)

#############################
#   CODE READER FUNCTIONS   #
#############################


def dtcIntro():
    text_box = text.get_rect()
    text_box.center = (400, 30)
    screen.blit(text, text_box)

def display_dtc(code_list):
    screen.blit(dtc_text, (50, 100))
    y_loc = 200
    # Display DTC codes
    if len(code_list) != 0:
        for code in code_list:
            code = small_font.render(str(code), True, white)
            screen.blit(code, (60, y_loc))
            y_loc += 50
    else:
        screen.blit(no_codes, (60, 200))


#############################
#       GET FPS             #
#############################

# Fps function derived from pythonprogramming.com
# https://pythonprogramming.altervista.org/pygame-how-to-display-the-frame-rate-fps-on-the-screen/

def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps + " fps", 1, pygame.Color("coral"))
    return fps_text


#########################################
#   Functions to retrieve ECU data      #
#########################################

# Functions written as so defined by Python-OBD authors
# https://python-obd.readthedocs.io/en/latest/Async%20Connections/
def get_speed(s):
    global speed
    if not s.is_null():
        speed = int(s.value.magnitude )


def get_fuel_rail_press(fp):
    global fuel_rail_press
    if not fp.is_null():
        fuel_rail_press = float(fp.value.magnitude) * .145038  # kp to psi


def get_intake_temp(it):
    global intake_temp
    if not it.is_null():
        intake_temp = int(it.value.magnitude)  # C 


def get_afr(af):
    global afr
    if not af.is_null():
        afr = float(af.value.magnitude) * 14.64 # Convert to AFR for normal gasoline engines


def get_rpm(r):
    global rpm
    if not r.is_null():
        rpm = int(r.value.magnitude)


def get_load(l):
    global load
    if not l.is_null():
        load = int(l.value.magnitude)


def get_coolant_temp(ct):
    global coolant_temp
    if not ct.is_null():
        coolant_temp =int(ct.value.magnitude) # C


def get_intake_press(ip):
    global intake_pressure
    if not ip.is_null():
        intake_pressure = float(ip.value.magnitude)


def get_baro_press(bp):
    global baro_pressure
    if not bp.is_null():
        baro_pressure = float(bp.value.magnitude)


def get_dtc(c):
    global codes
    if not c.is_null():
        codes = c.value


def get_timing_a(ta):
    global timing_advance
    if not ta.is_null():
        timing_advance = str(ta.value).replace("degree", "") # in degrees / remove text from val
        timing_advance = float(timing_advance)


def get_maf(m):
    global maf
    if not m.is_null():
        maf = str(m.value).replace("gps", "")  # grams / second / remove text from val
        maf = float(maf)


def get_fuel_status(fs):
    global fuel_status, fuel_status_display
    if not fs.is_null():
        fuel_status = fs.value


def get_o2(o):
    global o2_trim
    if not o.is_null():
        o2_trim = str(o.value).replace("percent", "")  # +/- 3 percent normal range - negative = rich, positive = lean
        o2_trim = float(o2_trim)


def get_throttle_pos(tp):
    global throttle_pos, previous_speed
    if not tp.is_null():
        throttle_pos =  float(tp.value.magnitude)


def get_short_fuel_trim_1(sft1):
    global short_fuel_trim_1
    if not sft1.is_null():
        short_fuel_trim_1 = (sft1.value.magnitude)


def get_long_fuel_trim_1(lft1):
    global long_fuel_trim_1
    if not lft1.is_null():
        long_fuel_trim_1 = (lft1.value.magnitude)


def get_o2_sensors(os):
    global o2_sensors, o2_sensors_display
    if not os.is_null():
        o2_sensors = (os.value)


def get_o2_b1s1(o2b1s1):
    global o2_b1s1
    if not o2b1s1.is_null():
        o2_b1s1 = (o2b1s1.value.magnitude)


def get_o2_b1s2(o2b1s2):
    global o2_b1s2
    if not o2b1s2.is_null():
        o2_b1s2 = (o2b1s2.value.magnitude)


def calculate_distance():
    global distance, logging_start_time, previous_distance

    if logging_start_time is None:
        logging_start_time = datetime.datetime.now()

    current_time = datetime.datetime.now()
    time_difference = current_time - logging_start_time
    time_difference_seconds = time_difference.total_seconds()
    current_distance = (speed / 3600) * time_difference_seconds  # 현재 이동한 거리 계산

    distance = previous_distance + current_distance  # 이전 거리에 현재 이동한 거리를 더해 누적 거리 계산

    previous_distance = distance  # 이전에 이동한 거리 업데이트
    logging_start_time = current_time
    
def increase_count_based_on_acceleration(speed_diff):
    global rapid_acceleration_count, rapid_deceleration_count

    # 출발 직후에는 급가속 및 급감속 횟수를 계산하지 않도록 조건 추가
    if int(speed) >= 20:
        if speed_diff >= 6:  # 급가속 기준값 (7 km/h)
            rapid_acceleration_count += 1
            decrease_driving_score()

        elif speed_diff <= -8:  # 급감속 기준값 (-9 km/h)
            rapid_deceleration_count += 1
            decrease_driving_score()
            
def decrease_driving_score():
    global driving_score

    decrease_amount = 1  
    driving_score -= decrease_amount
    driving_score = max(driving_score, 0)

def calculate_driving_score(speed, rpm, load, throttle_pos):
    global driving_score

    speed_weight = 0.1
    rpm_weight = 0.1
    load_weight = 0.1
    throttle_pos_weight = 0.1

    # Store previous driving score
    previous_driving_score = driving_score

    # Decrease driving score based on speed, RPM, and load
    if int(speed) >= 80:
        speed_ratio = (int(speed) - 20) / 80  # Adjust speed range and calculate ratio (0 to 1)
        speed_penalty = (speed_ratio ** 0.5) * speed_weight  # Apply square root of ratio to penalty unit
        driving_score -= speed_penalty

    if int(rpm) >= 2500:
        rpm_ratio = (int(rpm) - 1800) / 2000  # Adjust RPM range and calculate ratio (0 to 1)
        rpm_penalty = (rpm_ratio ** 0.5) * rpm_weight  # Apply square root of ratio to penalty unit
        driving_score -= rpm_penalty

    if int(load) >= 50:
        load_ratio = (int(load) - 35) / 65  # Adjust load range and calculate ratio (0 to 1)
        load_penalty = (load_ratio ** 0.5) * load_weight  # Apply square root of ratio to penalty unit
        driving_score -= load_penalty

    if int(throttle_pos) >= 30:
        throttle_pos_ratio = (int(throttle_pos) - 25) / 75  # Adjust throttle position range and calculate ratio (0 to 1)
        throttle_pos_penalty = (throttle_pos_ratio ** 0.5) * throttle_pos_weight  # Apply square root of ratio to penalty unit
        driving_score -= throttle_pos_penalty
    
    driving_score = max(driving_score, 0)

    return driving_score

# 안전 운전 메세지 표시 함수
def display_safety_message(message, color):
    global safety_message, safety_message_start_time
    safety_message = font.render(message, True, color)
    safety_message_start_time = time.time()

# 메세지 표시 시간 확인 함수
def check_message_display_time():
    global safety_message_start_time, safety_message
    if safety_message_start_time is not None:
        current_time = time.time()
        elapsed_time = current_time - safety_message_start_time
        if elapsed_time >= message_display_time:
            safety_message = None
            safety_message_start_time = None

# 안전 운전 메세지 표시 함수 호출
def display_safety_messages(driving_score):
    if driving_score <= 70:
        display_safety_message("Danger", red) 
    elif driving_score <= 80:
        display_safety_message("Caution", yellow)
    elif driving_score <= 90:
        display_safety_message("Safe", green) 
        
def check_and_update_driving_score():
    global driving_score, speed_diff, previous_speed, previous_driving_score

    speed_diff = speed - previous_speed
    increase_count_based_on_acceleration(speed_diff)

    if driving_score != previous_driving_score:
        decrease_driving_score()
        previous_driving_score = driving_score

    previous_speed = speed

def handle_record_stop_buttons():
    global is_recording, video_thread

    if record_button.draw_button():
        if not is_recording:
            if video_thread is None or not video_thread.is_alive():
                is_recording = True
                try:
                    video_thread = Thread(target=video_recorder_main, args=(connection, 0, 30, 800, 480))
                    video_thread.start()
                except Exception as e:
                    print(f"Error starting video thread: {e}")
                    is_recording = False
            else:
                print("Video thread is already running.")

    if back_button.draw_button():
        if is_recording:
            is_recording = False
            if video_thread is not None and video_thread.is_alive():
                try:
                    video_thread.join()  # 스레드가 종료될 때까지 기다림
                    video_thread = None
                except Exception as e:
                    print(f"Error stopping video thread: {e}")
      
class LoggingThread(threading.Thread):
    def __init__(self, filename):
        super(LoggingThread, self).__init__()
        self.filename = filename
        self.running = True
        self.last_logging_time = datetime.datetime.now()

    def run(self):
        while self.running:
            self.log_to_file()

    def log_to_file(self):
        global logging_start_time, distance, last_logging_time

        current_time = datetime.datetime.now()
        elapsed_time = (current_time - self.last_logging_time).total_seconds()

        if elapsed_time >= LOGGING_INTERVAL:
            self.manage_disk_space(folder_path, 10 * 1024 * 1024 * 1024, 20)
            self.perform_logging()
            self.last_logging_time = current_time

    def manage_disk_space(self, folder_path, max_size, max_files):
        files = glob.glob(os.path.join(folder_path, "*.csv"))
        total_size = sum(os.path.getsize(file) for file in files)

        while total_size > max_size or len(files) > max_files:
            oldest_file = min(files, key=os.path.getctime)
            os.remove(oldest_file)
            files.remove(oldest_file)
            total_size -= os.path.getsize(oldest_file)

    def perform_logging(self):
        global logging_start_time
        current_time = datetime.datetime.now()
        folder_name = f"/home/pi/Desktop/OBD2 Car Data/{current_time.strftime('%Y-%m-%d')}"
        file_path = os.path.join(folder_name, self.filename)

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        if os.path.isfile(file_path):
            mode = "a"
        else:
            mode = "w"

        if logging_start_time is None:
            logging_start_time = current_time

        row = [current_time.strftime("%H:%M:%S"), str(rpm), str(speed), str(coolant_temp), str(intake_temp),
               str(throttle_pos), str(timing_advance), str(short_fuel_trim_1), str(long_fuel_trim_1), str(o2_b1s1),
               str(o2_b1s2), str(load), str(driving_score), str(distance), str(rapid_acceleration_count),
               str(rapid_deceleration_count)]

        with open(file_path, mode, newline="") as dl:
            writer = csv.writer(dl)

            if mode == "w":
                writer.writerow(header)

            writer.writerow(row)

    def stop(self):
        self.running = False


logging_thread = LoggingThread(filename)
logging_thread.start()


def ecu_connections():
    if connection:
        connection.watch(obd.commands.SPEED, callback=get_speed)
    connection.watch(obd.commands.RPM, callback=get_rpm)
    connection.watch(obd.commands.ENGINE_LOAD, callback=get_load)
    connection.watch(obd.commands.GET_DTC, callback=get_dtc)
    connection.watch(obd.commands.COOLANT_TEMP, callback=get_coolant_temp)
    connection.watch(obd.commands.INTAKE_TEMP, callback=get_intake_temp)
    connection.watch(obd.commands.FUEL_RAIL_PRESSURE_DIRECT, callback=get_fuel_rail_press)
    connection.watch(obd.commands.COMMANDED_EQUIV_RATIO, callback=get_afr)
    connection.watch(obd.commands.MAF, callback=get_maf)
    connection.watch(obd.commands.TIMING_ADVANCE, callback=get_timing_a)
    connection.watch(obd.commands.LONG_O2_TRIM_B1, callback=get_o2)
    connection.watch(obd.commands.THROTTLE_POS, callback=get_throttle_pos)
    connection.watch(obd.commands.FUEL_STATUS, callback=get_fuel_status)
    connection.watch(obd.commands.SHORT_FUEL_TRIM_1, callback=get_short_fuel_trim_1)
    connection.watch(obd.commands.LONG_FUEL_TRIM_1, callback=get_long_fuel_trim_1)
    connection.watch(obd.commands.O2_SENSORS, callback=get_o2_sensors)
    connection.watch(obd.commands.O2_B1S1, callback=get_o2_b1s1)
    connection.watch(obd.commands.O2_B1S2, callback=get_o2_b1s2)
    connection.start()

# Turn off debug mode
obd.logger.removeHandler(obd.console_handler)


# Game loop variables
run = True
home = True
vDash = False
dtcMode = False
logging = False
cnt = 0  # For flash messages
clock = pygame.time.Clock()  # Initiate clock for fps

# Call watch() for ecu connections
if connection:
    ecu_connections()


#################################
#          Game Loop            #
#################################
while run:
    
    current_time = datetime.datetime.now()
    screen.fill(black)
    screen.blit(update_fps(), (5, 446))
    #log_to_file(filename)
    
    if home:
        screen.blit(quattro_image, (0, 40))
        vDash = False
        dtcMode = False
        cnt = 0
        if virtualDash.draw_button():
            counter = 0
            home = False
            vDash = True

        if dtc.draw_button():
            home = False
            dtcMode = True
            
    if quit.draw_button():
        if logging_active:
            logging_active = False
            # 필요한 경우 로그 파일을 마무리하는 코드 추가
            print("Logging stopped before quitting")
        run = False
        
    if not home:
        if go_home.draw_button():
            home = True

    if vDash and cnt < textPopUp:
        virtualDashIntro()
        cnt += 1
        
    if dtcMode and cnt < textPopUp:
        dtcIntro()
        cnt += 1
        
    if home:
        if record_button.draw_button():
            video_recorder_main(connection, obd_connected, src=0,  frame_rate=15, width=800, height=480)
            video_thread.start()
        else:
            video_recorder.recording = False
            
    if vDash:
        virtDash()
        if not logging:
            if data_log_off.draw_button():
                logging = True
                logging_start_time = datetime.datetime.now()
                
        #if logging:
            #log_to_file(filename)

            if data_log_on.draw_button():
                logging = False
    
        
        speed_diff = speed - previous_speed
        increase_count_based_on_acceleration(speed_diff)
        
        previous_speed = speed
        
        check_and_update_driving_score()
    
        # 안전 운전 메세지 표시 함수 호출
        display_safety_messages(driving_score)

        # 안전 운전 메세지 표시 시간 확인
        check_message_display_time()

        # 안전 운전 메세지 표시
        if safety_message is not None:
            screen.blit(safety_message, (20, 65))
        
        calculate_distance()
        
    if dtcMode:
        display_dtc(codes)
    clock.tick(5)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                # Q 키가 눌렸을 때의 로직
                if is_recording:
                    # 영상 녹화 종료 및 저장 로직
                    is_recording = False
                    if video_thread is not None and video_thread.is_alive():
                        video_thread.join()  # 녹화 스레드가 종료될 때까지 기다림
                        video_thread = None
                    print("Recording stopped and saved.")
                
                # 홈 화면으로 상태 전환
                home = True
                vDash = False
                dtcMode = False
    pygame.display.update()
    pygame.display.flip()

logging_thread.stop()
logging_thread.join()

pygame.quit()

