import os
import numpy as np
# import rawpy
import cv2
import tifffile as tiff
from PIL import Image
from math import log10, sqrt
from skimage.transform import hough_line#, hough_line_peaks
from skimage.metrics import structural_similarity
import matplotlib.pyplot as plt
import matplotlib.patches as patches

#%% GLOBAL VARIABLES

IMAGE_RGB_FILE_TYPES = [".png", ".jpeg", ".jpg"]
IMAGE_RAW_FILE_TYPES = [".tif", ".tiff", ".npy"] # "dng"
IMAGE_FILE_TYPES = [*IMAGE_RAW_FILE_TYPES, *IMAGE_RGB_FILE_TYPES]

#%% LOADING AND SAVING

def load_rgb_image(filepath, dtype=np.float32):
    """Loads an RGB image as a Numpy aray

    Parameters
    ----------
    filepath : str
        Filepath to image
    dtype : Numpy datatype, optional
        Desired output data type. Default is `np.float32`.
    
    Returns
    -------
    Image as a Numpy array (RGB, not BGR)

    See also
    --------
    PIL.Image.load
    """
    
    return np.array(Image.open(filepath)).astype(dtype)

def load_tiff_image(filepath, dtype=np.float32):
    """Loads a TIFF image as a Numpy aray

    Parameters
    ----------
    filepath : str
        Filepath to image
    dtype : Numpy datatype, optional
        Desired output data type. Default is `np.float32`.
    
    Returns
    -------
    Image as a Numpy array (probably RGGB)

    See also
    --------
    tifffile.imread
    """

    return np.array(tiff.imread(filepath)).astype(dtype)

def load_npy_image(filepath, dtype=np.float32):
    """Loads an image saved as .npy into a Numpy aray

    Parameters
    ----------
    filepath : str
        Filepath to image, must have ".npy" extension
    dtype : Numpy datatype, optional
        Desired output data type. Default is `np.float32`.
    
    Returns
    -------
    Image as a Numpy array (probably RGGB)

    See also
    --------
    np.load
    """
    
    return np.load(filepath).astype(dtype)

def load_image(filepath, dtype=np.float32):
    """Loads an image as a Numpy aray

    Currently supported formats: jpg, png, tiff, npy

    Parameters
    ----------
    filepath : str
        Filepath to image
    dtype : Numpy datatype, optional
        Desired output data type. Default is `np.float32`.
    
    Returns
    -------
    Image as a Numpy array (RGB, not BGR; probably RGGB if raw)
    """

    file_type = os.path.splitext(filepath)[1].lower()
    assert file_type in IMAGE_FILE_TYPES, "Image extension is not supported"

    if file_type in IMAGE_RGB_FILE_TYPES:
        return load_rgb_image(filepath, dtype)
    elif file_type == "npy":
        return load_npy_image(filepath, dtype)
    # if file_type == "dng":
    #     return np.array(rawpy.imread(filepath).raw_image_visible).astype(dtype)
    elif file_type == "tiff" or file_type == "tif":
        return load_tiff_image(filepath, dtype)
    else:
        raise ValueError("Image extension is not supported")

def save_figure(name, sub_name=None, path=os.getcwd(), divider="_", filetype=".png"):

    if not os.path.isdir(path): os.makedirs(path)
    filepath = os.path.join(path, name+divider+sub_name+filetype)
    plt.savefig(filepath, bbox_inches="tight", pad_inches=0.1)

#%% MULTICHANNEL

def demosaic(raw_image):
    """Simple demosaicing to visualize RAW images

    Based on AIM22 Reverse ISP challenge's starter code.

    Parameters
    ----------
    raw_image : np.array
        Raw RGGB image with shape (H, W, 4)
    
    Returns
    -------
    image : np.array
        Demosaiced RGB image with shape (H*2, W*2, 3)
    """
    
    image = rggb2rgb(raw_image) # Shape (H, W, 3)
    
    shape = raw_image.shape
    image = cv2.resize(image, (shape[1]*2, shape[0]*2))

    return image


def rggb2rgb(raw_image):
    """Simple RAW to RGB conversion, with no upsampling

    Could also convert BGGR to BGR

    Parameters
    ----------
    raw_image : np.array
        Raw RGGB image with shape (H, W, 4)
    
    Returns
    -------
    image : np.array
        RGB image with shape (H, W, 3)
    """
    
    assert raw_image.shape[-1] == 4
    
    red        = raw_image[:,:,0]
    green_red  = raw_image[:,:,1]
    green_blue = raw_image[:,:,2]
    blue       = raw_image[:,:,3]
    avg_green  = (green_red + green_blue) / 2

    image = np.stack((red, avg_green, blue), axis=-1)

    return image

def rgb2gray(rgb_image):
    """Converts an RGB image into a grayscale image

    Grayscale image intensity is the luminance: 0.3R + 0.6G + 0.1B

    Parameters
    ----------
    rgb_image : np.array
        RGB image array with shape (H,W,3)
    
    Returns
    -------
    gray_image : np.array
        Grayscale image array with shape (H,W)
    """

    return cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)

def list_images(path, filetypes=IMAGE_FILE_TYPES):
    """List images in the selected directory"""

    return [fname for fname in os.listdir(path)
            if os.path.splitext(fname)[1].lower() in filetypes]

def list_rgb_images(path):
    """List RGB images in the selected directory"""
    return list_images(path, IMAGE_RGB_FILE_TYPES)

def list_raw_images(path):
    """List raw images in the selected directory"""
    return list_images(path, IMAGE_RAW_FILE_TYPES)

#%% IMAGE PROCESSING

def normalize_image(image, bitdepth):
    return image / (2**bitdepth-1)

def invert_normalize_image(image, bitdepth):
    return image * (2**bitdepth-1)

def quantise_image(image, bitdepth, dtype=np.float32):
    return np.clip(image.round(), 0, 2**bitdepth-1).astype(dtype)

#%% IMAGE ANALYSIS

def fourier_transform(image):
    """Calculates the discrete fourier transform of a grayscale image.

    Based on https://www.geeksforgeeks.org/how-to-find-the-fourier-transform-of-an-image-using-opencv-python/

    Parameters
    ----------
    image : np.array
        Grayscale image shaped (H,W)
    
    Returns
    -------
    magnitude : np.array
        DFT of the image, centered on the zero-frequency component
    
    See also
    --------
    cv2.dft
    """

    # Compute the discrete Fourier Transform of the image
    fourier = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    
    # Shift the zero-frequency component to the center of the spectrum
    fourier_shift = np.fft.fftshift(fourier)
    
    # Calculate the magnitude of the Fourier Transform
    magnitude = 20*np.log(cv2.magnitude(fourier_shift[:,:,0],fourier_shift[:,:,1])) # dB
    
    # Scale the magnitude for display
    # magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8UC1)
    
    return magnitude

def hough_transform(image, n_angles=180):
    """Calculates the Hough transform of a grayscale image.

    Based on https://scikit-image.org/docs/stable/auto_examples/edges/plot_line_hough_transform.html

    Parameters
    ----------
    image : np.array
        Grayscale image shaped (H,W)
    n_angles : int, optional


    Returns
    -------
    radius : np.array
        Hough transform radial distance coordinate, expressed in pixels
    theta : np.array
        Hough transform angular coordinate, expressed in radians, from -pi/2 to pi/2
    hough : np.array
        Hough transform, shaped (2*sqrt(2)*max(H,W), n_angles)
    
    See also
    --------
    skimage.transform.hough_line
    """

    tested_angles = np.linspace(-np.pi / 2, np.pi / 2, n_angles, endpoint=False)
    hough, theta, radius = hough_line(image, theta=tested_angles)

    return radius, theta, hough

#%% IMAGE METRICS

def MSE(image_1, image_2):    
    """Mean-Square Error (MSE) to compare two images"""

    image_1, image_2 = np.asarray(image_1), np.asarray(image_2)
    image_1 = image_1.astype(np.float32)
    image_2 = image_2.astype(np.float32)
    mse = np.mean( ( image_1 - image_2 )**2 )

    return mse

def PSNR(image_1, image_2, byte_depth=8):    
   """Peak Signal-to-Noise Ratio (PSNR) to compare two images.
   
   Parameters
   ----------
   image_1, image_2 : np.array
       The two pictures to compare. Must have the same shape.
    byte_depth : int, optional
        Image byte depth. Default is 8 for 8-bit images.
      
   Returns
   -------
   psnr : float
   """
    
   mse = MSE(image_1, image_2)
    
   if(mse == 0):  return np.inf
   # If MSE is null, then the two pictures are equal

   maximum_pixel = 2**byte_depth - 1

   psnr = 20 * log10(maximum_pixel / sqrt(mse)) # dB
    
   return psnr

def SSIM(image_1, image_2, byte_depth=8, win_size=None, channel_axis=None):    
    """Structural Similarity Index Measure (SSIM) to compare two images.
    
    Parameters
    ----------
    image_1, image_2 : np.array
        The two images to compare. Must have the same shape.
    byte_depth : int, optional
        Image byte depth. Default is 8 for 8-bit images.
        
    Returns
    -------
    ssim : float
    
    See also
    --------
    skimage.metrics.structural_similarity
    """
     
    data_range = 2**byte_depth

    image_1, image_2 = np.asarray(image_1), np.asarray(image_2)
    
    return structural_similarity(image_1, image_2, 
                                 data_range=data_range, win_size=win_size, 
                                 channel_axis=channel_axis)

def IOU(mask_1, mask_2):
    """Intersection Over Union (IOU) to compare two boolean masks.
    
    Parameters
    ----------
    mask_1, mask_2 : np.array, torch.Tensor
        The two image masks to compare. Must have the same shape.
        
    Returns
    -------
    iou : float
    """

    image_1, image_2 = np.asarray(image_1), np.asarray(image_2)
    intersection_count = int( np.sum(np.logical_and(mask_1, mask_2)) )
    union_count = int( np.sum(np.logical_or(mask_1, mask_2)) )
    
    return intersection_count / union_count

#%% PLOTTING TOOLS

def plot_image(image, title=None, dark=True, colormap="viridis",
               figsize=(2.66, 1.7), dpi=200, ax=None, **kwargs):
    """Plots an image

    Parameters
    ----------
    image : np.array
        Either grayscale (H,W) or RGB (H,W,3) image.
    title : str, optional
        Plot title. Default presents no title.
    dark : bool, optional
        Whether to use a black figure background or a white one. 
        Default is True, to produce a black background.
    colormap : str, matplotlib.colors.Colormap, optional
        Colormap used if input is a grayscale image. Default is 'viridis'.
    figsize : tuple of floats, optional
        Figure size in inches. Default is (2.66, 1.7) standing for 
        height, width.
    dpi : int, optional
        Dots per inch. Default is 200.
    ax : matplotlib.axes, optional
        Axes to plot in. If none is provided, then a new figure is set up 
        and its main axes are used (default behaviour).
    **kwargs : dict, optional
        Accepts Matplotlib's `imshow` kwargs.
    """

    if ax is None: 
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi, 
                               gridspec_kw=dict(left=0, right=1, top=1, bottom=0))
    else: fig = ax.get_figure()

    ax.imshow(image, cmap=colormap, **kwargs)
    if title is not None: 
        if dark: ax.set_title(title, fontsize="small", color="w")
        else: ax.set_title(title, fontsize="small")
    if dark: fig.patch.set_facecolor('k')
    ax.axis("off") # Remove axes and padding

    return fig, ax

def plot_images(*images, labels=None, title=None,
                dark=True, colormap="viridis", dpi=200, 
                shape_ratio=1, **kwargs):
    """Plots several images

    Parameters
    ----------
    images : list or tuple of np.ndarray
        Either grayscale (H,W) or RGB (H,W,3) images.
    labels : list of str, optional
        Image titles. Defaults present no title.
    dark : bool, optional
        Whether to use a black figure background or a white one. 
        Default is True, to produce a black background.
    colormap : str, matplotlib.colors.Colormap, optional
        Colormap used if input is a grayscale image. Default is 'viridis'.
    dpi : int, optional
        Dots per inch. Default is 200.
    **kwargs : dict, optional
        Accepts Matplotlib's `imshow` kwargs.
    """

    if labels is None: labels = [None]*len(images)

    if title is not None: top = 1.01
    else: top = 1

    fig, axes = plt.subplots(ncols=len(images), 
                             figsize=(5.1/shape_ratio, 1.7*len(images)), 
                             dpi=dpi, squeeze=False, 
                             gridspec_kw=dict(left=0, right=1, top=top, bottom=0))
    
    for k, image in enumerate(images):
        plot_image(image, labels[k], ax=axes[0][k], dpi=dpi,
                   dark=dark, colormap=colormap, **kwargs)

    if title is not None:
        if dark: plt.suptitle(title, fontsize="medium", color="white", y=0.98)
        else: plt.suptitle(title, fontsize="medium", y=0.98)
    
    return fig, axes

def plot_images_grid(*images_grid, 
                     columns_labels=None, rows_labels=None, rows_info=None, 
                     dark=True, colormap="viridis", dpi=200):
    """Plots a grid of images

    Parameters
    ----------
    images : list or tuple of np.ndarray
        Either grayscale (H,W) or RGB (H,W,3) images.
    columns_labels : list of str, optional
        Column titles. Defaults present no title.
    rows_labels : list of str, optional
        Rows titles. Defaults present no title.
    rows_info : dict of lists or np.ndarrays
        Additional row information. Dictionary keys could be metric labels 
        such as "MSE" or "SSIM" in case the value iterables contain the 
        metric associated to each row.
    dark : bool, optional
        Whether to use a black figure background or a white one. 
        Default is True, to produce a black background.
    colormap : str, matplotlib.colors.Colormap, optional
        Colormap used if input is a grayscale image. Default is 'viridis'.
    dpi : int, optional
        Dots per inch. Default is 200.
    **kwargs : dict, optional
        Accepts Matplotlib's `imshow` kwargs.
    """

    if not isinstance(images_grid)==np.ndarray:
        images_grid = np.array(images_grid)
    assert images_grid.dim >= 2, "Images must be on a 2D grid"
    
    n_columns = len(images_grid)
    n_rows = len(images_grid[0])
    mid_column = int(np.floor(n_columns/2))

    if columns_labels is None: 
        columns_labels = [None]*len(n_columns)

    if rows_labels is not None:
        labels = [[lab+lab_2 for lab_2 in rows_labels] for lab in columns_labels]
    else:
        labels = [[lab]+[None]*(n_rows-1) for lab in columns_labels]
    
    sec_labels = []
    if rows_info!={}:
        for i in range(n_rows):
            sec_labels.append([f"{k} {values[i]}" for k, values in rows_info.items()])
        if len(rows_info)>1:
            sec_labels = [" : "+", ".join(ls) for ls in sec_labels]
    if len(sec_labels)==0:
        sec_labels = [""]*n_rows

    fig, axes = plt.subplots(n_rows, n_columns, figsize=(1.7*n_columns, 1.7*n_rows), 
                             dpi=dpi, squeeze=False)
    for i in range(n_rows):
        for k, ims in enumerate(images_grid):
            if k==mid_column: label = labels[k][i]+sec_labels[i]
            else: label = labels[k][i]
            plot_image(ims[i].detach(), label, ax=axes[i][k],
                       dark=dark, colormap=colormap, dpi=dpi)
    
    return fig, axes

#%% OTHER PLOTTING TOOLS

def plot_bounding_boxes(ax, bboxes, colors=None):
    """Draw bounding boxes on a given figure axis.

    Parameters
    ----------
    bboxes : iterable of iterables with length 4
        List of bounding boxes in (x0, y0, xf, yf) format.
    colors : list of str, optional
        Colors for each bounding box. If None, all boxes will be red.
    """

    for i, (x0, y0, xf, yf) in enumerate(bboxes):
        color = colors[i] if colors is not None else "red"
        rect = patches.Rectangle((x0, y0), xf-x0, yf-y0, linewidth=0.5,
                                 edgecolor=color, facecolor="none")
        ax.add_patch(rect)

    return ax

def plot_colored_labels(labels, colors):
    """Plot a legend consisting of words on colors.
    
    Parameters
    ----------
    labels : list of str
        The label names.
    colors : list of str or list of tuples
        Colors corresponding to each label.
    """

    fontsize = 14; spacing = 1.5
    fig, ax = plt.subplots(figsize=(2.5, len(labels) * 0.3), facecolor="black")
    for i, (label, color) in enumerate(zip(labels, colors)):
        ax.text(0.01, 1 - i * spacing / len(labels), label,
                fontsize=fontsize, color=color, ha="left", va="top")
    ax.axis("off")
    plt.show()
    
    return fig, ax