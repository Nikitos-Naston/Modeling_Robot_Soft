import random
import time


class Robot():
    """
    Robot class for simulating robot movement and localization on a grid map.
    """

    def __init__(self, map_size, p_over_rotate=0.2, p_not_rotate=0.1, p_not_move=0.2, p_sense_under_right = 0.9, p_sense_forward_right = 0.75):
        """
        Initialize robot with movement probabilities and map parameters.

        Args:
            map_size (int): Size of the square grid map
            p_over_rotate (float): Probability of over-rotating (default 0.2)
            p_not_rotate (float): Probability of not rotating (default 0.1)
            p_not_move (float): Probability of not moving (default 0.2)
            p_sense_under_right (float): Probability of sensing under robot right (default 0.9)
            p_sense_forward_right (float): Probability of sensing forward right (default 0.75)
        """
        self.p_sense_under_right = p_sense_under_right
        self.p_sense_forward_right = p_sense_forward_right
        self.p_over_rotate = p_over_rotate  # Probability of over-rotating
        self.p_not_rotate = p_not_rotate  # Probability of not rotating
        self.p_rotate = 1 - p_over_rotate - p_not_rotate  # Probability of correct rotation
        self.p_not_move = p_not_move  # Probability of not moving
        self.p_move = 1 - p_not_move  # Probability of moving
        self.orientation = [1, 0]  # Current orientation vector
        self.robot_coord = []  # Current robot coordinates
        self.orientation_dict = {'N': [-1, 0], 'E': [0, 1], 'S': [1, 0], 'W': [0, -1]}  # Direction vectors
        self.under_robot = 0  # Terrain type under robot
        self.around_robot = []  # Terrain types around robot
        self.map_size = map_size  # Size of the map
        self.robot_prediction_map = [[1 / (map_size ** 2) for i in range(map_size)] for j in range(map_size)]  # Probability distribution of robot location

        # Probability of getting stuck in different terrain types
        self.robot_p_ried = {'gnus': 0.7, 'zubp': 0.5, 'fost': 0.3, 'grnd': 0.0, 'watr': 1.0}

    def change_map_params(self, p_gnus, p_zubp, p_fost, p_grnd):
        """
        For setting
        Update terrain probabilities for different terrain types.

        Args:
            p_gnus (float): Probability for 'gnus' terrain (default 0.7) picture with dwarf
            p_zubp (float): Probability for 'zubp' terrain (default 0.5) picture with sand
            p_fost (float): Probability for 'fost' terrain (default 0.3) picture with mashroom
            p_grnd (float): Probability for 'grnd' terrain (default 0.0) picture with road
        """
        self.robot_p_ried = {'gnus': p_gnus, 'zubp': p_zubp, 'fost': p_fost, 'grnd': p_grnd, 'watr': 1.0}

    def update_prediction_size(self, new_size):
        """
        Update map size and reinitialize prediction map.

        Args:
            new_size (int): New size for the square grid map
        """
        self.map_size = new_size
        self.robot_prediction_map = [[1 / (new_size * new_size) for i in range(new_size)] for j in range(new_size)]

    def place(self, coord_x, coord_y, orientation):
        """
        For setting
        Place robot at specific coordinates with given orientation.
        Args:
            coord_x (int): X coordinate
            coord_y (int): Y coordinate
            orientation (str): Direction ('N', 'E', 'S', 'W')
        """
        self.robot_coord = [coord_x, coord_y]
        self.orientation = Robot.transform_orientation(self, orientation)

    def transform_orientation(self, orientation):
        """
        Convert between string and vector orientation formats.

        Args:
            orientation: Either string ('N','E','S','W') or vector ([x,y])

        Returns:
            Vector if input is string, string if input is vector
        """
        if type(orientation) == str:
            return self.orientation_dict[orientation]
        else:
            keys = [key for key, val in self.orientation_dict.items() if val == orientation]
            return keys[0]

    def rotate(self, turn):
        """
        Rotate robot left or right.

        Args:
            turn (str): Direction to turn ('left' or 'right')
        """
        if turn == 'right':
            self.orientation = list(self.orientation_dict.values())[
                (list(self.orientation_dict.values()).index(self.orientation) + 1) % len(
                    list(self.orientation_dict.values()))]
        else:
            self.orientation = list(self.orientation_dict.values())[
                (list(self.orientation_dict.values()).index(self.orientation) - 1) % len(
                    list(self.orientation_dict.values()))]

    def sense_all(self, real_map):
        """
        Sense terrain under and around robot.

        Args:
            real_map (list): 2D list representing the terrain map
        """
        self.under_robot = real_map[self.robot_coord[0]][self.robot_coord[1]]
        self.around_robot = []
        for i in range(4):
            self.around_robot += [
                real_map[self.robot_coord[0] + self.orientation[0]][self.robot_coord[1] + self.orientation[1]]]
            Robot.rotate(self, 'right')

        # Normalize sensor readings
        for i in range(len(list(self.orientation_dict.values())) - list(self.orientation_dict.values()).index(
                self.orientation)):
            self.around_robot += [self.around_robot[0]]
            self.around_robot.pop(0)

    def predict_place(self, real_map):
        """
        Predict robot position prediction based on sensor readings.

        Args:
            real_map (list): 2D list representing the terrain map
        """
        robot_sr_pred = [[0 for i in range(self.map_size)] for j in range(self.map_size)]
        for i in range(self.map_size):
            for j in range(self.map_size):
                result = (self.under_robot == real_map[i + 1][j + 1])
                robot_sr_pred[i][j] += (self.p_sense_under_right * result) + ((1 - self.p_sense_under_right) * (1 - result))
                for k in range(len(self.around_robot)):
                    help_orientation_mas = [[-1, 0], [0, 1], [1, 0], [0, -1]]
                    result = (self.around_robot[k] == real_map[i + 1 + help_orientation_mas[k][0]][
                        j + 1 + help_orientation_mas[k][1]])
                    robot_sr_pred[i][j] += ((self.p_sense_forward_right * result) + ((1 - self.p_sense_forward_right) * (1 - result)))
        suma = sum(sum(i) for i in robot_sr_pred)
        self.robot_prediction_map = [[robot_sr_pred[j][i] / suma for i in range(self.map_size)] for j in
                                     range(self.map_size)]
        # for test
        # print('Suma = ', sum(sum(i) for i in self.robot_prediction_map))
        # print('----------predict_place--------')

    def find_optimal_path(self, map, start=(2, 2), end=(5, 5)):
        """
        Find path  with minimal probility of stuck
        between two points considering terrain difficulty.

        Args:
            map (list): 2D list representing terrain map
            start (tuple): Starting coordinates (x,y)
            end (tuple): End coordinates (x,y)

        Returns:
            list: List of coordinates representing optimal path
        """
        ver_map = [[self.robot_p_ried[map[j][i]] for i in range(len(map))] for j in range(len(map))]
        dp = [[float('inf')] * len(ver_map) for _ in range(len(ver_map))]
        prev = [[None] * len(ver_map) for _ in range(len(ver_map))]
        dp[start[0]][start[1]] = ver_map[start[0]][start[1]]
        queue = [(start[0], start[1])]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < len(ver_map) and 0 <= new_y < len(ver_map[0]):
                    new_prob = dp[x][y] + ver_map[new_x][new_y]
                    if new_prob < dp[new_x][new_y]:
                        dp[new_x][new_y] = new_prob
                        prev[new_x][new_y] = [x, y]
                        queue.append((new_x, new_y))
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = prev[curr[0]][curr[1]]
        path.reverse()
        print(path)
        return path

    def find_position(self):
        """
        Find most likely robot position based on prediction map.

        Returns:
            tuple: Most likely coordinates (x,y) of robot position
        """
        X, Y, max_now = 0, 0, -100
        for i in range(len(self.robot_prediction_map)):
            for j in range(len(self.robot_prediction_map)):
                if self.robot_prediction_map[i][j] > max_now:
                    max_now = self.robot_prediction_map[i][j]
                    X, Y = i + 1, j + 1
        return (X, Y)

    def move(self, real_map):
        """
        Move robot and update position predictions.
        Takes into account probabilities of getting stuck in different terrains.
        !!! REALISM , with some probability can not move in different terrains
        Args:
            real_map (list): 2D list representing terrain map
        """
        new_robot_prediction_map = [[0 for i in range(self.map_size)] for j in range(self.map_size)]
        #making predicition map
        for i in range(self.map_size):
            for j in range(self.map_size):
                start_location = self.robot_prediction_map[i][j]
                if i + self.orientation[0] < self.map_size and j + self.orientation[1] < self.map_size and i + \
                        self.orientation[0] >= 0 and j + self.orientation[1] >= 0:
                    new_robot_prediction_map[i][j] += ((self.p_not_move + self.robot_p_ried[
                        real_map[i + 1][j + 1]] * self.p_move) * start_location)

                    new_robot_prediction_map[i + self.orientation[0]][j + self.orientation[1]] += (
                            self.p_move * start_location * (1 - self.robot_p_ried[real_map[i + 1][j + 1]]))
                else:
                    new_robot_prediction_map[i][j] += start_location * (
                            self.p_not_move + self.p_move * self.robot_p_ried[
                        real_map[i + 1][j + 1]]) + start_location * self.p_move * (
                                                              1 - self.robot_p_ried[real_map[i + 1][j + 1]])
        self.robot_prediction_map = new_robot_prediction_map
        # check for realism and move
        if random.random() >= self.robot_p_ried[real_map[self.robot_coord[0]][self.robot_coord[1]]]:
            if self.robot_coord[0] + self.orientation[0] - 1 < self.map_size and self.robot_coord[1] + self.orientation[1] - 1 < self.map_size and self.robot_coord[0] + self.orientation[0] - 1 >= 0 and self.robot_coord[1] + self.orientation[1] - 1 >= 0:
                self.robot_coord = [self.robot_coord[0] + self.orientation[0],
                                    self.robot_coord[1] + self.orientation[1]]
        #for test
        # print('Suma = ', sum(sum(i) for i in self.robot_prediction_map))
        # print('----------move_predict--------')



