# Montafons

Python library to generate an image _collage_ from other images. I mainly use it to generate horizontal wallpapers from multiple vertical images, but feel free to use it for any other purpuse. It is optimized for speed by using multiple threads to render images in paralel.

- **Author**: [LluisE](https://github.com/lluises)
- **Source**: https://github.com/lluises/montafons
- **Licence**: https://www.mozilla.org/en-US/MPL/2.0/


# Usage

This python library can be used as a CLI tool or as a library for another project.


## Use from the command line

Run `montafons`

```
usage: montafons [-h] -o OUTPUT [-H HEIGHT] [-W WIDTH] [-bc BGCOLOR] [-b BACKGROUND]
                 [-top BORDER_TOP] [-right BORDER_RIGHT] [-bottom BORDER_BOTTOM]
                 [-left BORDER_LEFT] [-smin SEPARATION_MIN] [-smax SEPARATION_MAX]
                 [-mw WIDTH_MIN] [-c CORRECTION_MAX] [-t] [-rn]
                 [images ...]

Make a montage with images

positional arguments:
  images                Images to process, or -

options:
  -h, --help            show this help message and exit
  -o, --output OUTPUT   Output file: "res.png"
  -H, --height HEIGHT   Output height in px, def:1080
  -W, --width WIDTH     Output width in px, def:total width of all images
  -bc, --background-color BGCOLOR
                        Background color in hex. def:FFFFFF
  -b, --background BACKGROUND
                        Background image (overwrites --background-color)
  -top, --border-top BORDER_TOP
                        Top border in px
  -right, --border-right BORDER_RIGHT
                        Right border in px
  -bottom, --border-bottom BORDER_BOTTOM
                        Bottom border in px
  -left, --border-left BORDER_LEFT
                        Left border in px
  -smin, --separation-min SEPARATION_MIN
                        Minimum separation between images
  -smax, --separation-max SEPARATION_MAX
                        Maximum separation between images
  -mw, --min-width WIDTH_MIN
                        Minimum width (after resize) of an image to be added
  -c, --correction CORRECTION_MAX
                        Maximum width correction when resizing images
  -t, --transparentify  Convert white pixels to transparent
  -rn, --random         Randomize image placement
```



## Usage as a library

```python
from montafons import Montafons

example_images = ['a.png', 'b.jpg', 'c.png']
params = {
    "width": 1080,
    "height": 1920,
    # More parameters can be added, see the parametres section
}

mf = Montafons(**params)

for image in example_images:
    mf.add(image)

mf.make("output.png")
```


### Parameters

The `Montafons` class constructor accepts the following parameters:

```
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
```


# LICENSE

This project is licenced under the Mozilla Public License version 2.0. You may obtain a copy of the licence at the [LICENCE file in this repository](./LICENSE), or online at [https://www.mozilla.org/en-US/MPL/2.0/](https://www.mozilla.org/en-US/MPL/2.0/).
