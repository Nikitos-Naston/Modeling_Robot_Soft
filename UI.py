from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
import random
import time


class RobotGUI:
    """
    A class that implements a graphical interface for robot control and visualization
    """

    def __init__(self, robot, real_map):
        """
        Initialize the GUI

        Args:
            robot: Robot object for control
            real_map: Current map of the environment
        """
        self.robot = robot
        self.real_map = real_map

        self.root = tk.Tk()
        self.root.title("Robot Control")

        # Create top control panel
        self.top_control_frame = ttk.Frame(self.root)
        self.top_control_frame.pack(pady=5, padx=10, fill='x')

        # Add map size spinner
        ttk.Label(self.top_control_frame, text="Map Size:").pack(side='left', padx=5)
        self.size_var = tk.StringVar(value="4")
        self.size_spinner = ttk.Spinbox(self.top_control_frame, from_=4, to=12,
                                        textvariable=self.size_var, width=5)
        self.size_spinner.pack(side='left', padx=5)

        # New map generation button
        ttk.Button(self.top_control_frame, text="Generate New Map",
                   command=self.generate_new_map).pack(side='left', padx=5)

        # Create frame for maps
        self.maps_frame = ttk.Frame(self.root)
        self.maps_frame.pack(pady=10, padx=10)

        # Create canvases for maps
        self.real_canvas = tk.Canvas(self.maps_frame, width=600, height=600)
        self.real_canvas.grid(row=0, column=0, padx=5)

        self.pred_canvas = tk.Canvas(self.maps_frame, width=600, height=600)
        self.pred_canvas.grid(row=0, column=1, padx=5)

        # Create bottom control panel
        self.bottom_control_frame = ttk.Frame(self.root)
        self.bottom_control_frame.pack(pady=10)

        self.need_x = 0
        self.need_y = 0

        # Control buttons
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
        ttk.Button(self.bottom_control_frame, text="Generate road",
                   command=self.take_new_point).pack(side='left', padx=5)

        ttk.Label(self.bottom_control_frame, text="X:").pack(side='left', padx=5)
        self.x_var = tk.StringVar(value="5")
        self.x_spinner = ttk.Spinbox(self.bottom_control_frame, from_=4, to=12,
                                     textvariable=self.x_var, width=5)
        self.x_spinner.pack(side='left', padx=5)

        ttk.Label(self.bottom_control_frame, text="Y:").pack(side='left', padx=5)
        self.y_var = tk.StringVar(value="5")
        self.y_spinner = ttk.Spinbox(self.bottom_control_frame, from_=4, to=12,
                                     textvariable=self.y_var, width=5)
        self.y_spinner.pack(side='left', padx=5)
        self.images = [
            'watr',
            'grnd',
            'gnus',
            'zubp',
            'fost',
            'tank'
        ]

        # Dictionary of colors for different terrain types if you havenot images
        self.colors = {
            'watr': 'blue',
            'grnd': 'brown',
            'gnus': 'gray',
            'zubp': 'yellow',
            'fost': 'green'
        }

        self.draw_maps()

    def take_new_point(self):
        """Get new target coordinates from spinners and generate path"""
        self.need_x = int(self.x_var.get())
        self.need_y = int(self.y_var.get())
        self.generate_road_and_move(self.need_x, self.need_y, self.real_map)

    def generate_new_map(self):
        """Generate new random map with given size"""
        size = int(self.size_var.get())
        self.map_size = size
        self.real_map = generate_map(size)
        # Update robot's prediction map size
        self.robot.update_prediction_size(size)
        # Move robot to center of new map
        self.robot.place(size // 2, size // 2, 'S')
        self.draw_maps()

    def draw_maps(self):
        """Draw both real map and prediction map"""
        # Clear canvases
        self.real_canvas.delete("all")
        self.pred_canvas.delete("all")

        map_size = len(self.real_map)
        cell_size = min(600 // map_size, 80)  # Scale cell size

        for i in range(map_size):
            for j in range(map_size):
                terrain_type = self.real_map[i][j]
                x1 = j * cell_size
                y1 = i * cell_size
                x2 = (j + 1) * cell_size
                y2 = (i + 1) * cell_size

                if terrain_type in self.images:
                    # Scale image to new cell size
                    img = Image.open(f"images/{terrain_type}.png").resize((cell_size, cell_size))
                    photo = ImageTk.PhotoImage(img)
                    # Save image reference
                    setattr(self, f"img_{i}_{j}", photo)
                    self.real_canvas.create_image(
                        x1 + cell_size / 2,
                        y1 + cell_size / 2,
                        image=getattr(self, f"img_{i}_{j}")
                    )
                else:
                    color = self.colors.get(terrain_type, 'white')
                    self.real_canvas.create_rectangle(x1, y1, x2, y2, fill=color)

        # Draw robot
        robot_x = self.robot.robot_coord[1] * cell_size + cell_size / 2
        robot_y = self.robot.robot_coord[0] * cell_size + cell_size / 2
        self.real_canvas.create_oval(robot_x - 10, robot_y - 10, robot_x + 10, robot_y + 10, fill='blue')

        # Draw robot's direction
        end_x = robot_x + self.robot.orientation[1] * 20
        end_y = robot_y + self.robot.orientation[0] * 20
        self.real_canvas.create_line(robot_x, robot_y, end_x, end_y, arrow=tk.LAST, width=3)

        # Draw probability map
        pred_size = map_size - 2
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
        """Move robot forward"""
        self.robot.move(self.real_map)
        self.draw_maps()

    def rotate(self, direction):
        """Rotate robot left or right"""
        self.robot.rotate(direction)
        self.draw_maps()

    def sense(self):
        """Update robot's sensor readings"""
        self.robot.sense_all(self.real_map)
        self.draw_maps()

    def predict(self):
        """Update robot's position prediction"""
        self.robot.sense_all(self.real_map)
        self.robot.predict_place(self.real_map)
        self.draw_maps()

    def run(self):
        """Start the GUI main loop"""
        self.root.mainloop()

    def generate_road_and_move(self, X, Y, real_map):
        """
        Generate best route to point and go alonng it
        Function has delay 2 seconds to understand what the robot is doing

        Args:
            X: Target X coordinate
            Y: Target Y coordinate
            real_map: Current map of environment
        """
        print('FUNCTION START')
        self.predict()
        pred_coord = self.robot.find_position()
        route = self.robot.find_optimal_path(real_map, pred_coord, (Y, X))
        i = 1
        while pred_coord[0] != X or pred_coord[1] != Y:
            # turns to right side
            if pred_coord[0] + self.robot.orientation[0] != route[i][0] or pred_coord[1] + self.robot.orientation[1] != \
                    route[i][1]:
                need_coord = [route[i][0] - pred_coord[0], route[i][1] - pred_coord[1]]
                our_cord_indx = (list(self.robot.orientation_dict.values()).index(self.robot.orientation))
                need_coord_indx = (list(self.robot.orientation_dict.values()).index(need_coord))
                if abs(need_coord_indx - our_cord_indx + 4) % 4 > abs(our_cord_indx - need_coord_indx + 4) % 4:
                    while need_coord != self.robot.orientation:
                        self.rotate('right')
                        self.draw_maps()
                        time.sleep(2)
                else:
                    while need_coord != self.robot.orientation:
                        self.rotate('left')
                        self.draw_maps()
                        time.sleep(2)
            # try go to point
            while pred_coord[0] != route[i][0] or pred_coord[1] != route[i][1]:
                self.robot.move(real_map)
                self.predict()
                self.draw_maps()
                pred_coord = self.robot.find_position()
            # check if we reach right destination
            raz_x, raz_y = pred_coord[0] - route[i][0], pred_coord[1] - route[i][1]
            if raz_x > 1 or raz_y > 1 or raz_x < -1 or raz_y < -1:
                route = self.robot.find_optimal_path(real_map, pred_coord, (Y, X))
            else:
                i += 1
            self.draw_maps()
            time.sleep(2)
        print('FINISH')


def generate_map(size):
    """
    Generate random map with water borders

    Args:
        size: Size of inner map area

    Returns:
        2D list representing the map
    """
    # Create map with water borders
    new_map = [['watr' for _ in range(size + 2)] for _ in range(size + 2)]

    # Fill inner area with random terrain
    terrain_types = ['grnd', 'gnus', 'zubp', 'fost']
    for i in range(1, size + 1):
        for j in range(1, size + 1):
            new_map[i][j] = random.choice(terrain_types)

    return new_map