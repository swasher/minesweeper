import cv2 as cv
from test.imagesearch import imagesearch
import mss
import mss.tools
import numpy
import sys


def tst_imagesearch():  # worked
    print("OpenCV Version: {}".format(cv.__version__))
    pos = imagesearch("./pic/github.png")
    if pos[0] != -1:
        print("position : ", pos[0], pos[1])
    else:
        print("image not found")


def save_entire_monitor():
    with mss.mss() as sct:
        filename = sct.shot(output="mon-{mon}.png")
        print(filename)


def save_region():
    with mss.mss() as sct:
        # The screen part to capture
        monitor = {"top": 160, "left": 160, "width": 160, "height": 135}
        output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor)

        # Grab the data
        sct_img = sct.grab(monitor)

        # Save to the picture file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        print(output)


def try_opencv():
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": 1920, "height": 1080}

        # Get raw pixels from the screen, save it to a Numpy array
        img = numpy.array(sct.grab(monitor))

        # Display the picture
        cv.imshow("OpenCV/Numpy normal", img)


def capt():
    import time
    with mss.mss() as sct:
        # Part of the screen to capture
        monitor = {"top": 40, "left": 0, "width": 800, "height": 640}

        while "Screen capturing":
            last_time = time.time()

            # Get raw pixels from the screen, save it to a Numpy array
            img = numpy.array(sct.grab(monitor))

            # Display the picture
            cv.imshow("OpenCV/Numpy normal", img)

            # Display the picture in grayscale
            # cv2.imshow('OpenCV/Numpy grayscale',
            #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))

            # print("fps: {}".format(1 / (time.time() - last_time)))

            # Press "q" to quit
            if cv.waitKey(25) & 0xFF == ord("q"):
                cv.destroyAllWindows()
                break


def show_pic():
    img = cv.imread(cv.samples.findFile("./pic/smile_ok.png"))
    if img is None:
        sys.exit("Could not read the image.")
    cv.imshow("Display window", img)
    k = cv.waitKey(0)
    if k == ord("s"):
        cv.imwrite("starry_night.png", img)


if __name__ == '__main__':
    show_pic()
