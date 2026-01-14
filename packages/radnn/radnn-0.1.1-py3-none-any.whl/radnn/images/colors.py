import numpy as np
from matplotlib import colors
from matplotlib.colors import to_rgba

LUMA_W = np.asarray([0.29889531 / 255.0, 0.58662247 / 255.0, 0.11448223 / 255.0], dtype=np.float32)

# ------------------------------------------------------------------------------------
# Analyse the image to H,S,L, B
def image_rgb_to_hslb(image):
  '''
  Analyzes an image and returns the hue, saturation, luma and brightness
  :param image:
  :return: image in HSLB format
  '''
  img_hsv = colors.rgb_to_hsv(image / 255.0)
  luma = np.dot(image, LUMA_W.T)
  return np.stack([img_hsv[..., 0], img_hsv[..., 1], luma, img_hsv[..., 2]], axis=-1).astype(np.float32)
# ------------------------------------------------------------------------------------
def image_rgb_to_hif(image):
  oImageHSLB = image_rgb_to_hslb(image)

  img_hsv = colors.rgb_to_hsv(image / 255.0)
  luma = np.dot(image, LUMA_W.T)
  return np.stack([img_hsv[..., 0], img_hsv[..., 1], luma], axis=-1).astype(np.float32)
# ------------------------------------------------------------------------------------
def color(name):
  return tuple([int(x*255) for x in to_rgba(name)])
# ------------------------------------------------------------------------------------
