from snake import *
import socket
import time
import threading
import qrcode
from ledwand import Wallcomm
from PIL import ImageEnhance

URL = "http://pixel-games.art/"
WALLS = (10, )
BRIGHTNESS = 0.2

if __name__ == '__main__':
    queue = []

    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 1234))
    s.listen(10)

    running = True

    def notify_queue():
        for c in queue:
            c.send('You are on queue. Place: {}\n'.format(queue.index(client)+1).encode())

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
                wall = Wallcomm(offsets=WALLS)
                wall.sendFrame(ImageEnhance.Brightness(img).enhance(BRIGHTNESS))
                time.sleep(3)
            else:
                try:
                    playing_client = queue.pop(0)
                    notify_queue()
                    playing_client.send("It's your turn. GO!\n".encode())

                    game = Snake(wall_offsets=WALLS, brightness=BRIGHTNESS)
                    try:
                        def control():
                            while game.is_running():
                                key = playing_client.recv(1)
                                if key == b'a':
                                    game.set_direction(DIRECTION_LEFT)
                                elif key == b'd':
                                    game.set_direction(DIRECTION_RIGHT)
                                elif key == b'w':
                                    game.set_direction(DIRECTION_UP)
                                elif key == b's':
                                    game.set_direction(DIRECTION_DOWN)

                        threading.Thread(target=control).start()
                        game.run()
                        game.stop()
                    except GameOverException:
                        game.stop()
                    playing_client.send("\nGame Over! Score: {}".format(game.get_score()).encode())
                    playing_client.close()
                except BrokenPipeError:
                    pass

    threading.Thread(target=game_handling).start()

    try:
        while True:
            client, address = s.accept()
            queue.append(client)
            client.send('You are on queue. Place: {}\n'.format(queue.index(client)+1).encode())
    except KeyboardInterrupt:
        running = False
