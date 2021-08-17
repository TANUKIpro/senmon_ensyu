import socket
import numpy as np
import cv2
import time
import configparser

#config = configparser.ConfigParser()
config = configparser.SafeConfigParser()
config.read('C:/Users/ryota/Desktop/connection.ini', 'UTF-8')

FPS = 60
INDENT = '    '

CAMERA_ID = 2
CAMERA_FPS = 60
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

# サーバ設定
SERVER_IP = '127.0.0.1'
SERVER_PORT = int(config.get('server', 'port'))

# パケット設定
HEADER_SIZE = int(config.get('packet', 'header_size'))

# 画像設定
IMAGE_WIDTH = int(config.get('packet', 'image_width'))
IMAGE_HEIGHT = int(config.get('packet', 'image_height'))
#IMAGE_QUALITY = 30
IMAGE_QUALITY = 50

# カメラ設定適用
cam = cv2.VideoCapture(CAMERA_ID)
cam.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

# カメラ情報
print('Camera {')
print(INDENT + 'ID    : {},'.format(CAMERA_ID))
print(INDENT + 'FPS   : {},'.format(cam.get(cv2.CAP_PROP_FPS)))
print(INDENT + 'WIDTH : {},'.format(cam.get(cv2.CAP_PROP_FRAME_WIDTH)))
print(INDENT + 'HEIGHT: {}'.format(cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
print('}')

# クライアントに接続
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.bind((SERVER_IP, SERVER_PORT))
skt.listen(1)
soc, addr = skt.accept()

# サーバ情報
print('Server {')
print(INDENT + 'IP   : {},'.format(SERVER_IP))
print(INDENT + 'PORT : {}'.format(SERVER_PORT))
print('}')

# クライアント情報
print('Client {')
print(INDENT + 'IP   : {},'.format(addr[0]))
print(INDENT + 'PORT : {}'.format(addr[1]))
print('}')

while True:
    loop_start_time = time.time()

    # 画像データ作成
    flag, img = cam.read()
    #resized_img = cv2.resize(img, (IMAGE_WIDTH, IMAGE_HEIGHT))
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), IMAGE_QUALITY]
    (status, encoded_img) = cv2.imencode('.jpg', img, encode_param)

    # パケット構築
    packet_body = encoded_img.tostring()
    packet_header = len(packet_body).to_bytes(HEADER_SIZE, 'big') 
    packet = packet_header + packet_body

    # パケット送信
    try:
        soc.sendall(packet)
    except socket.error as e:
        print('Connection closed.')
        break

    # FPS制御
    time.sleep(max(0, 1 / FPS - (time.time() - loop_start_time)))

skt.close()