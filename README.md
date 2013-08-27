Pyxl
====

This is the source code for Pyxl, a python implementation of [PixelHoldr](https://github.com/chrisdingli/PixelHoldr) by [Christopher Dingli](https://github.com/chrisdingli).

This is just the Pyxl code, a font and it's tests rather than implementing it into any Python framework -- something that should be incredibly trivial.

For flask you might use (pardon if it's not completely proper):
```
from pyxl import Pyxl, buildPyxlName, savePyxlImage

@app.route('/<info>/<size>/', defaults={'options':None})
@app.route('/<info>/<size>/<options>/')
def makeImage(info, size, options):
    # lazy import like a boss
    from os.path import join, isfile

    p = Pyxl(info, size, options)
    
    path = 'where/images/live'
    fullpath = join(path, buildPyxlName(p))

    if not isfile(fullpath)
        p.draw()
        savePyxlImage(p, path)
        image = p.image

    else:
        with open(fullpath) as f:
            image = f.read()

    resp = make_response(image)
    resp.headers['content_type'] = 'image/jpeg'

    return resp
```

Pyxl is smart enough to not do any heavy lifting if it doesn't have to. Already got an image built from these settings? Pyxl doesn't need to do a thing. It's also smart enough to keep image duplication low:

```
p = Pyxl('toy,cat', '300', None)
```

will produce the same output (including file name hash) as:

```
p = Pyxl('cat',toy', '300', None)
```

Flickr tags and options keys are both sorted before generating a file name so you don't need to worry about someone remembering what order they put those in. Pyxl does it for them (and for your server).

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

When working with Pyxl, there's only four things you really need to know:

1. Building a new `Pyxl` object.
2. Drawing the image by calling `Pyxl.draw()`
3. Saving the image with `savePyxlImage()`
4. And maybe checking what the image name will be with `buildPyxlName()`

If you really want to, there's a handful of getters as well:

1. `Pyxl.getInfo()` will return the string representation of `Pyxl.info`.
2. `Pyxl.getSize()` will return the string representation of `Pyxl.size`, including expanding it to two dimensions if one was passed.
3. `Pyxl.getOptions()` will return the string representation of `Pyxl.options`, including sorting the options by name and stripping out any invalid options.

These are used in buildPyxlName to construct the hash name for the image, but you might use them for storing information in a database or adding EXIF data to the image.

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
Pyxl has a few requirements.
1. PIL or Pillow with JPEG support.
2. The FlickrAPI.

However, these are easy enough to install. PIL may have to be installed after installing a JPEG library, though. Double check your setup.

After that, pop over to the (Flickr API page)[http://www.flickr.com/services/api/] to get an API key. Add that `flickrapi.json` (make sure you strip .sample from the end of that file).

You should be good to go.
