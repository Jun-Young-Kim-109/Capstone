from buttonClass import *
import os

raspberry_pi = False

#############################
#     Fonts                 #
#                           #
#############################

font = pygame.font.SysFont('agencyfb', 40)
small_font = pygame.font.SysFont('agencyfb', 20)
big_font = pygame.font.SysFont('agencyfb', 70)
rpm_font = pygame.font.SysFont('agencyfb', 40)

#############################
#    Images                 #
#                           #
#############################

if raspberry_pi:
    quattro_image = pygame.image.load("/home/pi/Desktop/OBD_Delay/images/sportquattro.jpg")  # for RPI 4
    gauge_image = pygame.image.load("/home/pi/Desktop/OBD_Delay/images/gaugecrop.jpg")
    needle_image = pygame.image.load("/home/pi/Desktop/OBD_Delay/images/needtransp.png")
else:
    path = os.path.dirname(os.path.abspath(__file__)) + "/images"
    quattro_image = pygame.image.load(path + "/sportquattro.jpg")
    gauge_image = pygame.image.load(path + "/gaugecrop.jpg")
    needle_image = pygame.image.load(path + "/needtransp.png")

#############################
#      DTC TEXT             #
#                           #
#############################

text = small_font.render("WELCOME TO THE CODE READER", True, silver)
dtc_text = font.render("OBDII CODES:", True, white)
no_codes = 'There are no codes at this time'
no_codes = small_font.render(no_codes, True, white)

#############################
#      Virtual Dash         #
#          Text             #
#                           #
#############################

rpm_text = font.render("RPM", True, orange)
degree_sign = u"\N{DEGREE SIGN}"
deg_C = font.render(degree_sign + "C", True, orange)
coolant_temp_text = font.render("Coolant", True, yellow)
o2_trim_text = font.render("O2 Trim", True, yellow)
percent = font.render("%", True, orange)
intake_temp_text = font.render("Intake", True, yellow)
maf_text = font.render("MAF", True, yellow)
gs_text = font.render("G/S", True, orange)
timing_text = font.render("Adv.", True, yellow)
psi_text = font.render("PSI", True, orange)
fuel_rail_text = font.render("Fuel Rail", True, magenta)
fuel_rail_text2 = font.render("Pressure", True, magenta)
engine_load_e = font.render("Engine", True, magenta)
engine_load_l = font.render("Load", True, magenta)
afr_text = font.render("AFR", True, magenta)
speed_text = font.render("Speed", True, yellow)
mph = font.render("km/h", True, orange)
throttle_pos_text = font.render("Pos", True, yellow)
score_text = font.render("Safe Driving Score", True, magenta)
rapid_acceleration_text = font.render("R-Accel:", True, yellow)
rapid_deceleration_text = font.render("R-Decel:", True, yellow)
o2_sensors_text = font.render("O2 Sensors:", True, magenta)
o2_b1s1_text = font.render("O2 B1S1:", True, yellow)
o2_b1s2_text = font.render("O2 B1S2:", True, yellow)
fuel_status_text = font.render("Fuel Status:", True, magenta)
short_fuel_trim_1_text = font.render("Short Trim 1:", True, yellow)
long_fuel_trim_1_text = font.render("Long Trim 1:", True, yellow)
