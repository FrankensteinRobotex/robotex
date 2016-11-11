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

# List for blue goal centerpoints, so that we know which way to turn
blue_goal_centre = []

# Serial communication
port = "COM8"
baud = 9600
ser = serial.Serial(port, baud, serial.EIGHTBITS)
def sc(command):
    if ser.isOpen:
        ser.write(command + '\r\n')

'''# RF Serial
port = "COM5"
baud = 9600
rf = serial.Serial(port, baud, serial.EIGHTBITS)'''
'''def srf():
    global rf_input, start, stop
    if rf.isOpen:
        #print 'Enter your commands below.\r\nInsert "exit" to leave the application.'
        rf_input = raw_input()
        stop = rf_input
        rf.write(rf_input) # + '\r\n')
        print rf_input'''

#start = time.time()
        
def sd_all(a,b,c,d):
    return sc('a'+str(a)+'b'+str(b)+'c'+str(c)+'d'+str(d))

def sd(a,b,c):
    return sc('a'+str(a)+'b'+str(b)+'c'+str(c))


#rf('AX')
# construct the argument parse and parse the argumentsq
ap = argparse.ArgumentParser()
'''ap.add_argument("-v", "--video",
                help="path to the (optional) video file")'''
ap.add_argument("-b", "--buffer", type=int, default=64,
                help="max buffer size")
args = vars(ap.parse_args())

# upper and lower boundaries for orange (ball) and blue (one of the goals)
orangeLower = (3, 40, 42)
orangeUpper = (15, 235, 255)
blueLower = (106,32,51)
blueUpper = (122,255,151)
yellowLower = (2,54,168)
yellowUpper = (44,209,247)
whiteLower = (0,4,40)
whiteUpper = (45,206,220)
greenLower = (43,46,32)
greenUpper = (111,177,84)

pts = deque(maxlen=args["buffer"])

# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    camera = cv2.VideoCapture(0)

seq = ''
toggle = 1

# keep looping
while True:
    '''for c in rf.read():
        seq = seq+c
        #print seq
        if 'aAXSTART' in seq:
            seq = ''
            toggle = 1
            print 'SUCCESS'
            sd('d1')
            break'''

    while toggle == 1:

        '''for c in rf.read():
            seq = seq+c
            #print seq
            if 'aAXSTOP' in seq:
                seq = ''
                toggle = 0
                print 'STOP!!'
                time.sleep(0.5)
                sd_all(0,0,0,0)
                break'''
    
        # grab the current frame
        (grabbed, frame) = camera.read()
        stop = 0

        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if args.get("video") and not grabbed:
            break

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

        # find contours in the mask and initialize the current
        cnts, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        cnts2 = cv2.findContours(mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts3 = cv2.findContours(mask3.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts4 = cv2.findContours(mask4.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cnts5 = cv2.findContours(mask5.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        areaArray = []

        # for finding the blue goal
        '''if len(cnts2) == 0:
            bigger = 0
            smaller = 0
            if blue_goal_centre > 4:
                for i in range(len(blue_goal_centre)-1):
                    if blue_goal_centre[i][0] < blue_goal_centre[i+1][0]:
                        bigger += 1
                    else:
                        smaller += 1
                if smaller == 0:
                    sd(-25,-25,-25)
                elif bigger == 0:
                    sd(25,25,25)
            else:
                sd(-25,-50,25)

        # for finding the ball 
        if len(cnts) == 0:
            sd(-25,-50,25)'''
                    
    
        # only proceed if at least one contour was found
        if len(cnts) > 0:

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
        

            # Moving the motors
            #turn right
            if (centre_ball[0] > 350):
                #print("right")
                value_right = int(interp(centre_ball[0],[350,600],[0,250]))
                sd(-50,value_right,50)
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break
                

            #turn left
            if (centre_ball[0] < 250):
                value_left = int(interp(centre_ball[0],[250,0],[0,250]))
                sd(-50,-value_left,50)
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break
            

            #go forward
            if (centre_ball[0] > 250 and centre_ball[0] < 350): # and ball_radius < length_x/8):
                sd(-75,0,75)
                if toggle == 0:
                    sd_all(0,0,0,0)
                    break    



        if len(cnts2) > 0:
            # goal area
            for i, c in enumerate(cnts2):
                area = cv2.contourArea(c)
                areaArray.append(area)

            # first sort the array by area
            # bc_g = goal contour
            bc_g = (sorted(zip(areaArray, cnts2), key=lambda x: x[0], reverse=True))[0][1]
            centre_goal = []
            moments_g = cv2.moments(bc_g)
            centre_goal.append(int(moments_g['m10'] / moments_g['m00']))
            centre_goal.append(int(moments_g['m01'] / moments_g['m00']))
            cv2.circle(frame, (centre_goal[0], centre_goal[1]), 3, (0, 0, 0), -1)

            if len(blue_goal_centre) < 11:
                blue_goal_centre.append(centre_goal)
            else:
                blue_goal_centre = []

            #print (centre_goal)

            # draw it
            x, y, w, h = cv2.boundingRect(bc_g)
            cv2.drawContours(frame, bc_g, -1, (255, 0, 0), 2)



        
        
        cv2.drawContours(frame, cnts3, -1, (52, 180, 205), 2)
        cv2.drawContours(frame, cnts4, -1, (255, 255, 255), 2)
        cv2.drawContours(frame, cnts5, -1, (0, 255, 0), 2) 
            


    # show the frame to our screen
        #cv2.imshow("Frame", frame)
        #key = cv2.waitKey(1) & 0xFF

    # if the 'esc' key is pressed, stop the loop
        if cv2.waitKey(1) & 0xFF == 27:
            break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
#ser.close()
