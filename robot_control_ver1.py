import robot_model
import UI

"""
TO DO
Make an algorithm for passing from one point to another
to figure out the realism 
Refine the configuration function
"""

print('DEVELOPED BY DREAMTIM STAS, FAN, RODNIKOVA --- VER BETA.2')
print('Welcome to the robot movement simulation app')
print('First, adjust the probability of movement of the robot: \n Do you want to keep the basic settings? (y/n)', end = ' ')
answer = input('Probability of not going = 0.2, probability of going = 0.8').lower()
if answer == 'n':
    result = list(map(float, input('Enter the desired probabilities separated by commas(,) in the order indicated above.').split(',')))
    rb = robot_model.Robot(p_not_move = result[0])
else:
    rb = robot_model.Robot(p_not_move = 0.2)

print('Now configure the map: \n Do you want to keep the basic settings? (y/n)', end = ' ')
answer = input('Card size = 4 \n The probability of not traveling through the territory of gnusmus = 0.7 \n  The probability of not driving on the sand = 0.5 \n The probability of not traveling through the forest = 0.3 \n The probability of not going on the road = 0').lower()

if answer == 'n':
    result = list(map(float, input('Enter the desired map sizes and probabilities separated by commas(,) in the order indicated above.').split(',')))
    real_map = UI.generate_map(result[0])
    rb.change_map_params(result[1], result[2], result[3], result[4])
else:
    real_map = UI.generate_map(4)

print('Now arrange the work: \n Do you want to keep the basic settings? (y/n)', end = ' ')
answer = input('The robot will be positioned at position 2,2 with orientation S').lower()

if answer == 'n':
    result = list(map(str, input('Enter the desired location and orientation of the robot separated by commas(,)').split(',')))
    rb.place(int(result[0]), int(result[1]), result[2])
else:
    rb.place(2, 2, 'S')


gui = UI.RobotGUI(rb, real_map)
gui.run()
