# Here lies the code that makes Kevin, Kevin
# This is all written in Python. And since snakes don't understand hashtags, anytime you
# see something after a #, python ignores it. We use # to make comments in our programs
# to make it easier to understand.
#First we are going to import some prewritten code to make our lives easier
import time # this allows to easily make a delay
import math # this makes doing fancy math easy
import board # not sure
import neopixel # helps us control the neopixel lights
from digitalio import DigitalInOut, Direction # not exactly sure
import audioio # probably something to do with audio IO
import busio # ¯\_(ツ)_/¯
import pulseio # ¯\_(ツ)_/¯
import adafruit_lis3dh # helps us work with the accelerometer
import gc # garbage collection, which I dont really understand but it helps us manage memory
import adafruit_motor.servo # code to make working with servos easier
import random # random number stuff

# Next we are going to assign some constants and variables that we will need for Kevin to work
SERVO_PIN = board.D9 # basically giving a nicname to our servo_pin so that its easier to remember.
PIXEL_PIN = board.D5 # giving a nicname to the pin our neopixels are attached to
POWER_PIN = board.D10  # give a nicname to the enable pin that controls power to our leds and amp
AUDIO_PIN = board.A0 # give a nicname to the audio pin
flipper_closed_position = .5 # when we send this value to our servo it goes to the closed position
flipper_open_position = 1.7 # This sends our servo to the flip position. Increase it by 0.1 if it isn't flipping
HIT_THRESHOLD = 150 # decrease this number to make Kev more sensitive
last_event_time = 0 # number used to keep track of hits, and rolls
time_to_wait_before_moving = 15 #Kev has to be left alone 15 seconds before he can roll
time_to_wait_between_hits = 2
Flippable = False # This is a boolean, or a true/false value. We use this one to store whether Kev can Flip
z_value_at_rest_high = 10 # value we use to determine if Kevin is sitting up and can roll
z_value_at_rest_low = 7 # value we use to determine if Kevin is sitting up and can roll
max_gas_pressure = 6000 # Max amount of gas Kev can hold back
fart_time = 1.5 # Average length of each Cube Toot
gas_pressure = 0 # Start Kev's gas pressure at 0
gas_production_rate = 3 # amount of gas produced each time through the loop
kevin_is_hit = False #Boolean to store if Kev is hit. To start, we're going to say False or NO!
kevin_can_move = False # We want Kevin to start not moveable
flippability_just_changed = False # keep track if kevins orientation just changed
kevin_has_to_toot = False # I think you get it...

#Let's set up our enable pin. Both the audio amplifier and the lights have to be turned
#on by sending voltage to pin 10, our "POWER_PIN". 
enable = DigitalInOut(POWER_PIN)  #NicName time.
enable.direction = Direction.OUTPUT # Enable pin is an output because the program tells it what to do
enable.value = False # 

servo = pulseio.PWMOut(SERVO_PIN, frequency=50) # ¯\_(ツ)_/¯ Just do it
# this is our first function. It's a little confusing, but basically it allows us to control our servo easier
def servo_duty_cycle(pulse_ms, frequency=50):
    period_ms = 1.0 / frequency * 1000.0
    duty_cycle = int(pulse_ms / (period_ms / 65535.0))
    return duty_cycle

servo.duty_cycle = servo_duty_cycle(flipper_closed_position)# drive the servo to close the flipper_closed_position

# This is basically setting up our neopixel lights.
NUM_PIXELS = 5 #how many pixels? 5... okay lets give it a nicname
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=1, auto_write=False)
pixels.fill(0) # what color do you want to start your pixels with? Off? Perfect...
pixels.show() # Now display the setting

audio = audioio.AudioOut(AUDIO_PIN)     # Nicname to make our lives easier when playing audio

# Lets set up our accelerometer to detect when Kevin is hit. I never would have figured out how to write
# this code myself. So I found a program that used an accelerometer and stole this part of the code.
i2c = busio.I2C(board.SCL, board.SDA)
accel = adafruit_lis3dh.LIS3DH_I2C(i2c)
accel.range = adafruit_lis3dh.RANGE_4_G

#alright, something new. This is a function. It is a bit of code that is easy to reuse. I stole it from another program
def play_sound(name, loop=False):
    """
    Did you know snakes don't like quotes? Next time you see a snake, tell it "do, or do not, there is no try"
    then "Use the force Luke" then "Fear is the path to the dark side" and it will ignore you
    Just kidding. But this is how you do a block quote. Anything between these 3 quotation marks, the program
    will ignore. 
    Play a WAV file in the 'sounds' directory.
    @param name: partial file name string, complete name will be built around
                 this, e.g. passing 'foo' will play file 'sounds/foo.wav'.
    @param loop: if True, sound will repeat indefinitely (until interrupted
                 by another sound).
    """
    try:
        wave_file = open('sounds/' + name + '.wav', 'rb')
        wave = audioio.WaveFile(wave_file)
        audio.play(wave, loop=loop)
    except:
        return

#make a function to detect hits
def check_for_hit():
    global last_event_time 
    global kevin_is_hit
    current_time = time.monotonic() #check the time
    elapsed = current_time - last_event_time # how long between the last time something happened and now
    x, y, z, = accel.acceleration # get readings from our accelerometer
    accel_total = (x * x) + (y * y) + (z * z) # you should learn this in highschool but its a nifty way to display total
    #if kevin was hit hard enough and it has been long enough, do the following
    if accel_total > HIT_THRESHOLD and elapsed > time_to_wait_between_hits: 
        kevin_is_hit = True # lets remember kevin was hit
        last_event_time = current_time # let's remember when kevin was hit
    else:
        kevin_is_hit = False # otherwise do this

#This function controls Kev's reaction when hit
def get_mad_kevin():
    enable.value = True  #this enables the audio amp and lights
    file_name = 'kevinIsMad' #This is the name of the audio file in the sounds folder that we want to play
    play_sound(file_name) # calling the play_sound fuction above and telling it to play 'kevinIsMad'
    i = 0 
    while True: # this increases the brightness by 1 each time through the loop, from 0 all the way to 200
        if i > 200:
            break
        pixels.fill((i, i, i,))
        pixels.show()
        i += 1
    pixels.fill((0, 0, 0)) #turn the lights back off
    pixels.show()
    time.sleep(1) # wait one second for the sound to finish playing.
    enable.value = False # turn the power off to the lights and the amplifier
    
def check_to_see_if_kevin_can_move():# this fucntion checks if kevin is upright and has been left alone long enough
    global last_event_time
    global Flippable
    global kevin_can_move
    global flippability_just_changed
    current_time = time.monotonic()
    elapsed = current_time - last_event_time
    if elapsed > time_to_wait_before_moving: # check to see if he has been left alone long enough
        check_orientation()
        if Flippable is False or flippability_just_changed is True: # Flippable is false means kevin is on his side
            kevin_can_move = False
            return #our job here is done, return back where we were before we started the function
        else:
            kevin_can_move = True # since kevin can move, we need to write it down so we remember
            last_event_time = current_time # make note of the time we decided kevin can move

#this function makes kevin flip over
def roll_kevin_roll():
    global kevin_can_move
    servo.duty_cycle = servo_duty_cycle(flipper_open_position)# move kev's servo to the flip position
    time.sleep(1) #wait a second for the servo to reach the position
    servo.duty_cycle = servo_duty_cycle(flipper_closed_position) #close the servo
    time.sleep(1) #wait a second for the servo to reach the position
    kevin_can_move = False #set Kev can move to false since he obviously just rolled on his side.

#check to see if kevin is upright or on his side
def check_orientation():
    global Flippable
    global last_event_time
    global flippability_just_changed
    last_flippability = Flippable
    x, y, z, = accel.acceleration # get accelerometer readings
    if z > z_value_at_rest_high or z < z_value_at_rest_low: # if z values are out of range then kev is probably on side
        Flippable = False # since kevin is on side, don't try to flip him

    else:
        Flippable = True # otherwise you can flip him

    if last_flippability != Flippable: # kevin has just changed orientation which resets the event clock
        flippability_just_changed = True
        last_event_time = time.monotonic()
    
    else: 
        flippability_just_changed = False

# I bet you can figure out what this function does...
def check_to_see_if_kevin_has_to_let_one_rip():
    global kevin_has_to_toot
    if gas_pressure > max_gas_pressure: #if gas pressure is greater than the max, kevin has to toot
        kevin_has_to_toot = True
    else:
        kevin_has_to_toot = False #otherwise kevin can hold it

#the actual fart function
def let_er_rip():
    gc.collect() # ¯\_(ツ)_/¯ this is part of the memory management. No clue how/where/why it should be used but...yeah
    global gas_production_rate
    global gas_pressure
    enable.value = True #this enables the audio amp and lights, even though we will only use the amp
    random_fart_sound_number = random.randint(0, 5) # pick a random number between 1 and 5
    fart_sound_file_name = 'fart' + str(random_fart_sound_number) # randomly pick fart sound name
    play_sound(fart_sound_file_name) # use the play_sound function above to play random fart sound
    time.sleep(fart_time) # wait for the sound to finish
    enable.value = False # turn off the amplifier
    gas_pressure = 0 # reset gas_pressure since all the gas has been released
    gas_production_rate = random.randint(1, 7) #randomly set new gas production rate

#function to increase gas pressure each time it is called    
def create_gas():
    global gas_pressure #use global variable gas_pressure to store new amount of gas
    gas_pressure = gas_pressure + gas_production_rate # add gas to old gas_pressure value

"""
this is a super important part of the program. The loop. This is a while loop. And it continues doing
everything inside it while it is true. And since True is always True, it will loop over this next bit of
code forever and ever. Until you turn it off. Every single time through this loop, we check to see
if kevin was hit, we check to see if kevin can move, we check to see if kevin has to toot and then do
something if any of those conditions are true. So, we call the fuction we wrote above, check_for_hit. 
And if we find out kevin is hit, we call the function get_mad_kevin. Oh another thing we do is, every time
through the loop, the create_gas function is called, increase gas pressure just a little bit. So, there are
several ways you can diffuse the bomb. How many ways can you diffuse the bomb? 
"""
while True:
    check_for_hit()
    
    if kevin_is_hit is True:
        get_mad_kevin()

    check_to_see_if_kevin_can_move()
    
    if kevin_can_move is True:
        roll_kevin_roll()
    
    create_gas()
    check_to_see_if_kevin_has_to_let_one_rip()
    
    if kevin_has_to_toot is True:
        let_er_rip()
    