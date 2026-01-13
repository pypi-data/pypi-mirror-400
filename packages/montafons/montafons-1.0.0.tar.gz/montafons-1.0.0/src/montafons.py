#!/usr/bin/python3

import os
import sys
import random
import concurrent.futures
from PIL import Image

VERSION = "1.0.0"
VERSION_DATE = "2026-01-05"


class Montafons:
    """
    Montafons
    LluísE 2020-04-16
    kitsune.cat

    Parameters
      *args           ["/path/to/image.png", "img2.jpg"] (optional)
      height          int, in px (default 1080)
      width           int, in px (default -1, no width limit)
      background      "/path/to/image.png" or tuple(R, G, B)
      bottom_top      int, in px (default 0)
      bottom_right    int, in px (default 0)
      bottom_bottom   int, in px (default 0)
      bottom_left     int, in px (default 0)
      separation_min  int, in px (defalut 0)
      separation_max  int, in px (default 65536)
      width_min       int, in px (default 0)
      correction_max  int, in px (default 0)
      transparentify  bool (change white for transparent) (default false)
      random          bool (default false) Randomize image placement

    Changelog
      2021-07-24 Added threads, other optimitzations and readability.
      2021-11-23 Added main with argparse (copied from older iterations)
      2022-10-01 Added correction_max
      2023-06-03 Added random
      2026-01-05 Public release of the source code and as a PyPI package
    """

    def __init__(self, *images, **kwargs):
        self.width       = kwargs.get('width')          or -1
        self.height      = kwargs.get('height')         or 1080
        self._background = kwargs.get('background')     or (255, 255, 255)
        self.space_min   = kwargs.get('separation_min') or 0
        self.width_min   = kwargs.get('width_min')      or 0
        self.forcetrans  = kwargs.get('transparentify') or False
        self.random      = kwargs.get('random') or False
        self.correction_max = kwargs.get('correction_max') or 0
        self.space_max  = (
            kwargs['separation_max']
            if kwargs.get('separation_max') is not None else 65536)
        self.borders = {
            'top'    : kwargs.get('border_top')    or 0,
            'right'  : kwargs.get('border_right')  or 0,
            'bottom' : kwargs.get('border_bottom') or 0,
            'left'   : kwargs.get('border_left')   or 0,
        }
        self.canvas  = None
        self.stack   = []
        self.stack_w = 0

        for image in images:
            self.add(image)

    def make(self, output=None):
        """
        Generate the montage, and if output defined it saves it
        """
        if self.random:
            random.shuffle(self.stack)

        # Calculate some numbers
        width, height = self._get_size()
        correction    = self._calculate_image_width_correction(width)
        space         = self._get_space(width, correction)
        draw_height   = height - self.borders['top'] - self.borders['bottom']
        x = self._get_left_margin(width, self.stack_w, space, correction, len(self.stack))
        y = self.borders['top']
        positions = self.calculate_positions(draw_height, space, correction, x, y)
        last_correction_bonus = 0
        if self.stack:
            last_correction_bonus = int(
                width
                - (positions[-1][0]
                   + self._size_by_height_with_correction(self.stack[-1], height, correction)[0]
                   + space)
            )

        # Generate the empty canvas
        self.canvas = self._get_canvas(width, height)

        # Resize and add images to the canvas
        for index, img in self.resize_all_images(draw_height, correction, last_correction_bonus):
            params = {}
            if img.mode == "RGBA":
                params['mask'] = img
            elif self.forcetrans:
                img.convert("RGBA")
                params['mask'] = self.white2transmask(img)
            self.canvas.paste(img, positions[index], **params)

        # Save if needed
        if output:
            self.canvas.save(output)
        return self

    def save(self, output):
        """
        Save the canvas to output path
        """
        self.canvas.save(output)

    def add(self, image, ignore=None):
        """
        Adds an image.
        image: Image() or "/path/to/image.png"
        Returns False if not added (in case ignore is False)
        """
        ignore = ignore if ignore is not None else self.width <= 0
        if isinstance(image, str):
            image = Image.open(image)
        w, h = self._size_by_height(
            image,
            self.height - self.borders['top'] - self.borders['bottom']
        )
        if (ignore
            or (w >= self.width_min
                and (self.stack_w + w + self.space_min*(len(self.stack)-1)
                     <= self.width))):
            self.stack_w += w
            self.stack.append(image)
            return True
        return False

    def background(self, background):
        """
        Set the background image path
        """
        self._background = background

    def white2transmask(self, image):
        """
        Transparentify an image. Returns the new transparentifyied image
        """
        res = Image.new('RGBA', image.size)
        res.putdata([(255, 255, 255, 0 if item[0] == 255 and item[1] == 255 and item[2] == 255 else 255) for item in image.getdata()])
        return res

    def resize_image(self, image, size:tuple, crop:tuple=None):
        """
        Resizes an image and returns it.
        Size is the size to which the image will be resized
        Crop is the final size of the image, the cropping will be centered.
        """
        w, h   = size
        cw, ch = crop
        img = image.resize(size, Image.Resampling.LANCZOS)
        if crop and (cw != w or ch == h):
            img = img.crop((0, (h-ch)//2, w, h - (h-ch)//2))
        return img

    def resize_all_images(self, height, correction, last_correction_bonus=0):
        """
        Generator that returns (index, resized_image)
        WARNING: Order is not preserved.
        Uses threads
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            future_todo = {}
            for i in range(len(self.stack)):
                w, h = self._size_by_height_with_correction(self.stack[i], height, correction)
                cw, ch = self._size_by_height(self.stack[i], height)
                if last_correction_bonus > 0 and i == len(self.stack)-1:
                    w += last_correction_bonus
                    cw += last_correction_bonus
                future = executor.submit(
                    self.resize_image,
                    self.stack[i],
                    (w, h),
                    (cw, ch),
                )
                future_todo[future] = i

            for future in concurrent.futures.as_completed(future_todo):
                index = future_todo[future]
                try:
                    newimg = future.result()
                except Exception as e:
                    print(f"Error resizing {index}: {e}")
                    continue
                yield (index, newimg)

    def calculate_positions(self, height, space, correction, start_x, start_y):
        """
        Calculate canvas positions of images in stack
        """
        res = [] # [(width, height)]
        x = start_x
        y = start_y
        for img in self.stack:
            w, h = self._size_by_height_with_correction(img, height, correction)
            res.append((int(x), y))
            x += w + space
        return res

    def _get_left_margin(self, width, images_width, space, correction, total_images):
        """
        Calculate the left margin (in pixels) considering the borders
        """
        res = round((width
                - images_width
                - space * (total_images - 1)
                - correction * (total_images)
                - self.borders['right']) / 2)
        return res if res > self.borders['left'] else self.borders['left']

    def _get_size(self):
        """
        Calculate the total width and height of the final image from parameters
        """
        width = self.width
        if width <= 0:
            width = self.stack_w
        height = self.height
        if height <= 0:
            height = max(img.size[1] for img in self.stack)
        return width, height

    def _get_space(self, width, correction=0):
        """
        Calculate the space (in pixels) between images
        """
        space = round((width
                       - self.stack_w
                       - self.borders['left']
                       - self.borders['right']
                       - correction * len(self.stack))
                      / (len(self.stack) + 1))
        if space < self.space_min:
            space = self.space_min
        if space > self.space_max:
            space = self.space_max
        return space

    def _calculate_image_width_correction(self, width) -> int:
        """
        Calculate the width correction in pixels
        """
        if self.correction_max <= 0: # Don't do calculations if no correction
            return 0
        return min(
            self.correction_max,
            round((width - self.stack_w) / len(self.stack))
        )

    def _size_by_height(self, image, height=None):
        """
        Calculate a resizing from height keeping aspect ratio. Returns new size
        """
        height = height or self.height
        w, h   = image.size
        return int(w * height / h), height

    def _size_by_height_with_correction(self, image, height=None, correction=0):
        """
        Calculate a resizing from height keeping aspect ratio. Returns new size
        Applies correction to width
        """
        w, h = self._size_by_height(image, height)
        return self._size_by_width(image, w + correction)

    def _size_by_width(self, image, width=None):
        """
        Calculate a resizing from width keeping aspect ratio. Returns new size
        """
        width = width or self.width
        w, h  = image.size
        return (width, int(h * width / w))

    def _get_canvas(self, width=None, height=None, background=None):
        """
        Creates a canvas
        """
        width  = width  or self.width
        height = height or self.height
        background = background or self._background
        if not isinstance(background, str):
            return Image.new('RGB', (width, height), background)
        canvas = Image.open(background)

        iw, ih = canvas.size
        if iw != width or ih != height:
            nw, nh = self._size_by_height(canvas, height)
            if nw < width:
                nw, nh = self._size_by_width(canvas, width)
            canvas = canvas.resize((nw, nh), Image.LANCZOS)
            left = abs(width  - nw) // 2
            top  = abs(height - nh) // 2
            if left or top:
                canvas = canvas.crop((left, top, width+left, height+top))

        return canvas

def parse_arguments():
    import argparse
    parser = argparse.ArgumentParser(description='Make a montage with images')
    parser.add_argument('images', type=str, nargs='*',
                        help='Images to process, or -')
    parser.add_argument('-o', '--output', type=str, dest='output',
                        help='Output file: "res.png"', required=True)
    parser.add_argument('-H', '--height', type=int, dest='height',
                        help='Output height in px, def:1080')
    parser.add_argument('-W', '--width', type=int, dest='width',
                        help='Output width in px, def:total width of all images')
    parser.add_argument('-bc', '--background-color', type=str, dest='bgcolor',
                        help='Background color in hex. def:FFFFFF')
    parser.add_argument('-b', '--background', type=str, dest='background',
                        help='Background image (overwrites --background-color)')
    parser.add_argument('-top', '--border-top', type=int, dest='border_top',
                        help='Top border in px')
    parser.add_argument('-right', '--border-right', type=int, dest='border_right',
                        help='Right border in px')
    parser.add_argument('-bottom', '--border-bottom', type=int, dest='border_bottom',
                        help='Bottom border in px')
    parser.add_argument('-left', '--border-left', type=int, dest='border_left',
                        help='Left border in px')
    parser.add_argument('-smin', '--separation-min', type=int, dest='separation_min',
                        help='Minimum separation between images')
    parser.add_argument('-smax', '--separation-max', type=int, dest='separation_max',
                        help='Maximum separation between images')
    parser.add_argument('-mw', '--min-width', type=int, dest='width_min',
                        help='Minimum width (after resize) of an image to be added')
    parser.add_argument('-c', '--correction', dest='correction_max', type=int, default=0,
                        help='Maximum width correction when resizing images')
    parser.add_argument('-t', '--transparentify', dest='transparentify', default=False,
                        action="store_true", help='Convert white pixels to transparent')
    parser.add_argument('-rn', '--random', dest='random', default=False,
                        action="store_true", help='Randomize image placement')
    parser.add_argument('-v', '--version', dest='version', default=False,
                        action="store_true", help='Print version and exit')
    return parser.parse_args()

def hex2rgb(h):
    # "00FF00" → (0, 255, 0)
    return tuple(int(h[i:i+2],16)for i in(0,2,4))

def read_stdin():
    return [l.strip() for l in sys.stdin.readlines() if l]

def main():
    if '-v' in sys.argv[1:] or '--version' in sys.argv[1:]:
        print(f"Montafons version {VERSION} ({VERSION_DATE})")
        print(f"Created by LluísE <https://kitsune.cat>")
        return 0

    params = vars(parse_arguments())
    params['background'] = params.get('background') or \
        hex2rgb(params.get('bgcolor') or 'FFFFFF')

    images = params.get('images', [])
    if '-' in images:
        del images[images.index('-')]
        images += read_stdin()

    mf = Montafons(**params)
    for image in images:
        try:
            if mf.add(image):
                print(image)
        except Exception as e:
            pass
    mf.make(params['output'])

    return 0

if __name__ == '__main__':
    sys.exit(main())
