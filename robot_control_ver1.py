import tkinter as tk
from tkinter import ttk
import random
from PIL import Image, ImageTk

"""
TO DO
Сделать функцию настройки
Сделать алгоритм проходки от одно точки до другой
разобраться с реалестичностью 
"""


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
                robot_sr_pred[i][j] += (0.9 * result) + (0.1 * (1 - result))
                for k in range(len(self.around_robot)):
                    help_orientation_mas = [[-1, 0], [0, 1], [1, 0], [0, -1]]
                    result = (self.around_robot[k] == real_map[i + 1 + help_orientation_mas[k][0]][
                        j + 1 + help_orientation_mas[k][1]])
                    robot_sr_pred[i][j] += ((0.75 * result) + (0.25 * (1 - result)))
        for i in robot_sr_pred:
            print(i)
        print('---------ver 1---------------')
        suma = sum(sum(i) for i in robot_sr_pred)
        self.robot_prediction_map = [[robot_sr_pred[j][i] / suma for i in range(4)] for j in range(4)]
        for i in robot_sr_pred:
            print(i)
        print('---------ver 1---------------')
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
        #if random.random() > self.robot_p_ried[real_map[self.robot_coord[0] - 1][self.robot_coord[1] - 1]]:
        if self.robot_coord[0] + self.orientation[0] - 1 < self.map_size and self.robot_coord[1] + self.orientation[1] - 1 < self.map_size and self.robot_coord[0] + self.orientation[0] - 1 >= 0 and self.robot_coord[1] + self.orientation[1] - 1 >= 0:
            self.robot_coord = [self.robot_coord[0] + self.orientation[0],
                                self.robot_coord[1] + self.orientation[1]]
        print('Suma = ', sum(sum(i) for i in self.robot_prediction_map))
        print('----------move_predict--------')


def generate_map(size):
    # Создаем карту с водой по краям

    new_map = [['watr' for _ in range(size + 2)] for _ in range(size + 2)]

    # Заполняем внутреннюю часть случайными элементами
    terrain_types = ['grnd', 'gnus', 'zubp', 'fost']
    for i in range(1, size + 1):
        for j in range(1, size + 1):
            new_map[i][j] = random.choice(terrain_types)

    return new_map


# Инициализация начальной карты
real_map = generate_map(4)


class RobotGUI:
    def __init__(self, robot, real_map):
        self.robot = robot
        self.real_map = real_map

        self.root = tk.Tk()
        self.root.title("Robot Control")

        # Создаем верхнюю панель управления
        self.top_control_frame = ttk.Frame(self.root)
        self.top_control_frame.pack(pady=5, padx=10, fill='x')

        # Добавляем спиннер для размера карты
        ttk.Label(self.top_control_frame, text="Map Size:").pack(side='left', padx=5)
        self.size_var = tk.StringVar(value="4")
        self.size_spinner = ttk.Spinbox(self.top_control_frame, from_=4, to=12,
                                        textvariable=self.size_var, width=5)
        self.size_spinner.pack(side='left', padx=5)

        # Кнопка генерации новой карты
        ttk.Button(self.top_control_frame, text="Generate New Map",
                   command=self.generate_new_map).pack(side='left', padx=5)

        # Создаем фрейм для карт
        self.maps_frame = ttk.Frame(self.root)
        self.maps_frame.pack(pady=10, padx=10)

        # Создаем канвасы для карт
        self.real_canvas = tk.Canvas(self.maps_frame, width=600, height=600)
        self.real_canvas.grid(row=0, column=0, padx=5)

        self.pred_canvas = tk.Canvas(self.maps_frame, width=400, height=400)
        self.pred_canvas.grid(row=0, column=1, padx=5)

        # Создаем нижнюю панель управления
        self.bottom_control_frame = ttk.Frame(self.root)
        self.bottom_control_frame.pack(pady=10)

        # Кнопки управления
        ttk.Button(self.bottom_control_frame, text="Move",
                   command=self.move).pack(side='left', padx=5)
        ttk.Button(self.bottom_control_frame, text="Rotate Left",
                   command=lambda: self.rotate('left')).pack(side='left', padx=5)
        ttk.Button(self.bottom_control_frame, text="Rotate Right",
                   command=lambda: self.rotate('right')).pack(side='left', padx=5)
        ttk.Button(self.bottom_control_frame, text="Predict",
                   command=self.predict).pack(side='left', padx=5)
        ttk.Button(self.bottom_control_frame, text="Sense",
                   command=self.sense).pack(side='left', padx=5)

        self.images = {
            'watr': (ImageTk.PhotoImage(Image.open("images/watr.png").resize((80, 80)))),
            'grnd': (ImageTk.PhotoImage(Image.open("images/grnd.png").resize((80, 80)))),
            'gnus': (ImageTk.PhotoImage(Image.open("images/gnus.png").resize((80, 80)))),
            'zubp': (ImageTk.PhotoImage(Image.open("images/zubp.png").resize((80, 80)))),
            'fost': (ImageTk.PhotoImage(Image.open("images/fost.png").resize((80, 80))))
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

    def generate_new_map(self):
        size = int(self.size_var.get())
        self.map_size = size
        self.real_map = generate_map(size)
        # Обновляем размер prediction map робота
        self.robot.update_prediction_size(size)
        # Перемещаем робота в центр новой карты
        self.robot.place(size // 2, size // 2, 'S')
        self.draw_maps()

    def draw_maps(self):
        # Очищаем канвасы
        self.real_canvas.delete("all")
        self.pred_canvas.delete("all")

        map_size = len(self.real_map)
        cell_size = min(600 // map_size, 80)  # Масштабируем размер ячейки

        for i in range(map_size):
            for j in range(map_size):
                terrain_type = self.real_map[i][j]
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = (j + 1) * cell_size
                y2 = (i + 1) * cell_size

                if terrain_type in self.images:
                    # Масштабируем изображение под новый размер ячейки
                    img = Image.open(f"images/{terrain_type}.png").resize((cell_size, cell_size))
                    photo = ImageTk.PhotoImage(img)
                    # Сохраняем ссылку на изображение
                    setattr(self, f"img_{i}_{j}", photo)
                    self.real_canvas.create_image(
                        x1 + cell_size / 2,
                        y1 + cell_size / 2,
                        image=getattr(self, f"img_{i}_{j}")
                    )
                else:
                    color = self.colors.get(terrain_type, 'white')
                    self.real_canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        # Рисуем робота
        robot_x = self.robot.robot_coord[1] * cell_size + cell_size / 2
        robot_y = self.robot.robot_coord[0] * cell_size + cell_size / 2
        self.real_canvas.create_oval(robot_x - 10, robot_y - 10, robot_x + 10, robot_y + 10, fill='blue')

        # Рисуем направление робота
        end_x = robot_x + self.robot.orientation[1] * 20
        end_y = robot_y + self.robot.orientation[0] * 20
        self.real_canvas.create_line(robot_x, robot_y, end_x, end_y, arrow=tk.LAST, width=3)

        # Рисуем карту вероятностей
        pred_size = len(self.robot.robot_prediction_map)
        pred_cell_size = min(400 // pred_size, 60)
        padding = 20

        max_prob = max(max(row) for row in self.robot.robot_prediction_map)
        min_prob = min(min(row) for row in self.robot.robot_prediction_map)

        for i in range(pred_size):
            for j in range(pred_size):
                prob = self.robot.robot_prediction_map[i][j]
                intensity = int(50 + ((prob - min_prob) / (max_prob - min_prob if max_prob != min_prob else 1)) * 205)
                color = f'#{intensity:02x}{intensity:02x}{intensity:02x}'

                x1 = j * pred_cell_size + padding
                y1 = i * pred_cell_size + padding
                x2 = (j + 1) * pred_cell_size + padding
                y2 = (i + 1) * pred_cell_size + padding

                self.pred_canvas.create_rectangle(x1, y1, x2, y2,
                                                  fill=color,
                                                  outline='white',
                                                  width=1)

                text_color = 'black' if intensity > 128 else 'white'
                self.pred_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                             text=f'{prob:.3f}',
                                             font=('Arial', 10),
                                             fill=text_color)

    def move(self):
        self.robot.move(self.real_map)
        self.draw_maps()

    def rotate(self, direction):
        self.robot.rotate(direction)
        self.draw_maps()

    def sense(self):
        self.robot.sense_all(self.real_map)
        self.draw_maps()

    def predict(self):
        self.robot.sense_all(self.real_map)
        self.robot.predict_place(self.real_map)
        self.draw_maps()

    def run(self):
        self.root.mainloop()


# Заменить последние строки на:
rb = Robot()
rb.place(2, 2, 'S')
gui = RobotGUI(rb, real_map)
gui.run()
