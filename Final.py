# CHECK TRESHHOLD
# ASK ABOUT THE GOAL
# ASK ABOUT THE REFEREE COMMAND

# import the necessary packages
from collections import deque
from numpy import interp
import math
import argparse
import imutils
import cv2
import serial
import time

# Command for motors
# use function sd(motor 0 speed, motor 1 speed, motor 2 speed)

# Ideal coordinates of the ball
ball_x = 300
ball_y = 300

# Frame size
length_x = 600
length_y = 300

# Sensor Value
ball_sensor = 0

# When it's stuck between two
ball_counter_two = 0
ball_radius_two = 0

# List for opponent goal centerpoints, so that we know which way to turn
opponent_goal_centre = []


# Serial communication
port = "COM4"
baud = 9600
ser = serial.Serial(port, baud, serial.EIGHTBITS, timeout=0)
def sc(command):
    if ser.isOpen:
        ser.write(command + '\r\n')

# RF Serial
port = "COM6"
baud = 9600
rf = serial.Serial(port, baud, serial.EIGHTBITS, timeout=0)
'''def srf():
    global rf_input, start, stop
    if rf.isOpen:
        #print 'Enter your commands below.\r\nInsert "exit" to leave the application.'
        rf_input = raw_input()
        stop = rf_input
        rf.write(rf_input) # + '\r\n')
        print rf_input'''


#start = time.time()

def kick():
    return sc('k1')

def ball_value():
    return ser.read(1)
    
        
def sd_all(a,b,c,d):
    return sc('a'+str(a)+'b'+str(b)+'c'+str(c)+'d'+str(d))

def sd(a,b,c):
    return sc('a'+str(a)+'b'+str(b)+'c'+str(c))

def cnts_width(cnt):
    leftmost = int((cnt[cnt[:,:,0].argmin()][0])[0])
    rightmost = int((cnt[cnt[:,:,0].argmax()][0])[0])
    return abs(rightmost - leftmost)

def cnts_height(cnt):
    topmost = int((cnt[cnt[:,:,1].argmin()][0])[1])
    bottommost = int((cnt[cnt[:,:,1].argmax()][0])[1])
    return abs(topmost - bottommost)

def goal_position(cnt):
    if cnts_width(cnt) > (cnts_height(cnt)*2):
        return True
    else:
        return False

def biggest_contour(cnts):
    for i, c in enumerate(cnts):
        area = cv2.contourArea(c)
        areaArray.append(area)
    bc = (sorted(zip(areaArray, cnts), key=lambda x: x[0], reverse=True))[0][1]
    return bc

def contour_centre(cnts):
    centre = []
    moments_b = cv2.moments(biggest_contour(cnts))
    centre.append(int(moments_b['m10'] / moments_b['m00']))
    centre.append(int(moments_b['m01'] / moments_b['m00']))
    return centre


#rf('AX')
# construct the argument parse and parse the argumentsq
ap = argparse.ArgumentParser()
'''ap.add_argument("-v", "--video",
                help="path to the (optional) video file")'''
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# upper and lower boundaries for orange (ball) and blue (one of the goals)
orangeLower = (0, 114, 139)
orangeUpper = (8, 255, 255)
blueLower = (105,52,29)
blueUpper = (145,149,152)
yellowLower = (0,39,172)
yellowUpper = (26,142,253)
whiteLower = (0,15,132)
whiteUpper = (181,67,255)
greenLower = (43,46,32)
greenUpper = (111,177,84)
blackLower = (0,7,44)
blackUpper = (181,137,101)

pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)

seq = ''
balli = ''
toggle = 0
once = 1
sen_counter = 0
green_signal = 0

f_r = 'BB'
start_var = 'a' + f_r + 'START'
stop_var = 'a' + f_r + 'STOP'
ready = 'a' + f_r + 'PING'
acknowledge = 'a' + f_r + 'ACK------'


# keep looping
while True:

    
    for c in rf.read():
        seq = seq+c
        #print seq
        if 'aBXSTART' in seq :
            seq = ''
            #print 'SUCCESS'
            toggle = 1
            time.sleep(0.1)
            #sd_all(0,0,0,1)
            #rf.write(acknowledge)
            print 'SUCCESS'
            #time.sleep(1.0)
            
            #sd('d1')
            break

        elif start_var in seq :
            seq = ''
            #print 'SUCCESS'
            toggle = 1
            #sd_all(0,0,0,1)
            rf.write(acknowledge)
            print 'SUCCESS'
            #time.sleep(1.0)
            
            #sd('d1')
            break

        elif ready in seq:
            seq = ''
            rf.write(acknowledge)
            break
    
    #print 'out of loop'
    while toggle == 1:

        # grab the current frame
        (grabbed, frame) = camera.read()

        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if args.get("video") and not grabbed:
            break


        for c in rf.read():
            seq = seq+c
            #print seq
            if 'aBXSTOP' in seq:
                seq = ''
                toggle = 0
                #rf.write('aABPING')
                print 'STOP!!'
                time.sleep(0.1)
                sd_all(0,0,0,0)
                break

            elif stop_var in seq:
                seq = ''
                toggle = 0
                rf.write(acknowledge)
                print 'STOP!!'
                time.sleep(0.1)
                sd_all(0,0,0,0)
                break

            elif ready in seq:
                seq = ''
                rf.write(acknowledge)
                break
            
        #print 'SUCCESS'
        
        #ball_sensor = 0
        if '1' in ser.read():
            sen_counter = sen_counter + 1
            if sen_counter > 8:
                ball_sensor = 1
                sen_counter = 0
        
        #else:
            #ball_sensor = 0

        #if ball_sensor == 1:
            #kick()
            
        #print 'boo'

        # resize the frame, blur it, and convert it to the HSV
        # color space
        frame = imutils.resize(frame, width=600)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # construct a mask for the colors "orange" and "blue", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, orangeLower, orangeUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        mask2 = cv2.inRange(hsv, blueLower, blueUpper)
        mask2 = cv2.erode(mask2, None, iterations=2)
        mask2 = cv2.dilate(mask2, None, iterations=2)

        mask3 = cv2.inRange(hsv, yellowLower, yellowUpper)
        mask3 = cv2.erode(mask3, None, iterations=2)
        mask3 = cv2.dilate(mask3, None, iterations=2)

        mask4 = cv2.inRange(hsv, whiteLower, whiteUpper)
        mask4 = cv2.erode(mask4, None, iterations=2)
        mask4 = cv2.dilate(mask4, None, iterations=2)

        mask5 = cv2.inRange(hsv, greenLower, greenUpper)
        mask5 = cv2.erode(mask5, None, iterations=2)
        mask5 = cv2.dilate(mask5, None, iterations=2)

        mask6 = cv2.inRange(hsv, blackLower, blackUpper)
        mask6 = cv2.erode(mask6, None, iterations=2)
        mask6 = cv2.dilate(mask6, None, iterations=2)

        # find contours in the mask and initialize the current
        cnts, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        cnts2 = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts3 = cv2.findContours(mask3.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts4 = cv2.findContours(mask4.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts5 = cv2.findContours(mask5.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts6 = cv2.findContours(mask6.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]


        # cnts2 for blue --- cnts3 for yellow
        cntsg = cnts2
        # our goal
        cntso = cnts3

        areaArray = []

        # for finding the ball 
        if len(cnts) == 0 and ball_sensor == 0 and cntsg == 0 and ctso > 0:
            sd_all(-75,0,75,1)
        elif len(cnts) == 0 and ball_sensor == 0:
            sd_all(50,50,50,1)

        # only proceed if at least one contour was found
        if len(cnts) > 0 and ball_sensor == 0:
            for i, c in enumerate(cnts):
                area = cv2.contourArea(c)
                areaArray.append(area)

            # first sort the array by area
            #bc_b for biggest contour for ball
            bc_b = (sorted(zip(areaArray, cnts), key=lambda x: x[0], reverse=True))[0][1]

            centre_ball = []
            moments_b = cv2.moments(bc_b)
            centre_ball.append(int(moments_b['m10'] / moments_b['m00']))
            centre_ball.append(int(moments_b['m01'] / moments_b['m00']))
            cv2.circle(frame, (centre_ball[0],centre_ball[1]), 3, (0, 0, 0), -1)

            #print (centre_ball)
            # draw it
            x, y, w, h = cv2.boundingRect(bc_b)
            cv2.drawContours(frame, bc_b, -1, (0, 165, 255), 2)

            # Kerttu: calculating the radius for the ball by taking two extreme points from the contour: left and right
            ball_radius_calculated = int(math.sqrt(math.pow(
                tuple(bc_b[bc_b[:, :, 0].argmin()][0])[0] - tuple(bc_b[bc_b[:, :, 0].argmax()][0])[0],
                2) + math.pow(
                tuple(bc_b[bc_b[:, :, 0].argmin()][0])[1] - tuple(bc_b[bc_b[:, :, 0].argmax()][0])[1],
                2)) / 2)

            ball_radius = ball_radius_calculated
            #print(ball_radius)

            if ball_radius_two == 0:
                ball_radius_two = ball_radius
            if (ball_radius_two < (ball_radius+7)) and (ball_radius_two > (ball_radius-7)):
                ball_counter_two += 1
            if (ball_counter_two > 50):
                sd_all(-100,100,100,1)

            # Moving the motors
            #turn right
            if (centre_ball[0] > 330) and (ball_radius < 18):
                sd_all(75,75,75,1)
                #if (ball_sensor ==1):
                    #sd_all(0,0,0,0)
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break
                
            if (centre_ball[0] > 330) and (ball_radius >= 18):
                sd_all(75,75,75,1);
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break
                

            #turn left
            if (centre_ball[0] < 230) and (ball_radius < 18):
                sd_all(-75,-75,-75,1)
                #if (ball_sensor ==1):
                    #sd_all(0,0,0,0)
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break
                
            if (centre_ball[0] < 230) and (ball_radius >= 18):
                sd_all(-75,-75,-75,1)
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break

            
            #go forward
            if (centre_ball[0] > 230) and (centre_ball[0] < 330) and ball_radius < 18:
                sd_all(-350,0,350,1)
                #if (ball_sensor ==1):
                    #sd_all(0,0,0,0)
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break

            if (centre_ball[0] > 230) and (centre_ball[0] < 330) and ball_radius > 18:
                sd_all(-250,0,250,1)
                #if (ball_sensor ==1):
                    #sd_all(0,0,0,0)
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break



        # for finding the opponent's goal
        '''if len(cntsg) == 0 and ball_sensor == 1:
            bigger = 0
            smaller = 0
            if opponent_goal_centre > 4:
                for i in range(len(opponent_goal_centre)-1):
                    if opponent_goal_centre[i][0] < opponent_goal_centre[i+1][0]:
                        bigger += 1
                    else:
                        smaller += 1
                if smaller == 0:
                    # print('smaller')
                    sd_all(-80,-80,-80,1)
                elif bigger == 0:
                    # print('bigger')
                    sd_all(80,80,80,1)
            else:
                sd_all(-80,-80,-80,1)'''
        

        if ball_sensor == 1 and len(cntsg) == 0:
            sd_all(150,150,150,1)
            
        if len(cntsg) > 0 and ball_sensor == 1:
            ball_counter_two = 0
            ball_radius_two = 0
            
            # goal area
            for i, c in enumerate(cntsg):
                area = cv2.contourArea(c)
                areaArray.append(area)

            # first sort the array by area
            # bc_g = goal contour
            bc_g = (sorted(zip(areaArray, cntsg), key=lambda x: x[0], reverse=True))[0][1]
            centre_goal = []
            moments_g = cv2.moments(bc_g)
            centre_goal.append(int(moments_g['m10'] / moments_g['m00']))
            centre_goal.append(int(moments_g['m01'] / moments_g['m00']))
            cv2.circle(frame, (centre_goal[0], centre_goal[1]), 3, (0, 0, 0), -1)

            if len(opponent_goal_centre) < 11:
                opponent_goal_centre.append(centre_goal)
            else:
                opponent_goal_centre = []

        
            
            # draw it
            x, y, w, h = cv2.boundingRect(bc_g)
            #cv2.drawContours(frame, bc_g, -1, (255, 0, 0), 2)

            #if cnts

            #turn right
            if (centre_goal[0] > 330):
                value_right = int(interp(centre_goal[0],[380,600],[0,100]))
                sd_all(30,30,30,1)
                if toggle == 0:
                    sd_all(0,0,0,0)
            
            #turn left
            if (centre_goal[0] < 300):
                value_left = int(interp(centre_goal[0],[280,0],[0,100]))
                sd_all(-30,-30,-30,1)
                if toggle == 0:
                    sd_all(0,0,0,0)

            if (centre_goal[0] > 300 and centre_goal[0] < 330): # and goal_position(bc_g):
                sd_all(0,0,0,1)
                #time.sleep(2)
                kick()
                ball_sensor=0

            #goal_position(bc_g)'''


        
        cv2.drawContours(frame, cnts2, -1, (52, 180, 205), 2)
        #cv2.drawContours(frame, cnts4, -1, (255, 255, 255), 2)
        #cv2.drawContours(frame, cnts, -1, (0, 255, 0), 2)
            


        # show the frame to our screen
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

    # if the 'esc' key is pressed, stop the loop
        if cv2.waitKey(1) & 0xFF == 27:
            break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
#ser.close()
