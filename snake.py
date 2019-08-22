import time
from ledwand import Wallcomm
from PIL import Image
import threading


DIRECTION_UP = 1
DIRECTION_DOWN = -1
DIRECTION_LEFT = 2
DIRECTION_RIGHT = -2


class GameOverException(Exception):
    pass


class Snake:

    def __init__(self, wall_offsets=(10,), brightness=1):
        self.__width = len(wall_offsets)*32
        self.__height = 32
        self.__snake = [(int(self.__width/2), int(self.__height/2))]
        self.__direction = DIRECTION_UP
        # keyboard.add_hotkey('w', self.set_direction, args=(DIRECTION_UP, ))
        # keyboard.add_hotkey('s', self.set_direction, args=(DIRECTION_DOWN, ))
        # keyboard.add_hotkey('a', self.set_direction, args=(DIRECTION_LEFT, ))
        # keyboard.add_hotkey('d', self.set_direction, args=(DIRECTION_RIGHT, ))
        # keyboard.add_hotkey('shift+W', self.set_direction, args=(DIRECTION_UP, ))
        # keyboard.add_hotkey('shift+S', self.set_direction, args=(DIRECTION_DOWN, ))
        # keyboard.add_hotkey('shift+A', self.set_direction, args=(DIRECTION_LEFT, ))
        # keyboard.add_hotkey('shift+D', self.set_direction, args=(DIRECTION_RIGHT, ))

        self.__food = self.generate_food()

        self.__wall = Wallcomm(offsets=wall_offsets)

        self.__running = True

        self.__direction_changed = False

        self.__speed = 4
        self.__speedup_rate = 1.1

        self.__brightness = brightness

        self.__score = 0

        self.__last_interaction = 0
        self.__steps = 0
        self.__snake_color = (int(255*self.__brightness),
                              int(255* self.__brightness),
                              int(255*self.__brightness))

    def is_running(self):
        return self.__running

    def get_score(self):
        return self.__score

    def send_frames_forever(self):
        while self.__running:
            self.send_frame()
            time.sleep(0.02)

    def send_frame(self):
        frame = Image.new('RGB', (self.__width, self.__height), color='black')
        pixels = frame.load()

        for element in self.__snake:
            pixels[element[0], element[1]] = self.__snake_color

        pixels[self.__food[0], self.__food[1]] = (int(255*self.__brightness), 0, 0)

        color = (int(127 * self.__brightness), 0, int(127 * self.__brightness))
        for i in range(self.__width):
            pixels[i, 0] = color
            pixels[i, self.__height-1] = color
        for i in range(self.__height):
            pixels[0, i] = color
            pixels[self.__width-1, i] = color

        self.__wall.sendFrame(frame)

    def set_direction(self, direction):
        if not abs(self.__direction + direction) == 0 \
                and self.__direction != direction \
                and not self.__direction_changed:
            self.__direction = direction
            self.__direction_changed = True
            self.__last_interaction = self.__steps
            self.__snake_color = (int(255*self.__brightness),
                                  int(255*self.__brightness),
                                  int(255*self.__brightness))

    def generate_food(self):
        while True:
            food = (randint(0, self.__width-3)+1, randint(0, self.__height-3)+1)
            if food not in self.__snake:
                return food

    def step(self):
        if self.__width + self.__height - (self.__steps - self.__last_interaction) < 20:
            rest = self.__width + self.__height - (self.__steps - self.__last_interaction)
            factor = (100/20)*rest
            self.__snake_color = (int(255*self.__brightness),
                                  int(factor*self.__brightness),
                                  int(factor*self.__brightness))
        if self.__steps - self.__last_interaction > self.__width + self.__height:
            self.stop()
        next_point = (1, 1)
        current_x = self.__snake[-1][0]
        current_y = self.__snake[-1][1]
        left_x = current_x-1
        if left_x < 1:
            left_x = self.__width-2
        right_x = current_x+1
        if right_x > self.__width-2:
            right_x = 1
        top_y = current_y-1
        if top_y < 1:
            top_y = self.__height-2
        down_y = current_y+1
        if down_y > self.__height-2:
            down_y = 1
        if self.__direction == DIRECTION_UP:
            next_point = (current_x, top_y)
        elif self.__direction == DIRECTION_DOWN:
            next_point = (current_x, down_y)
        elif self.__direction == DIRECTION_LEFT:
            next_point = (left_x, current_y)
        elif self.__direction == DIRECTION_RIGHT:
            next_point = (right_x, current_y)

        if next_point in self.__snake:
            self.__running = False

        self.__snake.append(next_point)
        self.__steps += 1

        if next_point == self.__food:
            # self.__speed = self.__speed * (1 + exp(-self.__speed))
            self.__score += 1
            self.__speed = self.__speed + self.__speedup_rate
            self.__food = self.generate_food()
        else:
            self.__snake.pop(0)

        self.__direction_changed = False

    def run(self):
        threading.Thread(target=self.send_frames_forever).start()

        while self.__running:
            self.step()
            time.sleep(1.0/self.__speed)

        raise GameOverException

    def stop(self):
        self.__running = False


if __name__ == '__main__':
    s = Snake()

    try:
        s.run()
    except KeyboardInterrupt:
        s.stop()