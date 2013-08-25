Pyxl
====

This is the source code for Pyxl, a python implementation of (PixelHoldr)[https://github.com/chrisdingli/PixelHoldr] by (Christopher Dingli)[https://github.com/chrisdingli].

This is just the Pyxl code, a font and it's tests rather than implementing it into any Python framework -- something that should be incredibly trivial.

For flask you might use (pardon if it's not completely proper):
```
@app.route('/<info>/<size>/', defaults={'options':None})
@app.route('/<info>/<size>/<options>')
def makeImage(info, size, options):
    # lazy import like a boss
    from os.path import join, isfile

    p = Pyxl(info, size, options)
    
    path = 'where/images/live'
    fullpath = join(path, buildPyxlName(p))

    if not isfile(fullpath)
        p.draw()
        savePyxlImage(p, path)
    
    with open(fullpath) as f:
        image = f.read()

    resp = make_response(image)
    resp.headers['content_type'] = 'image/jpeg'

    return resp
```

Usage
-----
Pyxl works like this.

```
from pyxl import Pyxl, savePyxlImage

p = Pyxl('color:34df12', '300', None)
p.draw()
savePyxlImage(p)
```

Simple, no? There are three options for images:
1. color: Just pass a single color hex code to pyxl with this prefix.
2. gradient: Pass two color hex codes with this prefix, you can also specify a horizontal gradient by add ',h' to the hex codes.
3. flickr: Pass a series of comma delimited tags to Pyxl. This is a work in progress, currently and pyxl.drawFlickr currently does nothing.

Pyxl deals with converting hex codes to RGB tuples for you. It'll even extend shorthand codes like `f00` to `ff0000` and `f0` to `f0f0f0`. And, if you happen to accidentally forget a number (or put one too many), Pyxl'll handle that too: either padding with zeroes or truncating where needed.

###Options
Pyxl is constructed from three bits: `info`, `size` and `options`. Info is covered above, and size is obvious (you can pass either one dimension for a square or two for a rectangle). However, options has, well, options:

1. text: This gets a color hex code and determines the color of the dimension display and the watermark text (in the case of a flickr image).
2. font: A simple font name which changes the font of the dimension display and the watermark text (in the case of a flickr image). Pyxl comes packaged with a copy of LiberationSans-Regular.ttf for easy use, but dump whatever fonts you have a license to use in the fonts directory -- by default this is `fonts` but it can be changed by passing the path to pyxl after the options argument.
3. dimensions: If this option is passed, pyxl doesn't diplay the dimensions on the image.
4. seed: This is here to create a new file. It's only useful for creating a new flickr image.

Options are passed to Pyxl in this format `name:value` and are delimited by commas.
###A fuller example

```
p = Pyxl('gradient:f00,00f', '500x200', 'text:000')
```

This would create an image that's 500x200 with a vertical gradient from red to blue and the text will be black.

```
p = Pyxl('color:f', '30', 'dimensions:hide')
```

This is a white, 30x30 square with no dimensions on it.

Drop LiberationMono-Bold.ttf into your fonts folder

```
p = Pyxl('gradient:a63f7f,45d31a,h', '2500', 'font:liberationmono-bold')
```

Pyxl'll will detect it on build and make it a valid option.

Or, you can just change your fonts folder:

```
p = Pyxl('gradient:a63f7f,45d31a,h', '2500', 'font:liberationmono-bold', '/usr/share/fonts/truetype/liberation')
```

Installation
------------
Working on this.
