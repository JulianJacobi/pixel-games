from PIL import Image
import time


class Game:
    """
    Prototype game class
    """

    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._running = True

    def is_running(self):
        """
        Check if current game is running
        :return: boolean
        """
        return self._running

    def stop(self):
        """
        Gracefully stops the game
        :return:
        """
        self._running = False

    def get_score(self):
        """
        Return current game score
        :return: integer
        """
        return 0

    def keypress(self, key):
        """
        Handles keypress input
        :param key: is one of KEY_* constants
        :return:
        """
        pass

    def get_frame(self):
        """
        returns actual frame for displaying
        :return:
        """
        return Image.new('RGB', (32, 32), color='black')

    def run(self):
        """
        Run game.
        This funktion blocks until the game is running and gracefully stops the game or raises GameOverException
        :return:
        """
        while self._running:
            time.sleep(1)
