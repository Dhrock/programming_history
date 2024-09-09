# -*- coding: utf-8 -*-
import os
from posixpath import dirname
import cv2
import copy
from src import util
from src.body import Body


def openPose(dir_name):
    per = 1
    print("### execute ... " + dir_name)

    data_dir_path = "images/item_box/" + dir_name
    file_list = os.listdir(data_dir_path)
    range = len(file_list)

    # 出力先フォルダ名
    rst_f_name = "/pose_" + dir_name

    for file_name in file_list:
        root, ext = os.path.splitext(file_name)
        if ext == u'.png' or u'.jpeg' or u'.jpg':
            # INPUT_FILE_NAME = file_name
            body_estimation = Body('model/body_pose_model.pth')
            target_image_path = 'images/item_box/' + dir_name + "/" + file_name
            oriImg = cv2.imread(target_image_path)  # B,G,R order
            if oriImg is None:
                print("Can't read :" + target_image_path)

            candidate, subset = body_estimation(oriImg)
            canvas = copy.deepcopy(oriImg)
            canvas = util.draw_bodypose(canvas, candidate, subset)

            basename_name = os.path.splitext(
                os.path.basename(target_image_path))[0]

            result_image_path = "result" + rst_f_name + "/pose_" + basename_name + ".jpg"
            cv2.imwrite(result_image_path, canvas)
            
            print('%d / %d' % (per,range))
            per += 1

if __name__ == "__main__":
    path = "images/item_box"
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]

    # result内に出力結果のフォルダを作成
    for dir_name in files_dir:
        new_dir_path = 'result/pose_' + dir_name
        os.makedirs(new_dir_path, exist_ok=True)

    # 指定したフォルダのみ実行する場合
    # dir_name = "stop_kawai"
    # 全部一気にやる場合
    for dir_name in files_dir:
        openPose(dir_name)
