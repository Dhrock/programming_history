from turtle import pos
import pyrealsense2 as rs
import numpy as np
import cv2
import serial
import time


# Create a pipeline
pipeline = rs.pipeline()

# Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: " , depth_scale)

# We will be removing the background of objects more than
#  clipping_distance_in_meters meters away
clipping_distance_MAX_in_meters = 0.43 #1 meter
clipping_distance_MIN_in_meters = 0.37
clipping_distance_MAX = clipping_distance_MAX_in_meters / depth_scale
clipping_distance_MIN = clipping_distance_MIN_in_meters / depth_scale

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)

# 色領域のHSV閾値
# COLOR_BGR2HSV で色空間の変換を行うと，Hは[0,180)になることに注意．
HSV_MIN = np.array([80, 62, 115], dtype=np.uint8)
HSV_MAX = np.array([100, 255, 255], dtype=np.uint8)

# OpenCVのRectに合わせて，(x,y,w,h)の形式とする．
ROI_RECT1 = [[320,110,100,100,'a'],
             [180,250,100,100,'b'],
             [460,250,100,100,'c'],
             [320,390,100,100,'d']]
ROI_COLOR_BGR1 = (0, 200, 0) # ROIの色．緑

pos = []
for arr in ROI_RECT1:
    x, y, w, h, l = arr
    x_s = int(x-(w/2))
    x_f = int(x+(w/2))
    y_s = int(y-(h/2))
    y_f = int(y+(h/2))
    pos.append([x_s, y_s, x_f, y_f])

# シリアル通信のsetting
ser = serial.Serial('COM4', 9600) # デバイス名とボーレートを設定してポートをopen
time.sleep(1)

# Streaming loop
try:
    while True:
    
        # Get frameset of color and depth
        
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # decimarion_filterのパラメータ
        decimate = rs.decimation_filter()
        decimate.set_option(rs.option.filter_magnitude, 1)
        # spatial_filterのパラメータ
        spatial = rs.spatial_filter()
        spatial.set_option(rs.option.filter_magnitude, 1)
        spatial.set_option(rs.option.filter_smooth_alpha, 0.25)
        spatial.set_option(rs.option.filter_smooth_delta, 50)
        # hole_filling_filterのパラメータ
        hole_filling = rs.hole_filling_filter()
        # disparity
        depth_to_disparity = rs.disparity_transform(True)
        disparity_to_depth = rs.disparity_transform(False)
       
        # 画角を合わせたフレームからカラー・デプスフレームを取得
        aligned_frames = align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        
        # Validate that both frames are valid
        if not depth_frame or not color_frame:
            continue

        # filterをかける
        filter_frame = decimate.process(depth_frame)
        filter_frame = depth_to_disparity.process(filter_frame)
        filter_frame = spatial.process(filter_frame)
        filter_frame = disparity_to_depth.process(filter_frame)
        filter_frame = hole_filling.process(filter_frame)
        result_frame = filter_frame.as_depth_frame()

        # RGB画像・デプス画像・HSV画像を取得
        # マスク処理を行う
        RGB_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(result_frame.get_data())
        HSV_image = cv2.cvtColor(RGB_image, cv2.COLOR_BGR2HSV)

         # 深度値の取得

        black_color = 0
        depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
        HSV_bg_removed = np.where((clipping_distance_MIN > depth_image_3d) | (depth_image_3d > clipping_distance_MAX) | (depth_image_3d <= 0), black_color, HSV_image)


        mask = cv2.inRange(HSV_bg_removed, HSV_MIN, HSV_MAX)

        mask_bin = mask // 255
        # mask_binは0か1，maskを255で割る(整数除算)
        
        # mask領域のみを表示する
        mask_image = RGB_image * mask_bin[:,:,np.newaxis]
        # maskの3次元目(1成分)を3成分にbroadcastし(NumPyの機能)
        # それを元画像frame (BGR3成分，8ビット符号なし整数)に
        # 乗じることで，マスクが0の画素を(0,0,0)にしている．

        count = 0 # 画素数の初期化
        pixle = 0

        # 関心領域(Region Of Interest; ROI)の描画
        # 関心領域内の画素数を数える
        for i, arr in enumerate(ROI_RECT1):
            cx,cy,ch,cw = pos[i]
            cv2.rectangle(mask_image, (cx, cy), (ch, cw), ROI_COLOR_BGR1, 2)
            cv2.rectangle(RGB_image, (cx, cy), (ch, cw), ROI_COLOR_BGR1, 2)

        count_a = np.sum(mask_bin[pos[0][1]:pos[0][3],pos[0][0]:pos[0][2]])
        count_b = np.sum(mask_bin[pos[1][1]:pos[1][3],pos[1][0]:pos[1][2]])
        count_c = np.sum(mask_bin[pos[2][1]:pos[2][3],pos[2][0]:pos[2][2]])
        count_d = np.sum(mask_bin[pos[3][1]:pos[3][3],pos[3][0]:pos[3][2]])

        if count_a > 0:
            led_str = ROI_RECT1[0][4]
            pixle = count_a
            value_str = str(pixle)
            
        elif count_b > 0:
            led_str = ROI_RECT1[1][4]
            pixle = count_b
            value_str = str(pixle)

        elif count_c > 0:
            led_str = ROI_RECT1[2][4]
            pixle = count_c
            value_str = str(pixle)

        elif count_d > 0:
            led_str = ROI_RECT1[3][4]
            pixle = count_d
            value_str = str(pixle)

        else:
            led_str = 'x'
            pixle = 0
            value_str = str(pixle)
    
        # 画素数を表示
        cv2.putText(mask_image, f'{pixle}', (16, 32), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow('RGB_image', RGB_image)
        cv2.imshow('depth', HSV_bg_removed)
        cv2.imshow('area', mask_image)
        if cv2.waitKey(1) & 0xff == 27:#ESCで終了
            cv2.destroyAllWindows()
            break

        # 送信する文字列を作成
        send_message = f'{led_str}{value_str}\n'
        print(f'send: {send_message}', end='')

        # 送信する
        ser.write(send_message.encode('utf-8'))

        # 受信して確認
        recv_message = ser.readline().decode('utf-8')
        print(f'recv: {recv_message}', end='')


finally:
    
    led_str = 'x'
    value_str = 0
    send_message = f'{led_str}{value_str}\n'
    print(f'send: {send_message}', end='')
    ser.write(send_message.encode('utf-8'))
    recv_message = ser.readline().decode('utf-8')
    print(f'recv: {recv_message}', end='')

    print("Close Port")
    ser.close()
    
    pipeline.stop()