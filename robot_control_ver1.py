import tkinter as tk
from tkinter import ttk
import random

class Robot:

    def __init__(self, p_over_rotate = 0.2, p_not_rotate = 0.1 , p_not_move = 0.1 , p_over_move = 0.15):
        self.p_over_rotate = p_over_rotate
        self.p_not_rotate = p_not_rotate
        self.p_rotate = 1 - p_over_rotate - p_not_rotate
        self.p_not_move = p_not_move
        self.p_over_move = p_over_move
        self.p_move = 1 - p_over_move - p_not_move
        self.p_move_arr = [self.p_not_move, self.p_move, self.p_over_move]
        self.orientation = [0,1]
        self.robot_coord = []
        self.orientation_dict = {'N': [-1, 0], 'E': [0, 1], 'S': [1, 0], 'W': [0, -1]}
        self.under_robot = 0
        self.around_robot = []
        self.robot_prediction_map = [[1/(4*4) for i in range(4)] for j in range(4)]
        self.robot_p_ried = {'gnus' : 0.7, 'zubp' : 0.5, 'fost' : 0.3, 'grnd' :0}

    def place(self, coord_x, coord_y, orientation): # ориентацию задаем в формате БУКВЫ
        self.robot_coord = [coord_x, coord_y]
        self.orientation = Robot.transform_orientation(self, orientation)

    def transform_orientation(self, orientation):
        if type(orientation) == str:
            return self.orientation_dict[orientation]
        else:
            keys = [key for key, val in self.orientation_dict.items() if val == orientation]
            return keys[0]

    def rotate(self,turn):
        if turn == 'right':
            self.orientation = list(self.orientation_dict.values())[(list(self.orientation_dict.values()).index(self.orientation) + 1) % len(list(self.orientation_dict.values()))]
        else:
            self.orientation = list(self.orientation_dict.values())[(list(self.orientation_dict.values()).index(self.orientation) - 1) % len(list(self.orientation_dict.values()))]

    def sense_all(self, real_map):
        self.under_robot = real_map[self.robot_coord[0]][self.robot_coord[1]]
        self.around_robot = []
        for i in range(4):
            self.around_robot +=[real_map[self.robot_coord[0] + self.orientation[0]][self.robot_coord[1] + self.orientation[1]]]
            Robot.rotate(self,'right')
        # нормализация
        for i in range(len(list(self.orientation_dict.values())) - list(self.orientation_dict.values()).index(self.orientation)):
            self.around_robot += [self.around_robot[0]]
            self.around_robot.pop(0)

    def predict_place(self,real_map):
        print(self.around_robot)
        robot_sr_pred = [[0 for i in range(4)] for j in range(4)]
        for i in range(4):
            for j in range(4):
                result = (self.under_robot == real_map[i + 1][j + 1])
                robot_sr_pred[i][j] += (0.9 * result) + (0.1 * (1 - result))
                for k in range(len(self.around_robot)):
                    help_orientation_mas = [[-1,0],[0,1],[1,0],[0,-1]]
                    result = (self.around_robot[k] == real_map[i + 1 + help_orientation_mas[k][0]][j + 1 + help_orientation_mas[k][1]])
                    robot_sr_pred[i][j] += ((0.75 * result) + (0.25 * (1 - result)))
        suma = sum(sum(i) for i in robot_sr_pred)
        robot_sr_pred = [[robot_sr_pred[j][i] / suma for i in range(4)] for j in range(4)]
        for i in range(4):
            for j in range(4):
                self.robot_prediction_map[i][j] = robot_sr_pred[i][j] * self.robot_prediction_map[i][j]
        for i in self.robot_prediction_map:
            print(i)
        print('----------predict_place--------')

    def move(self):
        new_robot_prediction_map = [[0 for i in range(4)] for j in range(4)]
        for i in range(4):
            for j in range(4):
                start_location = self.robot_prediction_map[i][j]
                for range_mov in range(3):
                    if i + self.orientation[0] * range_mov < 4 and j + self.orientation[1] * range_mov < 4 and i + self.orientation[0] * range_mov >= 0 and j + self.orientation[1] * range_mov >= 0:
                        Z = range_mov > 0
                        new_robot_prediction_map[i + self.orientation[0] * range_mov][j + self.orientation[1] * range_mov] += (((self.p_move_arr[range_mov] + self.robot_p_ried[real_map[i + 1][j + 1]] ) + (1 - Z)) * start_location) +  (Z * self.p_move_arr[range_mov] * start_location * (1 - self.robot_p_ried[real_map[i + 1][j + 1]]))
# неправильно счиатется вероятность проезда по теоритории
        self.robot_prediction_map = new_robot_prediction_map
        if random.random() > self.robot_p_ried[real_map[self.robot_coord[0]][self.robot_coord[1]]]:
            if self.robot_coord[0] + self.orientation[0] - 1 < 4 and self.robot_coord[1] + self.orientation[1] - 1< 4 and self.robot_coord[0] + self.orientation[0] - 1 >=0  and self.robot_coord[1] + self.orientation[1] - 1 >= 0:
                self.robot_coord = [self.robot_coord[0] + self.orientation[0], self.robot_coord[1] + self.orientation[1]]
        for i in self.robot_prediction_map:
            print(i)
        print('----------move_predict--------')

# на карте есть разные объекты это
# 'gnus' гнусмусы вероятность не поехать 0.7
# 'zubp' зыбучие вероятность не поехать 0.5
# 'fost' лес верояность не проехать 0.3
# 'grnd' ровная земля вероятность не проехать 0
# вся карта ограничена водой 'watr'

real_map = [
    ['watr', 'watr', 'watr', 'watr', 'watr', 'watr'],
    ['watr', 'grnd', 'gnus', 'zubp', 'grnd', 'watr'],
    ['watr', 'grnd', 'fost', 'fost', 'gnus', 'watr'],
    ['watr', 'gnus', 'zubp', 'fost', 'grnd', 'watr'],
    ['watr', 'zubp', 'grnd', 'grnd', 'fost', 'watr'],
    ['watr', 'watr', 'watr', 'watr', 'watr', 'watr'],
]

class RobotGUI:
    def __init__(self, robot, real_map):
        self.robot = robot
        self.real_map = real_map
        
        self.root = tk.Tk()
        self.root.title("Robot Control")
        
        # Создаем фреймы для карт
        self.maps_frame = ttk.Frame(self.root)
        self.maps_frame.grid(row=0, column=0, padx=10, pady=10)
        
        # Создаем канвасы для карт
        self.real_canvas = tk.Canvas(self.maps_frame, width=600, height=600)
        self.real_canvas.grid(row=0, column=0, padx=5)
        
        self.pred_canvas = tk.Canvas(self.maps_frame, width=400, height=400)
        self.pred_canvas.grid(row=0, column=1, padx=5)
        
        # Создаем кнопки управления
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.grid(row=1, column=0, pady=10)
        
        ttk.Button(self.control_frame, text="Move", command=self.move).grid(row=0, column=0, padx=5)
        ttk.Button(self.control_frame, text="Rotate Left", command=lambda: self.rotate('left')).grid(row=0, column=1, padx=5)
        ttk.Button(self.control_frame, text="Rotate Right", command=lambda: self.rotate('right')).grid(row=0, column=2, padx=5)
        ttk.Button(self.control_frame, text="Sense", command=self.sense).grid(row=0, column=3, padx=5)
        ttk.Button(self.control_frame, text="Predict", command=self.predict).grid(row=0, column=4, padx=5)
        
        self.images = {
           # 'watr': tk.PhotoImage(file="images/watr.png"),
            #'grnd': tk.PhotoImage(file="images/grnd.png"),
            #'gnus': tk.PhotoImage(file="images/gnus.png"),
           # 'zubp': tk.PhotoImage(file="images/zubp.png"),
           # 'fost': tk.PhotoImage(file="images/fost.png")
        }

        # Словарь цветов для различных типов местности
        self.colors = {
            'watr': 'blue',
            'grnd': 'brown',
            'gnus': 'gray',
            'zubp': 'yellow',
            'fost': 'green'
        }
        
        self.draw_maps()

    def draw_maps(self):
        
        # Очищаем канвасы
        self.real_canvas.delete("all")
        self.pred_canvas.delete("all")

        cell_size = 80
        for i in range(6):
            for j in range(6):
                terrain_type = self.real_map[i][j]
                if terrain_type in self.images:
                    self.real_canvas.create_image(
                        j * cell_size + cell_size/2,
                        i * cell_size + cell_size/2,
                        image=self.images[terrain_type]
                    )
                else:
                    color = self.colors.get(self.real_map[i][j], 'white')
                    self.real_canvas.create_rectangle(j * cell_size, i * cell_size,
                                                              (j + 1) * cell_size, (i + 1) * cell_size,
                                                              fill=color)

                    
        # Рисуем реальную карту
        # for i in range(6):
        #     for j in range(6):
        #         color = self.colors.get(self.real_map[i][j], 'white')
        #         self.real_canvas.create_rectangle(j * cell_size, i * cell_size,
        #                                           (j + 1) * cell_size, (i + 1) * cell_size,
        #                                           fill=color)

        # robot_x = self.robot.robot_coord[1] * cell_size + cell_size/2
        # robot_y = self.robot.robot_coord[0] * cell_size + cell_size/2
        
        # # Вычисляем угол поворота для робота
        # angle_dict = {'N': 0, 'E': 90, 'S': 180, 'W': 270}
        # orientation_letter = self.robot.transform_orientation(self.robot.orientation)
        
        # # Создаем повернутое изображение робота
        # rotated_robot = self.robot_image.subsample(3, 3)  # Уменьшаем размер изображения
        # self.real_canvas.create_image(robot_x, robot_y, image=rotated_robot)
        
        # Рисуем робота
        robot_x = self.robot.robot_coord[1] * cell_size + cell_size / 2
        robot_y = self.robot.robot_coord[0] * cell_size + cell_size / 2
        self.real_canvas.create_oval(robot_x - 10, robot_y - 10, robot_x + 10, robot_y + 10, fill='red')

        # Рисуем направление робота
        end_x = robot_x + self.robot.orientation[1] * 20
        end_y = robot_y + self.robot.orientation[0] * 20
        self.real_canvas.create_line(robot_x, robot_y, end_x, end_y, arrow=tk.LAST, width=3)

        # Рисуем карту вероятностей
        pred_cell_size = 60
        padding = 20

        # Получаем размеры матрицы вероятностей
        rows = len(self.robot.robot_prediction_map)
        cols = len(self.robot.robot_prediction_map[0])

        # Находим максимальное и минимальное значение вероятности
        max_prob = float('-inf')
        min_prob = float('inf')
        for i in range(rows):
            for j in range(cols):
                prob = self.robot.robot_prediction_map[i][j]
                max_prob = max(max_prob, prob)
                min_prob = min(min_prob, prob)

        for i in range(rows):
            for j in range(cols):
                prob = self.robot.robot_prediction_map[i][j]

                # Нормализуем вероятность от 50 до 255 (чтобы избежать слишком темных клеток)
                intensity = int(50 + ((prob - min_prob) / (max_prob - min_prob if max_prob != min_prob else 1)) * 205)
                color = f'#{intensity:02x}{intensity:02x}{intensity:02x}'

                x1 = j * pred_cell_size + padding
                y1 = i * pred_cell_size + padding
                x2 = (j + 1) * pred_cell_size + padding
                y2 = (i + 1) * pred_cell_size + padding

                # Рисуем прямоугольник с белой границей
                self.pred_canvas.create_rectangle(x1, y1, x2, y2,
                                                  fill=color,
                                                  outline='white',
                                                  width=1)

                # Добавляем текст с вероятностью в центр ячейки
                text_color = 'black' if intensity > 128 else 'white'
                self.pred_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                             text=f'{prob:.3f}',
                                             font=('Arial', 10),
                                             fill=text_color)
    
    def move(self):
        self.robot.move()
        self.draw_maps()
        
    def rotate(self, direction):
        self.robot.rotate(direction)
        self.draw_maps()
        
    def sense(self):
        self.robot.sense_all(self.real_map)
        self.draw_maps()
        
    def predict(self):
        self.robot.predict_place(self.real_map)
        self.draw_maps()
        
    def run(self):
        self.root.mainloop()


# Заменить последние строки на:
rb = Robot()
rb.place(2, 2, 'S')
gui = RobotGUI(rb, real_map)
gui.run()








