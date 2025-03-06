import random

class Robot:

    def __init__(self, map_size=4, p_over_rotate=0.2, p_not_rotate=0.1, p_not_move=0.2):
        self.p_over_rotate = p_over_rotate
        self.p_not_rotate = p_not_rotate
        self.p_rotate = 1 - p_over_rotate - p_not_rotate
        self.p_not_move = p_not_move
        # self.p_over_move = p_over_move
        self.p_move = 1 - p_not_move
        self.orientation = [1, 0]
        self.robot_coord = []
        self.orientation_dict = {'N': [-1, 0], 'E': [0, 1], 'S': [1, 0], 'W': [0, -1]}
        self.under_robot = 0
        self.around_robot = []
        self.map_size = map_size
        self.robot_prediction_map = [[1 / (map_size * map_size) for i in range(map_size)] for j in range(map_size)]

        self.robot_p_ried = {'gnus': 0.7, 'zubp': 0.5, 'fost': 0.3, 'grnd': 0.1, 'watr': 1.0}

    def change_map_params(self, p_gnus, p_zubp, p_fost, p_grnd):
        self.robot_p_ried = {'gnus': p_gnus, 'zubp': p_zubp, 'fost': p_fost, 'grnd': p_grnd, 'watr': 1.0}

    def update_prediction_size(self, new_size):
        self.map_size = new_size
        self.robot_prediction_map = [[1 / (new_size * new_size) for i in range(new_size)] for j in range(new_size)]

    def place(self, coord_x, coord_y, orientation):  # ориентацию задаем в формате БУКВЫ
        self.robot_coord = [coord_x, coord_y]
        self.orientation = Robot.transform_orientation(self, orientation)

    def transform_orientation(self, orientation):
        if type(orientation) == str:
            return self.orientation_dict[orientation]
        else:
            keys = [key for key, val in self.orientation_dict.items() if val == orientation]
            return keys[0]

    def rotate(self, turn):
        if turn == 'right':
            self.orientation = list(self.orientation_dict.values())[
                (list(self.orientation_dict.values()).index(self.orientation) + 1) % len(
                    list(self.orientation_dict.values()))]
        else:
            self.orientation = list(self.orientation_dict.values())[
                (list(self.orientation_dict.values()).index(self.orientation) - 1) % len(
                    list(self.orientation_dict.values()))]

    def sense_all(self, real_map):
        self.under_robot = real_map[self.robot_coord[0]][self.robot_coord[1]]
        self.around_robot = []
        for i in range(4):
            self.around_robot += [
                real_map[self.robot_coord[0] + self.orientation[0]][self.robot_coord[1] + self.orientation[1]]]
            Robot.rotate(self, 'right')
        # нормализация
        for i in range(len(list(self.orientation_dict.values())) - list(self.orientation_dict.values()).index(
                self.orientation)):
            self.around_robot += [self.around_robot[0]]
            self.around_robot.pop(0)

    def predict_place(self, real_map):
        print(self.around_robot)
        robot_sr_pred = [[0 for i in range(self.map_size)] for j in range(self.map_size)]
        for i in range(self.map_size):
            for j in range(self.map_size):
                result = (self.under_robot == real_map[i + 1][j + 1])
                print(real_map[i + 1][j + 1])
                robot_sr_pred[i][j] += (0.9 * result) + (0.1 * (1 - result))
                for k in range(len(self.around_robot)):
                    help_orientation_mas = [[-1, 0], [0, 1], [1, 0], [0, -1]]
                    result = (self.around_robot[k] == real_map[i + 1 + help_orientation_mas[k][0]][
                        j + 1 + help_orientation_mas[k][1]])
                    robot_sr_pred[i][j] += ((0.75 * result) + (0.25 * (1 - result)))
        suma = sum(sum(i) for i in robot_sr_pred)
        self.robot_prediction_map = [[robot_sr_pred[j][i] / suma for i in range(self.map_size)] for j in
                                     range(self.map_size)]
        print('Suma = ', sum(sum(i) for i in self.robot_prediction_map))
        print('----------predict_place--------')

    def move(self, real_map):
        print(self.map_size)
        new_robot_prediction_map = [[0 for i in range(self.map_size)] for j in range(self.map_size)]
        for i in range(self.map_size):
            for j in range(self.map_size):
                start_location = self.robot_prediction_map[i][j]
                if i + self.orientation[0] < self.map_size and j + self.orientation[1] < self.map_size and i + self.orientation[0] >= 0 and j + self.orientation[1] >= 0:
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
        if random.random() > self.robot_p_ried[real_map[self.robot_coord[0]][self.robot_coord[1]]]:
            if self.robot_coord[0] + self.orientation[0] - 1 < self.map_size and self.robot_coord[1] + self.orientation[1] - 1 < self.map_size and self.robot_coord[0] + self.orientation[0] - 1 >= 0 and self.robot_coord[1] + self.orientation[1] - 1 >= 0:
                self.robot_coord = [self.robot_coord[0] + self.orientation[0],
                                    self.robot_coord[1] + self.orientation[1]]
        print('Suma = ', sum(sum(i) for i in self.robot_prediction_map))
        print('----------move_predict--------')


