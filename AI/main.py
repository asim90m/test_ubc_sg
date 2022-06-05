import os
from os import listdir
import shutil
from detector import Detector
import argparse
import ndownloader
import re
from PIL import Image


def hentAI_detection(dcp_dir, in_path, is_mosaic=False, is_video=False, force_jpg=False, dilation=0):
    # TODO: Create new window? Can show loading bar
    # hent_win = new_window()
    # info_label = Label(hent_win, text="Beginning detection")
    # info_label.pack(padx=10,pady=10)
    # hent_win.mainloop()

    dilation = (dilation) * 2  # Dilation performed via kernel, so dimension is doubled

    # Copy input input_images_folder to decensor_input_original. NAMES MUST MATCH for DCP
    print('copying inputs into input_original dcp input_images_folder')
    # always do this, even for bar, so that copying to the decensor_output for pics that have no bars is easier
    for fil in listdir(in_path):
        if fil.endswith('jpg') or fil.endswith('png') or fil.endswith('jpeg') or fil.endswith(
                'JPG') or fil.endswith('PNG') or fil.endswith('JPEG'):
            try:
                path1 = os.path.join(in_path, fil)
                path2 = os.path.join(dcp_dir, "decensor_input_original")
                shutil.copy(path1, path2)  # DCP is compatible with original jpg input.
            except Exception as e:
                print("ERROR in hentAI_detection: Mosaic copy to decensor_input_original failed!", fil, e)
                return

    # Run detection
    output_dir = os.path.join(dcp_dir, "decensor_input", "")
    assert os.path.exists(output_dir)

    print('Running detection, outputting to {}'.format(output_dir))
    detect_instance.run_on_folder(input_folder=in_path, output_folder=output_dir, is_video=False,
                                  is_mosaic=is_mosaic, dilation=dilation)

    # Announce completion, TODO: offer to run DCP from DCP directory
    detect_instance.unload_model()
    print('Process complete!')


# helper function to call TGAN input_images_folder function.
# def hentAI_TGAN(in_path=None, is_video=False, force_jpg=True):
#     print("Starting ESRGAN detection and decensor")
#
#     loader = Tk()
#     loader.title('Running ESRGAN')
#     load_label = Label(loader, text='Now running decensor. This can take a while. Please wait')
#     load_label.pack(side=TOP, fill=X, pady=10, padx=20)
#     loader.update()
#     detect_instance.run_ESRGAN(in_path=in_path, is_video=is_video, force_jpg=force_jpg)
#     loader.destroy()
#
#     print('Process complete!')
#     popup = Tk()
#     popup.title('Success!')
#     label = Label(popup, text='Process executed successfully!')
#     label.pack(side=TOP, fill=X, pady=20, padx=10)
#     num_jpgs = detect_instance.get_non_png()
#
#     okbutton = Button(popup, text='Ok', command=popup.destroy)
#     okbutton.pack()
#     popup.mainloop()


def bar_detect(dcp_dir, in_path):
    hentAI_detection(dcp_dir, in_path, is_mosaic=False, is_video=False, force_jpg=True, dilation=4)


def mosaic_detect(dcp_dir, in_path):
    hentAI_detection(dcp_dir, in_path, is_mosaic=True, is_video=False, dilation=4, force_jpg=True)


def wipedir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)


if __name__ == "__main__":
    """
    5 steps:
    1. Download from host site
    2. If screentone removal is specified, remove screentones
    3. Convert jpgs to pngs
    4. Run AI
    5. Run decensor (other script, Python 3.6 instead of 3.5)
    
    """

    # setup folders and stuff
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # hide 10% of memory allocated warnings
    weights_path = os.path.join(os.getcwd(), 'weights.h5')
    AI_folder = os.path.join(os.getcwd(), "AI", "")
    PY_folder = os.path.join(os.getcwd(), "Py", "")
    input_images_folder = os.path.join(AI_folder, "input_images", "")
    stremove_folder = os.path.join(os.getcwd(), "AI", "input_stremoved", "")
    if not os.path.exists(input_images_folder):
        os.makedirs(input_images_folder)
    dec_input = os.path.join(os.getcwd(), "Py", "decensor_input", "")
    dec_output = os.path.join(os.getcwd(), "Py", "decensor_output", "")
    wipedir(dec_input)
    wipedir(dec_output)

    detect_instance = Detector(weights_path=weights_path)
    current_window = None

    parser = argparse.ArgumentParser()
    parser.add_argument('link')
    parser.add_argument('barormosaic')  # bar or mosaic censorship
    parser.add_argument('stremove')  # remove screen tones or don't
    args = parser.parse_args()

    link, barormosaic, stremove = args.link, args.barormosaic, args.stremove
    if barormosaic.lower() not in ["bar", "mosaic"]:
        raise Exception("Specify BARORMOSAIC as bar or mosaic in the pipeline variables please")
    id = re.search('[0-9]+', link).group(0)
    if len(id) != 6:
        raise Exception("Invalid ID")
    print("Running with args barormosaic:" + barormosaic + " id:" + id + " screentoneremove:" + stremove)

    print("Step 1: Downloading images")
    wipedir(input_images_folder)
    ndownloader.download(input_images_folder, id)

    if stremove.lower() == "true":
        print("Step 2: Removing screentones")
        wipedir(stremove_folder)
        string = "python stremove.py"
        os.system(string)
        infolder = stremove_folder
    else:
        print("Skipping step 2: Removing screentones")
        infolder = input_images_folder

    print("Step 3: Converting to png")

    # convert jpgs to png
    for filename in os.listdir(infolder):
        if "jpg" in filename:
            im1 = Image.open(infolder + filename)
            im1.save(input_images_folder + filename.strip('jpg') + "png")
    # delete jpgs
    for filename in os.listdir(input_images_folder):
        if "jpg" in filename:
            os.remove(input_images_folder + filename)

    print("Step 4: Running AI")
    if barormosaic.lower() == 'bar':
        bar_detect(PY_folder, input_images_folder)
    elif barormosaic.lower() == 'mosaic':
        mosaic_detect(PY_folder, input_images_folder)

    print("Finished Part 1!")
