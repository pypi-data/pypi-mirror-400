import numpy as np
from radnn.core import RequiredLibs
oReqs = RequiredLibs()
if oReqs.is_opencv_installed:
  import cv2
from PIL import Image, ImageChops, ImageFilter, ImageDraw
from .colors import color

phi=(1.0+np.sqrt(5.0))/2.0

class ImageProcessor(object):
  # --------------------------------------------------------------------------------------------------------------------
  def __init__(self, pixels=None, filename=None, image=None, bgcolor=None):
    self.pixels = pixels
    self.filename = filename
    self.image = image
    self.bgcolor = bgcolor
    self._size = None

    if self.pixels is not None:
      if self.pixels is not None:
        nShape = self.pixels.shape
        if len(nShape) == 4:
          self._size = nShape[1:4]
        elif len(nShape) == 3:
          self._size = nShape[1:3]
        elif len(nShape) == 2:
          self._size = nShape

    if image is not None:
      self.pixels = np.array(self.image)
  # --------------------------------------------------------------------------------------------------------------------
  @property
  def size(self):
    if self.image is not None:
      return self.image.size
    else:
      return self._size
  # --------------------------------------------------------------------------------------------------------------------
  def load(self, filename=None):
    if filename is not None:
      self.filename = filename
    self.image = Image.open(self.filename).convert("RGB")
    self.pixels = np.array(self.image)
    return self
  # --------------------------------------------------------------------------------------------------------------------
  def pad_square_with_edges(self, size=(227, 227)):
    img = self.image
    img_width, img_height = img.size

    # Determine the scaling factor to maintain aspect ratio
    if img_width > img_height:
      bIsLandscape = True
      ratio = img_height / img_width
      new_width = size[0]
      new_height = int(size[0] * ratio)
    else:
      bIsLandscape = False
      ratio = img_width / img_height
      new_width = int(size[1] * ratio)
      new_height = size[1]

    # Resize the image while maintaining aspect ratio
    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Create a blank canvas for the final image
    Result = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    img_array = np.array(img)

    # Center the resized image on the new canvas
    offset_x = (size[0] - new_width) // 2
    offset_y = (size[1] - new_height) // 2
    Result[offset_y:offset_y + new_height, offset_x:offset_x + new_width, :] = img_array

    # Fill edges with repeated stripes and blur for a smooth effect
    if bIsLandscape:
      # Top and bottom padding
      first_row = Result[offset_y, :, :]
      last_row = Result[offset_y + new_height - 1, :, :]

      top_rows = np.repeat(first_row.reshape(1, size[0], 3), offset_y, axis=0)
      bottom_rows = np.repeat(last_row.reshape(1, size[0], 3), size[1] - offset_y - new_height, axis=0)

      # Apply blur to soften edges
      im_top = Image.fromarray(top_rows).filter(ImageFilter.BLUR)
      im_bottom = Image.fromarray(bottom_rows).filter(ImageFilter.BLUR)

      Result[0:offset_y, :, :] = np.array(im_top)
      Result[offset_y + new_height:size[1], :, :] = np.array(im_bottom)
    else:
      # Left and right padding
      first_col = Result[:, offset_x, :]
      last_col = Result[:, offset_x + new_width - 1, :]

      left_cols = np.repeat(first_col.reshape(size[1], 1, 3), offset_x, axis=1)
      right_cols = np.repeat(last_col.reshape(size[1], 1, 3), size[0] - offset_x - new_width, axis=1)

      # Apply blur to soften edges
      im_left = Image.fromarray(left_cols).filter(ImageFilter.BLUR)
      im_right = Image.fromarray(right_cols).filter(ImageFilter.BLUR)

      Result[:, 0:offset_x, :] = np.array(im_left)
      Result[:, offset_x + new_width:size[0], :] = np.array(im_right)

    # Convert back to a PIL image
    final_img = Image.fromarray(Result)
    return ImageProcessor(image=final_img, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def _get_background_color(self, bgcolor):
    if bgcolor is not None:
      self.bgcolor = bgcolor
    if self.bgcolor is None:
      self.bgcolor = "black"
    if isinstance(self.bgcolor, str):
      nBGColor = color(self.bgcolor)
    else:
      nBGColor = self.bgcolor
    return nBGColor
  # --------------------------------------------------------------------------------------------------------------------
  def roll(self, shift_x=0, shift_y=0, bgcolor=None):
    nBGColor = self._get_background_color(bgcolor)
    img = self.image

    arr = np.array(img)

    # Apply roll effect
    arr = np.roll(arr, shift_x, axis=1)  # Shift horizontally
    arr = np.roll(arr, shift_y, axis=0)  # Shift vertically

    img_out = Image.fromarray(arr)


    return ImageProcessor(image=img_out, filename=self.filename, bgcolor=self.bgcolor)

  # --------------------------------------------------------------------------------------------------------------------
  def zoom_center(self, scale=1.2, bgcolor=None):
    nBGColor = self._get_background_color(bgcolor)
    img = self.pixels
    w, h = self.size

    tx, ty = 0, 0
    if scale < 1.0:
      tx = int((w * (1.0 - scale)) // 2)
      ty = int((h * (1.0 - scale)) // 2)
    else:
      tx = - int(w*(scale - 1.0) // 2)
      ty = - int(w*(scale - 1.0) // 2)

    # Transformation matrix for scaling and translation
    M = np.array([[scale, 0, tx],
                  [0, scale, ty]], dtype=np.float32)

    # Apply affine warp
    result = cv2.warpAffine(img, M, (w, h))

    oImage = Image.fromarray(result)
    oCropped = oImage.crop((tx, ty, w - tx - 1, h - ty - 1)).convert("RGBA")
    oNewImageWithBackground = Image.new("RGBA",self.size, nBGColor)
    oNewImageWithBackground.paste(oCropped, (tx, ty), oCropped)

    return ImageProcessor(image=oNewImageWithBackground, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def zoom_pan(self, scale=1.2, tx=20, ty=20, bgcolor=None):
    nBGColor = self._get_background_color(bgcolor)
    img = self.pixels
    w, h = self.size

    # Transformation matrix for scaling and translation
    M = np.array([[scale, 0, tx],
                  [0, scale, ty]], dtype=np.float32)

    # Apply affine warp
    result = cv2.warpAffine(img, M, (w, h))

    oImage = Image.fromarray(result)
    oCropped = oImage.crop((tx, ty, w*scale - tx, h*scale - ty)).convert("RGBA")
    oNewImageWithBackground = Image.new("RGBA",self.size, nBGColor)
    oNewImageWithBackground.paste(oCropped, (tx, ty), oCropped)

    return ImageProcessor(image=oNewImageWithBackground, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def wave_effect(self, amplitude=20, frequency=0.1):
    img = self.pixels
    w, h = self.size

    # Create mapping arrays
    map_x = np.zeros((h, w), dtype=np.float32)
    map_y = np.zeros((h, w), dtype=np.float32)

    for i in range(h):
      for j in range(w):
        offset_x = int(amplitude * np.sin(2 * np.pi * frequency * i))
        map_x[i, j] = j + offset_x
        map_y[i, j] = i

    # Apply remapping
    result = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)
    pil_image = Image.fromarray(result)
    return ImageProcessor(image=pil_image, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def rotate(self, degrees, is_original_scale=True, bgcolor=None):
    nBGColor = self._get_background_color(bgcolor)
    oImageRGBA = self.image.convert('RGBA')
    oImageRotated = oImageRGBA.rotate(degrees, expand=True)
    oBackground = Image.new('RGBA', oImageRotated.size, nBGColor)
    oNewImage = Image.composite(oImageRotated, oBackground, oImageRotated).convert(self.image.mode)

    if is_original_scale:
      orig_w, orig_h = self.image.size
      new_w, new_h = oNewImage.size
      left = (new_w - orig_w) // 2
      top = (new_h - orig_h) // 2
      right = left + orig_w
      bottom = top + orig_h

      # Crop to original aspect ratio
      oNewImage = oNewImage.crop((left, top, right, bottom))
    else:
      # Composite the rotated image onto the background using its alpha mask
      oNewImage = Image.composite(oImageRotated, oBackground, oImageRotated).convert(self.image.mode)

    return ImageProcessor(image=oNewImage, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def fit_to_size(self, size=(227, 227), bgcolor=None):
    nBGColor = self._get_background_color(bgcolor)

    img = self.image
    img_width = float(self.size[0])
    img_height = float(self.size[1])

    if img_width > img_height:
      bIsLandscape = True
      ratio = img_height / img_width
      new_width = size[0]
      new_height = int(size[0] * ratio)
    else:
      bIsLandscape = False
      ratio = img_width / img_height
      new_width = int(size[0] * ratio)
      new_height = size[0]

    img = img.resize((new_width, new_height), Image.NONE).convert("RGBA")

    nOffsetX = 0
    nOffsetY = 0
    if bIsLandscape:
      nOffsetY = (size[1] - img.size[1]) // 2
    else:
      nOffsetX = (size[0] - img.size[0]) // 2

    thumb = img.crop((0, 0, size[0], size[1]))

    oMovedImage = ImageChops.offset(thumb, int(nOffsetX), int(nOffsetY))

    oNewImageWithBackground = Image.new("RGBA", oMovedImage.size, nBGColor)
    oNewImageWithBackground.paste(oMovedImage, (0, 0), oMovedImage)

    return ImageProcessor(image=oNewImageWithBackground, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def crop_to_size(self, target_size=(227, 227)):
    """
    Resizes the image so that the smallest dimension matches the corresponding
    target size dimension, then center crops it to the exact target size.

    :param image: PIL Image to be processed.
    :param target_size: Tuple (width, height) of the desired output size.
    :return: Cropped PIL Image of the specified size.
    """
    target_w, target_h = target_size
    img_w, img_h = self.size

    # Determine scale factor to match the smallest dimension
    scale = max(target_w / img_w, target_h / img_h)
    new_size = (int(img_w * scale), int(img_h * scale))

    # Resize while maintaining aspect ratio
    oResizedImage = self.image.resize(new_size, Image.NONE) #Image.LANCZOS

    # Center crop to the exact target size
    left = (oResizedImage.width - target_w) / 2
    top = (oResizedImage.height - target_h) / 2
    right = left + target_w
    bottom = top + target_h

    oCroppedImage = oResizedImage.crop((left, top, right, bottom))

    return ImageProcessor(image=oCroppedImage, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def horizontal_wave_effect(self, amplitude=7, frequency=0.01, bgcolor=None):
    nBGColor = self._get_background_color(bgcolor)

    img = self.pixels
    w, h = self.size

    # Create mapping arrays
    map_x = np.zeros((h, w), dtype=np.float32)
    map_y = np.zeros((h, w), dtype=np.float32)

    for i in range(h):
      for j in range(w):
        offset_y = int(amplitude * np.sin(2 * np.pi * frequency * j))  # Horizontal wave
        map_x[i, j] = j
        map_y[i, j] = i + offset_y  # Apply wave effect in Y direction

    # Apply remapping
    result = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=nBGColor)
    oImage = Image.fromarray(result)
    return ImageProcessor(image=oImage, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def drop_shadow(self, shrink=0.9, shadow_offset=(8, 8), shadow_blur=15,
                            shadow_color=(32, 32, 32, 255), bgcolor=None):
    """
    Shrinks an image while keeping the final output dimensions the same by adding a drop shadow.

    Parameters:
        shrink_factor (float): The factor by which the image is shrunk (0 < shrink_factor ≤ 1).
        shadow_offset (tuple): The (x, y) offset for the shadow.
        shadow_blur (int): The blur radius for the shadow.
        shadow_color (tuple): RGBA color of the shadow (default is semi-transparent black).

    Returns:
        ImageProcessor: A new instance with the processed image.
    """
    nBGColor = self._get_background_color(bgcolor)
    assert shrink < 1.0, "The shrink factor should be less than 1.0"
    img = self.pixels
    w, h = self.size

    # Compute new size for the shrunk image
    new_w = int(w * shrink)
    new_h = int(h * shrink)

    # Place the shrunk image centered in the original dimensions
    x_center = (w - new_w) // 2
    y_center = (h - new_h) // 2


    # Resize the image (shrink)
    shrunk_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Create transparent background
    shadow_img = np.zeros((h, w, 4), dtype=np.uint8)
    shadow_img[:,:,:4] = list(nBGColor)[:]

    # Create shadow by filling an ellipse or rectangle (based on image shape)
    shadow = np.full((new_h, new_w, 4), shadow_color, dtype=np.uint8)

    # Blur the shadow
    shadow = cv2.GaussianBlur(shadow, (shadow_blur, shadow_blur), 0)

    # Position the shadow
    x_offset, y_offset = x_center + shadow_offset[0], y_center + shadow_offset[1]
    shadow_img[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = shadow

    # Convert shrunk image to 4-channel RGBA if not already
    if shrunk_img.shape[2] == 3:
      shrunk_img = cv2.cvtColor(shrunk_img, cv2.COLOR_RGB2RGBA)

    # Paste the shrunk image onto the shadow
    shadow_img[y_center:y_center + new_h, x_center:x_center + new_w] = shrunk_img

    # Convert back to PIL image
    oImage = Image.fromarray(shadow_img)

    return ImageProcessor(image=oImage, filename=self.filename, bgcolor=self.bgcolor)
  # --------------------------------------------------------------------------------------------------------------------
  def make_mbsf_augmented_square(self, size=(227, 227)):
    '''
    Used in MSBF paper
    :param size:
    :return:
    '''
    nSize = size

    nHalfSize = (nSize[0] // 2, nSize[1] // 2)
    nModX = nSize[0] % 2
    nModY = nSize[1] % 2

    img = self.image

    img_width = float(self.size[0])
    img_height = float(self.size[1])
    nAspectRatio = img_width / img_height
    if nAspectRatio > 1.0:
      bIrregular = nAspectRatio > (phi * 0.9)
      bIsTopBottomPadding = True
    else:
      bIrregular = nAspectRatio < (1.0 / (phi * 0.9))
      bIsTopBottomPadding = False

    # print("[%d,%d]  AspectRatio:%.4f  Irregular:%r" % (img_width, img_height, nAspectRatio, bIrregular))
    nRatioWidth = 1.0
    nRatioHeight = 1.0
    if bIrregular:
      if img_width > img_height:
        nRatioHeight = img_height / img_width
      else:
        nRatioWidth = img_width / img_height
    else:
      if img_width > img_height:
        nRatioWidth = img_width / img_height
      else:
        nRatioHeight = img_height / img_width

    new_width = int(nSize[0] * nRatioWidth)
    new_height = int(nSize[1] * nRatioHeight)

    img = img.resize((new_width, new_height), Image.NONE)
    # print("New Image Size", self.size)

    if bIrregular:
      thumb = img.crop((0, 0, nSize[0], nSize[1]))

      offset_x = int(max((nSize[0] - self.size[0]) / 2, 0))
      offset_y = int(max((nSize[1] - self.size[1]) / 2, 0))

      img = ImageChops.offset(thumb, offset_x, offset_y)

      Result = np.array(img)

      # TODO: Fadding out by number of space size
      if bIsTopBottomPadding:
        space_size_top = offset_y
        space_size_bottom = nSize[1] - new_height - offset_y
        # print("top %i, bottom %i" %(space_size_top, space_size_bottom))

        first_row = Result[offset_y + 1, :, :]
        last_row = Result[offset_y + new_height - 1, :, :]
        # first_row=np.repeat( np.mean(first_row, axis=0).reshape(1, Result.shape[2]),  Result.shape[1], axis=0)
        # last_row=np.repeat( np.mean(first_row, axis=0).reshape(1, Result.shape[2]),  Result.shape[1], axis=0 )

        top_rows = np.repeat(first_row.reshape(1, Result.shape[1], Result.shape[2]), space_size_top + 1, axis=0)
        bottom_rows = np.repeat(last_row.reshape(1, Result.shape[1], Result.shape[2]), space_size_bottom, axis=0)

        im1 = Image.fromarray(top_rows)
        im1 = im1.filter(ImageFilter.BLUR)
        top_rows = np.array(im1)

        im2 = Image.fromarray(bottom_rows)
        im2 = im2.filter(ImageFilter.BLUR)
        bottom_rows = np.array(im2)

        Result[0:offset_y + 1, :, :] = top_rows[:, :, :]
        Result[offset_y + new_height:nSize[1], :, :] = bottom_rows[:, :, :]
      else:

        space_size_left = offset_x
        space_size_right = nSize[0] - new_width - space_size_left
        # print("left %i, right %i" %(space_size_left, space_size_left))

        first_col = Result[:, offset_x + 1, :]
        last_col = Result[:, offset_x + new_width - 1, :]

        left_cols = np.repeat(first_col.reshape(Result.shape[0], 1, Result.shape[2]), space_size_left + 1, axis=1)
        right_cols = np.repeat(last_col.reshape(Result.shape[0], 1, Result.shape[2]), space_size_right, axis=1)

        im1 = Image.fromarray(left_cols)
        im1 = im1.filter(ImageFilter.BLUR)
        left_cols = np.array(im1)

        im2 = Image.fromarray(right_cols)
        im2 = im2.filter(ImageFilter.BLUR)
        right_cols = np.array(im2)

        Result[:, 0:offset_x + 1, :] = left_cols[:, :, :]
        Result[:, offset_x + new_width:nSize[0], :] = right_cols[:, :, :]

      img = Image.fromarray(Result)

      # print("Base Image Size", self.size)
    # plt.imshow(np.array(img))
    # plt.show()


    if nAspectRatio > 1.0:
      nDiff = (self.size[0] - self.size[1]) // 2
    else:
      nDiff = (self.size[1] - self.size[0]) // 2
    #
    #
    #     if False:
    #         a4im = Image.new('RGB',
    #                          (595, 842),   # A4 at 72dpi
    #                          (255, 255, 255))  # White
    #         a4im.paste(img, img.getbbox())  # Not centered, top-left corne
    #         plt.imshow(np.array(a4im))
    #         plt.show()
    nCenterX = self.size[0] // 2
    nCenterY = self.size[1] // 2

    nImgCropped = [None] * 3
    if nDiff > 40:
      nCropPositions = [0, -nDiff // 2, nDiff // 2]
    else:
      nCropPositions = [0]

    for nIndex, nShiftPos in enumerate(nCropPositions):
      nPosX = nCenterX
      nPosY = nCenterY
      if nAspectRatio > 1.0:
        nPosX += nShiftPos
      else:
        nPosY += nShiftPos

      nLeft = nPosX - nHalfSize[0]
      nRight = nPosX + nHalfSize[0] + nModX

      nTop = nPosY - nHalfSize[1]
      nBottom = nPosY + nHalfSize[1] + nModY
      nImgCropped[nIndex] = np.array(img.crop((nLeft, nTop, nRight, nBottom)))

    if len(nCropPositions) == 1:
      nImgCropped[1] = np.array(self.rotate(img, 12).pixels)
      nImgCropped[2] = np.array(self.rotate(img, -12).pixels)

    return nImgCropped