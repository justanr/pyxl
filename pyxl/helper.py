'''Helper utilities for pyxl. These are things that pyxl needs 
but that don't need to be in the main module file.'''

import urllib2
import StringIO

from glob    import glob
from os.path import basename, join
from string  import maketrans


from flickrapi import FlickrAPI

__all__ = [
            'correct_hex_color', 
            'hex_to_RGB', 
            'RGB_to_hex', 
            'calc_grad_diff', 
            'shift_RGB', 
            'get_flickr_image',
            'shifter'
            ]

def correct_hex_color(hex_str):
    '''Accepts a hex color string like #34fA8c and ensures that it
    is the correct length and removes all letters beyond f.

    TODO: Maybe write a regex to make this more elegant. But then I have two problems.
    http://www.codinghorror.com/blog/2008/06/regular-expressions-now-you-have-two-problems.html
    '''
    removed = ' #ghijklmnopqrstuvwxyz'
    replace = ''

    trans_table = maketrans(replace, removed)
    hex_str = hex_str.lower().translate(trans_table)
    
    length = len(hex_str)

    # still really ugly.
    # Not really worth bringing in StupidParse or something else though.
    if length == 1:
        return hex_str*6
    elif length == 2:
        return hex_str*3
    elif length == 3:
        return (hex_str[0]*2) + (hex_str[1]*2) + (hex_str[3]*2)
    elif length > 3 and length < 6:
        return '{0:0<6}'.format(hex_str)
    else:
        return hex_str[0:6]

def hex_to_RGB(hex_str):
    '''Converts a hex color string to a RGB tuple

    For example: #FF0000 becomes (255,0,0)
    '''

    hex_str = correct_hex_color(hex_str)
    return tuple([int(hex_str[i:i+2], 16) for i in range(0,6,2)])

def RGB_to_hex(RGB):
    '''Accepts a RGB iterable (tuple or list most likely) 
    and returns a hex color string.

    For example: (255,0,0) becomes ff0000
    '''
    
    # Convert base 10 to base 16, left pad with 0 to 2 places
    return '{:0>2x}{:0>2x}{:0>2x}'.format(*RGB)

def calc_grad_diff(start, stop, distance):
    '''Calculates the start and stop gradient fills over a specific 
    distance.

    start and stop should be RGB tuples.
    '''

    return tuple((stop[x] - start[x])/distance for x in range(3))

def shift_RGB(start, stop, shift):
    '''Shifts an RGB tuple towards a new value.'''
    change = lambda x: (x[1]*shift)+(x[0])*shift)*(1-shift)
    return tuple(change(x) for x in zip(start, stop))

def get_flickr_image(api_key, tags):
    '''Not so simple function to grab a single image from flickr.'''

    # Mostly not so simple because the flickrapi module is a PITA

    flickr = FlickrAPI(api_key)

    rsp = flickr.photos_search(
                tags=tags,
                tag_mode='all',
                license='5,7',
                per_page=1
                )

    url = "http://farm{farm}.staticflickr.com/{server}/{id}_{secret}_b.jpg"

    if rsp.attrib['stat'] == 'ok':
        
        # wtf really?
        if len(rsp.getchildren()[0].getchildren()) == 1:
            photo = rsp.getchildren()[0][0]

            uri = urllib2.urlopen(url.format(**photo.attrib)

            # Store the whole thing in memory? Yuck.
            # Gotta remember to close it up when we're done.
            # TODO: FIX THIS!!!
            image = StringIO.StringIO(uri.read())
            image.seek(0)

            rsp = flickr.people_getInfo(user_id=photo.attrib['owner'])

            # Seriously, this is fucking retarded.
            # I had to figure this out in IPython 
            # because the flickrapi docs aren't very helpful.
            # Like not at all.
            owner = rsp.getchildren()[0].getchlidren()[0].text

            return owner, image

    return None

def load_fonts(font_path='fonts'):
    '''Grab all TrueType Fonts in the specified directory.
    Returns a dictionary.

    Example:
        fonts/ contains Liberationsans.ttf

        load_fonts will return:
            {'liberationsans':'fonts/Liberationsans.ttf'}
    '''
    
    fonts = glob(join(font_path, '*.ttf'))

    return {basename(font).lower().split('.')[0]:font for font in fonts}


# set color shifter
# shift_RGB is faster
shifter = shift_RGB
