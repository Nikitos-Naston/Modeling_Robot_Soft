# Приложение для моделирования передвижения робота в двухмерной среде. 
TO DO:
* Добавить расширенные настройки 
* Добавить проверку на дурака
* Добавить визуализацию пути
* Добавить реализма с помощью некоректного поворота

# Описание робота
В нашем случае у нас предствлен робот похожий на танк. 
##### Робот может:
1. Поворачиваться внури своей клетке
2. Совершать движение вперед
   
##### Робот имеет датчики:
1. Сенсор который смотрит территорию под собой более точный.
2. Сенсор который смотрит территорию перед собой менее точный.
3. Супер точный магнитометр благодаря которому мы с точностью можем понимать в каком направлении смотрит наш робот.

# 1. Подробное описание математических моделей

## 1.1 Математическая модель сенсора

### Формальное описание
Сенсор робота $ S $ возвращает два типа измерений:
1. $ T_{under} $ - тип местности под роботом
2. $ T_{around} = [T_N, T_E, T_S, T_W] $ - типы местности в четырех направлениях

### Вероятностная модель измерений
Для местности под роботом:
$ P(T_{measured} = T_{real}) = 0.9 $
$ P(T_{measured} \neq T_{real}) = 0.1 $

Для окружающей местности:
$ P(T_{measured} = T_{real}) = 0.75 $
$ P(T_{measured} \neq T_{real}) = 0.25 $

Реализация в коде:
```python
def sense_all(self, real_map):
    self.under_robot = real_map[self.robot_coord[0]][self.robot_coord[1]]
    self.around_robot = []
    for i in range(4):
        self.around_robot += [
            real_map[self.robot_coord[0] + self.orientation[0]]
                    [self.robot_coord[1] + self.orientation[1]]]
        self.rotate('right')
```

## 1.2 Математическая модель движения

### Параметры модели
1. Вероятности поворота:
   - $ P_{not\_rotate} = 0.1 $ - вероятность не повернуть
   - $ P_{over\_rotate} = 0.2 $ - вероятность избыточного поворота
   - $ P_{rotate} = 0.7 $ - вероятность корректного поворота

2. Вероятности движения:
   - $ P_{not\_move} = 0.2 $ - вероятность остаться на месте
   - $ P_{move} = 0.8 $ - вероятность движения

3. Вероятности застревания в различных типах местности $ P_{stuck}(terrain) $:
```python
{
    'gnus': 0.7,  # Гнусмус
    'zubp': 0.5,  # Песок
    'fost': 0.3,  # Лес
    'grnd': 0.1,  # Земля
    'watr': 1.0   # Вода
}
```

### Формула обновления вероятностей положения
Для каждой клетки $(i,j)$ на карте вероятностей:

$ P_{new}(i,j) = P_{old}(i,j) \cdot (P_{not\_move} + P_{stuck}(terrain) \cdot P_{move}) $
$ P_{new}(i+dx,j+dy) = P_{old}(i,j) \cdot P_{move} \cdot (1 - P_{stuck}(terrain)) $

где $(dx,dy)$ - вектор направления движения.

## 1.3 Модель локализации

### Формула Байеса 
Обновление вероятностей положения робота происходит в два этапа:

1. Предсказание (prediction step):
```python
def move(self, real_map):
    new_robot_prediction_map = [[0 for i in range(self.map_size)] 
                               for j in range(self.map_size)]
    for i in range(self.map_size):
        for j in range(self.map_size):
            start_location = self.robot_prediction_map[i][j]
            # Вычисление новых вероятностей с учетом модели движения
```

2. Коррекция (update step):
```python
def predict_place(self, real_map):
    robot_sr_pred = [[0 for i in range(self.map_size)] 
                     for j in range(self.map_size)]
    # Обновление вероятностей на основе показаний сенсоров
```

### Нормализация
После каждого обновления выполняется нормализация вероятностей:
$ P_{normalized}(i,j) = \frac{P(i,j)}{\sum_{x,y} P(x,y)} $

## 1.4 Модель планирования пути

### Алгоритм поиска оптимального пути
Используется модифицированный алгоритм Дейкстры, где вес ребра определяется вероятностью застревания:

$ weight(edge) = P_{stuck}(terrain_{destination}) $

Целевая функция:
$ Path_{optimal} = \arg\min_{\text{path}} \sum_{(i,j) \in \text{path}} P_{stuck}(terrain_{i,j}) $

```python
def find_optimal_path(self, map, start, end):
    # Создаем карту весов
    ver_map = [[self.robot_p_ried[map[j][i]] 
                for i in range(len(map))] 
                for j in range(len(map))]
    
    # Инициализация массива расстояний
    dp = [[float('inf')] * len(ver_map) 
          for _ in range(len(ver_map))]
    
    # Поиск пути с минимальной суммарной вероятностью застревания
```

# 2. Описание программного обеспечения для моделирования движения робота

### 2.1 Цель проекта
Разработано программное обеспечение для моделирования движения робота в неизвестной местности с использованием вероятностной локализации. Система позволяет симулировать реальные условия передвижения робота с учетом различных типов местности и неопределенностей в движении и измерениях.

### 2.1.1 Ключевые возможности
- Генерация случайных карт местности
- Визуализация реального положения робота и его предполагаемого местоположения
- Автоматическое планирование маршрута
- Интерактивное управление роботом
- Визуализация вероятностей положения робота

## 2.2 Интерфейс пользователя

### 2.2.1 Главное окно приложения
![Главное окно](/images_for_README/main_window.jpg)

Интерфейс разделен на три основные части:
1. **Панель управления (сверху)**
   - Выбор размера карты
   - Кнопка генерации новой карты
   
2. **Область визуализации (центр)**
   - Левая карта: реальная карта местности
   - Правая карта: карта вероятностей положения робота

3. **Панель навигации (снизу)**
   - Кнопки управления движением
   - Ввод целевых координат
   - Кнопки сканирования и прогнозирования

### 2.2.2 Визуализация типов местности
```
Условные обозначения:
🌊 Вода (watr) - синий
🟫 Земля (grnd) - коричневый
🌫️ Гнусмус (gnus) - серый
🟨 Песок (zubp) - желтый
🌲 Лес (fost) - зеленый
🤖 Робот - синий круг со стрелкой направления
```

## 2.3 Технические характеристики

### 2.3.1 Параметры моделирования

**Параметры движения робота:**
Вероятности движения:
- Успешное перемещение: 80%
- Возможность не поехать: 20%

**Вероятности застревания в различных типах местности:**
По умолчанию
- Болото (gnus): 70%
- Песок (zubp): 50%
- Лес (fost): 30%
- Земля (grnd): 10%
- Вода (watr): 100%

### 2.3.2 Точность сенсоров
Математическая модель пердставлена выше
Точность определения местности:
- Под роботом: 90%
- Вокруг робота: 75%

## 2.4 Алгоритмы и процессы 

### Алгоритм локализации и движения

1. **Инициализация**
   - Равномерное распределение вероятностей
   - Нахождения робота в точке 2, 2 _(по умолчанию)_
   ![Равномерное распределение](/images_for_README/first_p.png)

2. **Цикл локализации**
   1. Движение робота вниз _(к примеру)_
   2. Обновление вероятностей по модели движения ![Обновленые данные после движения вниз](/images_for_README/second_p.png)
   3. Получение данных с сенсоров
   4. Коррекция вероятностей по показаниям сенсоров
   5. Нормализация вероятностей ![Итоговая вероятность](/images_for_README/thisrd_p.png)

### Алгоритм нахождения пути

Этапы планирования:
1. Определение текущего положения по карте вероятности _(представлена выше)_
2. Построение карты весов перебором возможных варинатов где ребро это вероятность застрять 
3. Поиск оптимального пути с помощью алгоритма Дейкстры![Итоговая вероятность](https://commons.wikimedia.org/wiki/File:Dijkstra_Animation.gif?uselang=ru)
4. Пошаговое выполнение маршрута с задержкой 2 секунды для анализа выполенения

# 3. Руководство по воспроизведению проекта

## 3.1 Подготовка рабочего окружения

### 3.1.1 Необходимые библиотеки
```python
pip install pillow  # для работы с изображениями
pip install tkinter # для создания GUI (обычно уже установлен с Python)
```

### 3.1.2 Структура проекта
```
Model_Robot_Soft/
│
├── robot_model.py    # Математическая модель робота
├── UI.py            # Графический интерфейс
├── robot_control_ver1.py  # Основной модуль управления
│
├── images/          # Папка с изображениями для визуализации
│   ├── watr.png    # Вода
│   ├── grnd.png    # Земля
│   ├── gnus.png    # Болото
│   ├── zubp.png    # Песок
│   ├── fost.png    # Лес
│   └── tank.png    # Робот
```

## 3.2 Пошаговая реализация

### 3.2.1 Создание математической модели робота (robot_model.py)

#### Шаг 1: Инициализация базового класса
```python
class Robot():
    def __init__(self, map_size, p_over_rotate=0.2, p_not_rotate=0.1, p_not_move=0.2):
        # Параметры движения
        self.p_over_rotate = p_over_rotate  # Вероятность избыточного поворота
        self.p_not_rotate = p_not_rotate    # Вероятность неповорота
        self.p_rotate = 1 - p_over_rotate - p_not_rotate  # Вероятность корректного поворота
        self.p_not_move = p_not_move        # Вероятность неперемещения
        self.p_move = 1 - p_not_move        # Вероятность перемещения

        # Инициализация состояния робота
        self.orientation = [1, 0]  # Начальная ориентация (на юг)
        self.robot_coord = []      # Координаты робота
        
        # Словарь возможных ориентаций
        self.orientation_dict = {
            'N': [-1, 0],  # Север
            'E': [0, 1],   # Восток
            'S': [1, 0],   # Юг
            'W': [0, -1]   # Запад
        }
```

#### Шаг 2: Реализация сенсорной системы
```python
def sense_all(self, real_map):
    # Определение типа местности под роботом
    self.under_robot = real_map[self.robot_coord[0]][self.robot_coord[1]]
    
    # Сканирование окружающей местности
    self.around_robot = []
    for i in range(4):  # Проверяем все 4 направления
        self.around_robot += [
            real_map[self.robot_coord[0] + self.orientation[0]]
                    [self.robot_coord[1] + self.orientation[1]]
        ]
        self.rotate('right')  # Поворачиваем для проверки следующего направления
```

#### Шаг 3: Реализация системы локализации
```python
def predict_place(self, real_map):
    # Создаем карту предсказаний
    robot_sr_pred = [[0 for i in range(self.map_size)] 
                     for j in range(self.map_size)]
    
    # Обновляем вероятности для каждой клетки
    for i in range(self.map_size):
        for j in range(self.map_size):
            # Проверяем соответствие местности под роботом
            result = (self.under_robot == real_map[i + 1][j + 1])
            robot_sr_pred[i][j] += (0.9 * result) + (0.1 * (1 - result))
            
            # Проверяем соответствие окружающей местности
            for k in range(len(self.around_robot)):
                help_orientation_mas = [[-1, 0], [0, 1], [1, 0], [0, -1]]
                result = (self.around_robot[k] == 
                         real_map[i + 1 + help_orientation_mas[k][0]]
                                [j + 1 + help_orientation_mas[k][1]])
                robot_sr_pred[i][j] += ((0.75 * result) + 
                                       (0.25 * (1 - result)))
```

### 3.2.2 Создание графического интерфейса (UI.py)

#### Шаг 1: Основная структура GUI
```python
class RobotGUI:
    def __init__(self, robot, real_map):
        self.robot = robot
        self.real_map = real_map
        
        # Создание главного окна
        self.root = tk.Tk()
        self.root.title("Robot Control")
        
        # Создание фреймов
        self.create_control_panel()
        self.create_map_display()
        self.create_navigation_panel()
```

#### Шаг 2: Визуализация карты
```python
def draw_maps(self):
    # Очистка канвасов
    self.real_canvas.delete("all")
    self.pred_canvas.delete("all")
    
    # Определение размера ячеек
    map_size = len(self.real_map)
    cell_size = min(600 // map_size, 80)
    
    # Отрисовка реальной карты
    for i in range(map_size):
        for j in range(map_size):
            terrain_type = self.real_map[i][j]
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = (j + 1) * cell_size, (i + 1) * cell_size
            
            # Загрузка и отображение текстур
            if terrain_type in self.images:
                img = Image.open(f"images/{terrain_type}.png")
                img = img.resize((cell_size, cell_size))
                photo = ImageTk.PhotoImage(img)
                self.real_canvas.create_image(
                    x1 + cell_size/2, 
                    y1 + cell_size/2, 
                    image=photo
                )
```

### 3.2.3 Важные формулы и их реализация

#### Формула 1: Байесовское обновление вероятностей
\[ P(x_t | z_t) = \eta P(z_t | x_t) \sum_{x_{t-1}} P(x_t | x_{t-1}, u_t) P(x_{t-1}) \]

```python
def update_belief(self, measurement):
    eta = 0  # Нормализующий коэффициент
    
    # Применение формулы Байеса
    for i in range(self.map_size):
        for j in range(self.map_size):
            # P(z_t | x_t) - вероятность измерения
            measurement_prob = self.get_measurement_probability(
                measurement, i, j)
            
            # P(x_t | x_{t-1}, u_t) - модель движения
            motion_prob = self.get_motion_probability(i, j)
            
            # Обновление вероятности
            self.robot_prediction_map[i][j] *= (
                measurement_prob * motion_prob)
            eta += self.robot_prediction_map[i][j]
    
    # Нормализация
    for i in range(self.map_size):
        for j in range(self.map_size):
            self.robot_prediction_map[i][j] /= eta
```

#### Формула 2: Оптимальный путь
\[ Path_{cost} = \min_{\text{path}} \sum_{(i,j) \in \text{path}} -\log(1 - P_{stuck}(terrain_{i,j})) \]

```python
def find_optimal_path(self, start, end):
    # Преобразование вероятностей в веса
    weights = [[float('inf')] * self.map_size 
              for _ in range(self.map_size)]
    
    for i in range(self.map_size):
        for j in range(self.map_size):
            if self.real_map[i][j] != 'watr':
                weights[i][j] = -math.log(
                    1 - self.robot_p_ried[self.real_map[i][j]]
                )
    
    # Поиск пути методом Дейкстры
    return self.dijkstra(weights, start, end)
```




   
