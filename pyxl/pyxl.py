'''Pyxl module for creating simple images based on basic inputS'''

import helper

class Pyxl(object):
    
    __VALID_OPTIONS = ('seed', 'dimensions', 'text', 'font')
    __VALID_TYPES = ('gradient', 'h-gradient', 'solid', 'flickr')
    __DEFAULTS = {
                 'font':'liberationsans',
                 'colors':[(255,255,255), (0,0,0)]
                 }

    # Seriously, who the fuck needs an image this big?
    __MAX_SIZE = 2500

    def __init__(self, type, info, size, options=None, font_path='fonts'):
        self.type = type
        self.info = info
        self.size = size
        self.options = options
        
        self._font_path = font_path

        # Callback function set after configuring the object
        self.draw = None

    def __repr__(self):
        pass

    def __str__(self):
        '''Convert drawn image to Base64 for easy transport.
        '''
        # TODO: What happens when there isn't an image drawn yet?
        pass

    def _set_info(self, info):
        pass

    def _set_options(self, options):
        pass

    def _set_size(self, size):
        pass

    def _set_type(self, type):
        pass

    def _draw_solid(self):
        pass

    def _draw_gradient(self):
        pass

    def _draw_flickr(self):
        pass

    def _draw_dimensions(self):
        pass

