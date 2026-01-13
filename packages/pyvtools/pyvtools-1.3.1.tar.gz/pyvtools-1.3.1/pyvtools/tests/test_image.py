import os
import cv2
import matplotlib.pyplot as plt
import pyvtools.image as vim

#### UTILITIES

def load_test_image(file_type=".jpg"):
    if os.path.isdir("pyvtools"):
        return vim.load_rgb_image("pyvtools/tests/SampleImage"+file_type)
    else:
        if os.path.isdir("tests"):
            return vim.load_rgb_image("tests/SampleImage"+file_type)
        else:
            return vim.load_rgb_image("SampleImage"+file_type)

#### TESTS

def test_load_image():
    img = load_test_image()
    assert img.shape == (128, 128, 3), "Image shape is not as expected"
    # This ensures PIL and Numpy compatibility

def test_load_tiff_image():
    img = load_test_image(".tiff")
    assert img.shape == (434, 650, 4), "Image shape is not as expected"
    # This ensures PIL and Numpy compatibility

def test_resize_image():
    img = load_test_image()
    img_small = cv2.resize(img, (img.shape[1]//2, img.shape[0]//2))
    assert img_small.shape == (64, 64, 3), "Resized shape is not as expected"
    # This ensures compatibility with OpenCV

def test_SSIM_image():
    img = load_test_image()
    assert float(vim.SSIM(img, img, win_size=None, channel_axis=2)) == 1, "SSIM is not as expected"
    # This ensures compatibility with Scikit-Image

def test_plotting_image():
    img = load_test_image()
    vim.plot_image(vim.normalize_image(img,8))
    plt.savefig("TestSampleImage.png")
    assert os.path.isfile("TestSampleImage.png"), "Matplotlib did not save the figure"
    os.remove("TestSampleImage.png")
    # This ensures compatibility with Matplotlib

if __name__ == "__main__":
    test_load_image()
    test_load_tiff_image()
    test_resize_image()
    test_SSIM_image()
    test_plotting_image()
    print("Everything passed")