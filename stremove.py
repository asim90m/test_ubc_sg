# Feb 2020 - Nathan Cueto
# Attempt to remove screentones from input images (png) using blurring and sharpening
#
# import sys
# sys.path.append('/usr/local/lib/python2.7/site-packages')
# import cv2
from cv2 import GaussianBlur, bilateralFilter, filter2D, imread, imwrite
import numpy as np
from tkinter import *

# from tkinter import ttk
# from matplotlib import pyplot as plt
from tkinter import filedialog
from os import listdir

versionNumber = "1.6"


# Gaussian blue with variable kernel size, aka more or less blurring
def blur(img, blur_amount=5):
    # TODO experiment with upscaling
    # TODO customizable variables for sigmas
    if blur_amount == 7:
        dst2 = GaussianBlur(img, (7, 7), 0)
        dst = bilateralFilter(dst2, 7, 80, 80)
    else:
        dst2 = GaussianBlur(img, (5, 5), 0)
        dst = bilateralFilter(dst2, 7, 10 * blur_amount, 80)
    # plt.subplot(131)
    # plt.imshow(dst2)
    # plt.title('gauss')
    # plt.xticks([]), plt.yticks([])
    # plt.subplot(132)
    # plt.imshow(dst)
    # plt.title('abf')
    # plt.xticks([]), plt.yticks([])
    # plt.subplot(133)
    # plt.imshow(dst3)
    # plt.title('blur')
    # plt.xticks([]), plt.yticks([])
    # plt.show()
    return dst


# Laplacian filter for sharpening. Only want to do runs of 3x3 kernels to avoid oversharpening.
def sharp(img, sharp_point, sharp_low):
    # TODO customizable sliders for kernel parameters
    # TODO try darkening image
    s_kernel = np.array(
        [[0, sharp_low, 0], [sharp_low, sharp_point, sharp_low], [0, sharp_low, 0]]
    )

    sharpened = filter2D(img, -1, s_kernel)
    return sharpened


# 1 - no png files found
# 2 - no input dec_input
# 3 - no output dec_input
# 4 - write error
def error(errcode):
    # popup success message
    switcher = {
        1: "Error: No .png files found",
        2: "Error: No input directory",
        3: "Error: No output directory",
        4: "Error: File write error",
    }
    raise Exception(switcher[errcode])


# function scans directory and returns generator
def getfileList(dir):
    return (
        i
        for i in listdir(dir)
        if i.endswith(".png")
        or i.endswith(".PNG")
        or i.endswith(".jpg")
        or i.endswith(".JPG")
        or i.endswith(".jpeg")
    )


# function will call the blur and sharpen on every file in directory, and write output file
def removeScreentones(dir_i, dir_o, blur_amount, sh_point=5.56, sh_low=-1.14):
    if dir_i == [] or len(dir_i) == 0:
        return error(2)
    if dir_o == [] or len(dir_o) == 0:
        return error(3)
    inputs = list(getfileList(dir_i))
    if len(inputs) == 0:
        return error(1)

    # calculate sh params, warning if they are unproportionate
    sh_point = float(sh_point)
    sh_low = float(sh_low)
    # print(sh_point, sh_low)

    bs_amount = 0
    if blur_amount == 1:
        bs_amount = 3
    if blur_amount == 2:
        bs_amount = 5
    if blur_amount == 3:
        bs_amount = 7
    for i in inputs:
        # print(dir_i+'/'+i)
        img = imread(os.path.join(dir_i, i))
        blurred = blur(img, bs_amount)
        ret = sharp(blurred, sh_point, sh_low)
        write_dir = os.path.join(os.getcwd(), dir_o, i)
        sucess = imwrite(write_dir, ret)
        if sucess != True:
            return error(4)


if __name__ == "__main__":
    import os

    input_dir = os.path.join(os.getcwd(), "AI", "input_images", "")
    output_dir = os.path.join(os.getcwd(), "AI", "input_stremoved", "")
    removeScreentones(input_dir, output_dir, 2)

    pass
