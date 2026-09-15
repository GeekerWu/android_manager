import cv2

# 遇到imshow报错的话，需要重装说一下opencv，可能会好
# pip uninstall opencv-python opencv-contrib-python -y
# pip install --force-reinstall opencv-python
# 之后用下面的脚本测试一下

# image_path = "C:/***/***/Desktop/image.jpg"  #图片路径
img = cv2.imread('test_img/test.jpg')
cv2.imshow('img_window',img)  #显示图片,[图片窗口名字，图片]
cv2.waitKey(0)  # 无限期显示窗口
