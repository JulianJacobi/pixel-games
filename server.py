from games.snake import Snake
import socket
import time
import threading
import qrcode
from ledwand import Wallcomm
from constants import *
from PIL import Image
from exceptions import *

URL = "http://pixel-games.art/"
WALLS = (10, )
BRIGHTNESS = 0.2

GAMES = (
    ('Snake', Snake),
)


class Client:

    def __init__(self, sock, game):
        self.socket = sock
        self.game = game


if __name__ == '__main__':
    queue = []

    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 1234))
    s.listen(10)

    walls = Wallcomm(offsets=WALLS, brightness=BRIGHTNESS)

    running = True

    def notify_queue():
        for c in queue:
            c.socket.send('You are on queue. Place: {}\n'.format(queue.index(c)+1).encode())

    def game_handling():
        while running:
            if len(queue) == 0:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=1,
                    border=4,
                )
                qr.add_data(URL)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color='black', back_color='white').convert('RGB').crop((0, 0, 32, 32))
                img = Image.new('RGB', (len(WALLS)*32, 32), color='black')
                img.paste(qr_img, (0, 0, 32, 32))
                walls.sendFrame(img)
                time.sleep(3)
            else:
                try:
                    playing_client = queue.pop(0)
                    notify_queue()
                    playing_client.socket.send("It's your turn. GO!\n".encode())

                    game = playing_client.game(width=len(WALLS)*32, height=32)
                    try:
                        def control():
                            while game.is_running():
                                try:
                                    key = playing_client.socket.recv(1)
                                    if key == b'a':
                                        game.keypress(KEY_LEFT)
                                    elif key == b'd':
                                        game.keypress(KEY_RIGHT)
                                    elif key == b'w':
                                        game.keypress(KEY_UP)
                                    elif key == b's':
                                        game.keypress(KEY_DOWN)
                                except OSError:
                                    break

                        def frame_sending():
                            while game.is_running():
                                frame = game.get_frame()
                                walls.sendFrame(frame)
                                time.sleep(0.02)

                        threading.Thread(target=control).start()
                        threading.Thread(target=frame_sending).start()
                        game.run()
                        game.stop()
                    except GameOverException:
                        game.stop()
                    playing_client.socket.send("\nGame Over! Score: {}".format(game.get_score()).encode())
                    playing_client.socket.close()
                except BrokenPipeError:
                    pass

    threading.Thread(target=game_handling).start()

    def client_handling(client_socket):
        client_socket.send(b'Which game do you want to play?\n')
        for i, game in enumerate(GAMES):
            client_socket.send('{:>2d} : {}\n'.format(i, game[0]).encode())
        client_socket.send(b'\nPlease enter number and press [ENTER]: ')
        while True:
            choice = b""
            while True:
                char = client_socket.recv(1)
                if char not in (b'\r', b'\n'):
                    choice += char
                else:
                    break
            choice = int(choice)
            if choice < len(GAMES):
                client = Client(sock=client_socket, game=GAMES[choice][1])
                queue.append(client)
                client_socket.send('You are on queue. Place: {}\n'.format(queue.index(client) + 1).encode())
                break
            else:
                client_socket.send(b'Please choose a valid option: ')

    try:
        while True:
            client, address = s.accept()
            threading.Thread(target=client_handling, args=(client,)).start()
    except:
        running = False
