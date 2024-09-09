import cv2
import os

def boneOutput(dir_name):
    per = 1
    print("### execute ... " + dir_name)

    in_dir_path = "images/item_box/" + dir_name
    out_dir_path = "result/pose_" + dir_name
    file_list_in = os.listdir(in_dir_path)
    file_list_out = os.listdir(out_dir_path)
    file_list_in.sort()
    file_list_out.sort()
    
    range = len(file_list_in)

    threshold = 4

    # 出力先フォルダ名
    rst_f_name = "/bone_" + dir_name

    for (file_name_in, file_name_out) in zip(file_list_in,file_list_out):
        root, ext = os.path.splitext(file_name_in)
        if ext == u'.png' or u'.jpeg' or u'.jpg':
        
            image_path1 = 'images/item_box/' + dir_name + "/" + file_name_in 
            image_path2 = 'result/pose_' + dir_name + "/" + file_name_out
            image_path_out = 'bone_images' + rst_f_name + "/bone_" + file_name_in
            print(file_name_in,file_name_out)

            im = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
            im2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

            mask = cv2.absdiff(im2, im)

            ret, bin = cv2.threshold(mask, threshold,255,cv2.THRESH_BINARY)
            height = bin.shape[0]
            width = bin.shape[1]

            dst = cv2.resize(bin, (int(width*0.65), int(height*0.65)))

            cv2.imwrite(image_path_out, dst)

            print('%d / %d' % (per,range))
            per += 1


if __name__ == "__main__":

    path = "images/item_box/"
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]

    # result内に出力結果のフォルダを作成
    for dir_name in files_dir:
        new_dir_path = 'bone_images/bone_' + dir_name
        os.makedirs(new_dir_path, exist_ok=True)

    # 指定したフォルダのみ実行する場合
    # dir_name = "stop_kawai"
    # 全部一気にやる場合
    for dir_name in files_dir:
        boneOutput(dir_name)

