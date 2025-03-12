import robot_model
import UI

"""
TO DO
make soft more realism 
Refine the configuration function
make stupid check function
"""

# Greetings, basic setup
print('DEVELOPED BY DREAMTIM STAS, FAN, RODNIKOVA --- VER ALPHA 1.0')
print('Welcome to the robot movement simulation app')
print('First, adjust the probability of movement and sensing of the robot: \n Do you want to keep the basic settings? (y/n)', end = ' ')
answer = input('Probability of not going = 0.2 \n probability of successfully scanning area under robot = 0.9, probability of successfully scanning area in front of robot = 0.75').lower()
if answer == 'n':
    result_1 = list(map(float, input('Enter the desired probabilities separated by commas(,) in the order indicated above.').split(',')))

else:
    result_1 = [0.2, 0.9, 0.75]

print('Now configure the map: \n Do you want to keep the basic settings? (y/n)', end = ' ')
answer = input('Card size = 4 \n The probability of not traveling through the territory of gnusmus = 0.7 \n  The probability of not driving on the sand = 0.5 \n The probability of not traveling through the forest = 0.3 \n The probability of not going on the road = 0').lower()

if answer == 'n':
    result = list(map(float, input('Enter the desired map sizes and probabilities separated by commas(,) in the order indicated above.').split(',')))
    real_map = UI.generate_map(result[0])
    rb = robot_model.Robot(result[0],p_not_move = result_1[0])
    rb.change_map_params(result[1], result[2], result[3], result[4])

else:
    real_map = UI.generate_map(4)
    rb = robot_model.Robot(4,p_not_move = result_1[0], p_sense_under_right= 1 - result_1[0], p_sense_forward_right= result_1[1])

print('The last one, lets take the position and orientation of robot: \n Do you want to keep the basic settings? (y/n)', end = ' ')
answer = input('The robot will be positioned at position 2,2 with orientation S').lower()

if answer == 'n':
    result = list(map(str, input('Enter the desired location and orientation of the robot separated by commas(,)').split(',')))
    rb.place(int(result[1]), int(result[0]), result[2])
else:
    rb.place(2, 2, 'S')

gui = UI.RobotGUI(rb, real_map)
gui.run()

# for fast test
# rb = robot_model.Robot(6,p_not_move = 0.2)
# real_map = UI.generate_map(6)
# rb.place(2, 2, 'S')
# gui = UI.RobotGUI(rb, real_map)
# gui.run()

