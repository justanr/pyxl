'''
This simple module consists of the Pyxl class and a few helper functions.
'''

from os.path import basename, join
from glob import glob

try:
    import Image, ImageDraw, ImageFont, ImageFile
except ImportError:
    from PIL import Image, ImageDraw, ImageFont, ImageFile

#Helper functions.

def buildHex(hexStr):
    '''
    Accepts a supposed hex color string and ensures it's 6 characters long.
    '''
    hexStr = hexStr.lower().replace(' ','').replace('#','')

    #TODO: Make this prettier.
    if len(hexStr) == 1:
        return hexStr * 6
    elif len(hexStr) == 2:
        return hexStr * 3
    elif len(hexStr) == 3:
        return (hexStr[0] * 2) + (hexStr[1] * 2) + (hexStr[2] * 2)
    elif len(hexStr) > 3 and len(hexStr) < 6:
        return '{0:0<6}'.format(hexStr)
    elif len(hexStr) > 6:
        return hexStr[0:6]
    else:
        return hexStr

def hexToRGB(hexStr):
    '''Converts a hexStr color to a RGB tuple'''
    
    # Pretty self explainatory, but as a note this converts 
    # each hex pair (base16) to a base10 value
    # hexToRGB('ff0000') would return (255, 0, 0) or pure red
    
    hexStr = buildHex(hexStr)
    return tuple([int(hexStr[i:i+2], 16) for i in range(0, 6, 2)])

def RGBToHex(RGB):
    '''Converts a RGB tuple into a hex color'''
    #TODO: Convert to new style formatting
    return '%02x%02x%02x' % RGB


def calcGradDiff(startFill, stopFill, distance):
    '''
    Calculates the difference between the start and 
    stop fills over the specified distance.
    '''
    
    # account for the last pixel
    distance = distance - 1.0

    return tuple((stopFill[x] - startFill[x])/distance for x in range(3))

def buildPyxlName(pyxl, hasher=None):
    '''
    Builds a name from Pyxl.getInfo, Pyxl.getSize and Pyxl.getOptions.
    Optionally, it can be hashed by passing a function that has the 
    hexdigest method.
    '''
    
    name = '{}-{}-{}'.format(pyxl.getInfo(), pyxl.getSize(), pyxl.getOptions())

    if hasher is not None:
        name = hasher(name).hexdigest()

    return name+".jpg"


def savePyxlImage(pyxl, **kwargs):
    '''
    A simple save function for pyxl. Consider replacing with your own.
    '''

    path = kwargs.get('path', 'imgs')
    hasher = kwargs.get('hasher', None)

    ImageFile.MAXBLOCK = pyxl.image.size[0] * pyxl.image.size[1]

    fullpath = join(path, buildPyxlName(pyxl, hasher))

    pyxl.image.save(fullpath, 'JPEG')

def shiftRGB(old, new, shift):
    '''
    Shifts an RGB towards a new value.

    Shift can be anything that returns an integer or float.
    '''

    change = lambda x: (x[1]*shift)+(x[0]*(1-shift))

    return tuple(change(x) for x in zip(old, new))

def smartShape(oldsize, newsize):
    '''
    Intelligently shape an  image.
    WIP.
    '''
    
    # determine ratios 
    rx = oldsize[0]/float(newsize[0])
    ry = oldsize[1]/float(newsize[1])

    # get the smaller ratio
    r = rx if rx < ry else ry

    # where do we crop at?
    cropx = newsize[0] * r
    dx = (oldsize[0] - cropx)/2

    cropy = newsize[1] * r
    dy = (oldsize[1] - cropy)/2

    # return the crop box
    return dx, dy, cropx+dx, cropy+dy

class Pyxl(object):
    '''
    This class builds an image based on a series of inputs. 
    
    Either constructing it solely in PIL or pulling one from flickr.
    '''

    #TODO: Better documentation.

    def __init__(self, info, size, options=None, fonts='fonts'):
        
        # Initializing some very key variables.
        self.info    = {}
        self.size    = ()
        self.options = {}
        self.fonts   = {}
        self.draw    = None
        self.image   = None
    
        self.defaults = {
                        'font':'liberationsans', 
                        'colors':[hexToRGB('ffffff'), hexToRGB('ff0000')]
                        }
        
        # Build the fonts dictionary.
        self.loadFonts(fonts)

        # Load all the arguments passed to Pyxl
        self.setInfo(info)
        self.setSize(size)
        self.setOptions(options)

    def setInfo(self, info):
        '''
        This function sets the information Pyxl needs to start an image.

        It accepts one of three string patterns:
        tag or a series of tags delimited by a comma 
        -- In this case, it is a flickr image 
            OR
        color:hex 
        -- A solid color image
            OR
        gradient:hex,hex 
        -- A gradient image, there is an optional h argument at the end

        The info variable contains the following bits:
        type: This tells Pyxl what sort of image to produce
        tags: This key is only set for a flickr image, 
            it determines what tags to pull an image from.
        color: A list of RGB tuples.
        '''
        
        # Determine which kind of image we want
        # No colon found, we want to contact flickr
        if info.find(':') == -1:
            self.info['type'] = 'flickr'
            self.info['tags'] = sorted(info.split(','))
            self.draw = self.drawFlickr
        
        # We are building an image with PIL
        else:
            info = info.split(':')

            # We're drawing a gradient.
            if info[1].find(',') != -1:
                self.draw = self.drawGradient
                self.info['type'] = 'gradient'
                
                info[1] = info[1].split(',')
                
                self.info['colors'] = [ hexToRGB(info[1][0]),
                                        hexToRGB(info[1][1])
                                      ]
                
                # Specifically, a horizontal gradient
                if len(info[1]) == 3:
                    self.info['type'] = 'hgradient'

            # Just a solid image please
            else:
                self.draw = self.drawColor
                self.info['type'] = 'color'
                self.info['colors'] = [hexToRGB(info[1])]

    
    def getInfo(self):
        '''Returns a string representation of info dictionary.'''

        if self.info['type'] == 'flickr':
            return ','.join(self.info['tags'])
        elif self.info['type'] == 'color':
            return 'color:{}'.format(RGBToHex(self.info['colors'][0]))
        else:
            colors =  ','.join([RGBToHex(x) for x in self.info['colors']])

            if self.info['type'] == 'hgradient':
                colors = colors + ',h'

            return 'gradient:{}'.format(colors)

    def setSize(self, size):
        '''
        Sets the total size of the image. 
        
        This function accepts a string in the form of widthxheight.
        This function will also ensure that the dimensions are between 1 
        and the maximum (currently 2500)
        '''
         
        default = 200
        maximum = 2000
        # seriously, who needs an image this big
        
        sizes = []

        for x in size.split('x'):
            
            try:
            # Probably a better way to do this, but no point in letting this
            # ruin the script Even though I highly doubt someone will 
            # pass something like axd as the size argument from the API, 
            # better safe than sorry.

                x = int(x)
            except ValueError:
                x = default
            
            if x > maximum:
                x = maximum
            elif x < 1:
                x = default

            sizes.append(x)

        if len(sizes) != 2:
            sizes = [sizes[0], sizes[0]]

        self.size = tuple(sizes)
                

    def getSize(self):
        '''
        Returns string representation of the iamge size in 
        form of widthxheight
        '''
        return 'x'.join([str(x) for x in self.size])

    def setOptions(self, options):
        '''
        This function accepts a string for the options of Pyxl. 
        It should be formatted as: option:value,option2:value.

        There are just a few current valid options:
        seed: This option is to create a new image from the same options.
        
        text: A hex color that is converted to a RGB tuple.
        
        dimensions: This SHOULD be set to hide, 
        but if it's there, the dimensions are not displayed on the image.
        
        font: This sets the font for the image text, 
        it uses a defaults if the font isn't listed in Pyxl.fonts
        '''

        if options is None:
            #defaults ahoy!
            self.options = {
                    'text':self.defaults['colors'][0],
                    'font':self.setFont(self.defaults['font'])
                    }
        else:
            valid = ['seed', 'dimensions', 'text', 'font']
            for option in options.lower().split(','):
                option = option.split(':')
                
                #prevent a bunch of spamming non-recognized options
                if option[0] not in valid:
                    continue
        
                elif option[0] == 'font':
                    option[1] = self.setFont(option[1])
        
                elif option[0] == 'text':
                    try:
                    # again, probably a better way
                    # but better safe than sorry
        
                        option[1] = hexToRGB(option[1])
                    except ValueError:
                        option[1] = self.defaults['colors'][0]        
                elif option[0] == 'dimensions':
                    option[1] = 'hide'

                elif option[0] == 'seed' and self.info['type'] != 'flickr':
                    # There's no point in a seed for a none flickr image
                    continue
                
                self.options[option[0]] =  option[1]
        
        #double check to make sure at least font and text got set.
        if 'font' not in self.options:
            self.options['font'] = self.setFont(self.defaults['font'])

        if 'text' not in self.options:
            self.options['text'] = self.defaults['colors'][0]

    def getOptions(self):
        '''Returns a string representation of all the options set.'''
        options = ''

        for key in sorted(self.options.keys()):
            if key == 'text':
                option = RGBToHex(self.options['text'])
            elif key == 'font':
                option = basename(self.options['font']).lower().split('.')[0]
            else:
                option = self.options[key]

            options = options + '{}:{},'.format(key, option)

        return options.rstrip(',')
    
    def loadFonts(self, location='fonts'):
        '''
        This function scans the location folder for fonts and stores them in a
        dictionary. The keys are the lowercased version of the file name, 
        split at the first dot.
        
        LiberationSans.ttf becomes 
        {'liberationsans':'fonts/LiberationSans.ttf'}
        
        Currently, it is only implemented to find TrueType fonts.
        '''

        fonts = glob(join(location, '*.ttf'))
        
        self.fonts = {
            basename(font).lower().split('.')[0]:font for font in fonts
            }
    
    def setFont(self, font):
        '''
        This function sets the font for the text on the image.
        If it receives a font that isn't in Pyxl's font library, 
        it sets it to the default.
        '''
        if font not in self.fonts.keys():
            return self.fonts[self.defaults['font']]

        return self.fonts[font]
        
    def drawColor(self):
        '''Creates a solid colored image.'''
        self.image = Image.new('RGB', self.size, self.info['colors'][0])
        
        if 'dimensions' not in self.options:
            self.drawDimensions()

    def drawGradient(self):
        '''Creates a gradient image.'''
        
        # this'll be much easier to work with
        height = self.size[1]
        width = self.size[0]
        
        # set the correct distance
        distance = width if self.info['type'] == 'hgradient' else height

        # again, easier to work with
        start, stop  = self.info['colors']
       
        # make a new blank image
        self.image = Image.new('RGB', self.size, hexToRGB('ffffff'))
        draw = ImageDraw.Draw(self.image)

        
        for i in range(distance):
            # set the correct draw positions
            if self.info['type'] == 'hgradient':
                pos = (i, 0, i, height)
            else:
                pos = (0, i, width, i)
 
            # move the start color closer to the end color
            rgb = shiftRGB(start, stop, float(i)/distance)
            fill = tuple([int(round(x)) for x in rgb])

            draw.line(pos, fill=fill)
            
        if 'dimensions' not in self.options:
            self.drawDimensions()

    def drawFlickr(self):
        '''Creates an image based on a flickr image.'''
        self.getFlickrImage()

        size = 10
        font = ImageFont.truetype(self.options['font'], size)

        text = 'Copyright {}.'.format(self.info['user'])

        pos = ( (self.size[0] - font.getsize(text))/2,
                (self.size[1] - 2)
              )

        draw = ImageDraw.Draw(self.image)
        draw.text(pos, text, font=font, fill=self.options['text'])

        if 'dimensions' not in self.options:
            self.drawDimensions()

    def getFlickrImage(self):
        '''
        Retrieves a single flickr image based on Pyxl.info['tags']
        '''
        
        # lazy import like a boss
        # these are aren't needed for any other part of the script
        # so we'll just import them here.
        import json, urllib2, StringIO, flickrapi

        with open('flickrapi.json') as f:
            key = json.loads(f.read())

        flickr = flickrapi.FlickrAPI(key['api_key'])

        rsp = flickr.photos_search(
                tags=self.info['tags'], tag_mode='all',
                license='5,7', per_page=1)
        
        # TODO: add what happens if the request isn't good or there aren't kids.
        if rsp.attrib['stat'] == 'ok':
            if len(rsp.getchildren()[0].getchildren()) == 1:
                photo = rsp.getchildren()[0][0]

                url = "http://farm{farm}.staticflickr.com/{server}/{id}_{secret}_b.jpg"

                uri = urllib2.urlopen(url.format(**photo.attrib))
                self.uri = StringIO.StringIO(uri.read())

                self.uri.seek(0)

                self.image = Image.open(self.uri)

                rsp = flickr.people_getInfo(user_id=photo.attrib['owner'])
                person = rsp.getchildren()[0]

                # username, finally
                self.info['user'] = person.getchildren()[0].text

    def drawDimensions(self):
        '''Creates the dimensions image.'''

        text = self.getSize()
        size = 1

        font = ImageFont.truetype(self.options['font'], size)

        img_fraction = 0.5

        while (font.getsize(text)[0] < int(self.size[0] * img_fraction)) and \
            (font.getsize(text)[1] < int(self.size[1]*img_fraction)):
            
            font = ImageFont.truetype(self.options['font'], size)
            size += 1

        pos = ( (self.size[0] - font.getsize(text)[0])/2,
                (self.size[1] - font.getsize(text)[1])/2
              )

        draw = ImageDraw.Draw(self.image)
        draw.text(pos, text, font=font, fill=self.options['text'])
