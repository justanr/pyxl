try:
    import unittest
except:
    import unittest2 as unittest

from hashlib import md5

from pyxl import Pyxl, hexToRGB, RGBToHex, buildHex, buildPyxlName

class PyxlTestCase(unittest.TestCase):
    def setUp(self):
        self.gradient = Pyxl('gradient:ffffff,000000', '300x300', None)
        self.solid    = Pyxl('color:ffffff', '300x300', None)
        self.flickr   = Pyxl('farm,animal', '300x300', None)

    def tearDown(self):
        self.gradient = None
        self.solid    = None
        self.flickr   = None

    def testBuildHex(self):
        self.assertEqual('ffffff', buildHex('f'))
        self.assertEqual('ffffff', buildHex('ff'))
        self.assertEqual('ffffff', buildHex('fff'))
        self.assertEqual('ffff00', buildHex('ffff'))
        self.assertEqual('ffffff', buildHex('fffffff'))
        self.assertEqual('ffffff', buildHex('#ffffff'))
        self.assertEqual('ffffff', buildHex('ffffff '))
    
    def testHexToRGB(self):
        self.assertTupleEqual((255,255,255), hexToRGB('ffffff'))
    
    def testRGBToHex(self):
        self.assertEqual('ffffff', RGBToHex((255,255,255)))
    
    def testPyxlSetInfo(self):
        self.assertDictEqual(
            {'type':'gradient', 'colors':[(255,255,255), (0,0,0)]},
            self.gradient.info
            )

        self.assertDictEqual(
            {'type':'flickr', 'tags':['farm', 'animal']},
            self.flickr.info
            )

        self.assertDictEqual(
            {'type':'color', 'colors':[(255,255,255)]},
            self.solid.info
            )

        hgradient = Pyxl('gradient:fff,000,h', '300', None)

        self.assertDictEqual(
            {'type':'hgradient', 'colors':[(255,255,255), (0,0,0)]},
            hgradient.info
            )

    def testPyxlGetInfo(self):
        self.assertEqual('gradient:ffffff,000000', self.gradient.getInfo())
        self.assertEqual('color:ffffff', self.solid.getInfo())
        self.assertEqual('farm,animal', self.flickr.getInfo())
    
    def testPyxlSetSize(self):
        self.assertTupleEqual( (300,300), self.solid.size)
        
        one_size = Pyxl('tag', '400', None)
        self.assertTupleEqual((400,400), one_size.size)

        poorly_formed = Pyxl('tag', 'ax400', None)
        self.assertTupleEqual( (200, 400), poorly_formed.size)

    def testPyxlGetSize(self):
        self.assertEqual('300x300', self.gradient.getSize())

        test = Pyxl('tag', '400', None)
        self.assertEqual('400x400', test.getSize())

        poorly_formed = Pyxl('tag', 'ax400', None)
        self.assertEqual('200x400', poorly_formed.getSize())
    
    def testPyxlSetOptions(self):
        default_options = {'font':'fonts/LiberationSans.ttf', 'text':(255,255,255)}

        self.assertDictEqual(default_options, self.solid.options)

        poorly_formed = Pyxl('tag', '300', 'poorly:formed')
        self.assertDictEqual(default_options, poorly_formed.options)

        all_options = {
                        'font':'fonts/LiberationSans.ttf', 'text':(255,255,255),
                        'seed':'5', 'dimensions':'hide'
                      }
        all_options_Pyxl = Pyxl('tag', '300', 'font:liberationsans,text:fff,seed:5,dimensions:hide')
        self.assertDictEqual(all_options, all_options_Pyxl.options)

    def testPyxlGetOptions(self):
        self.assertEqual('font:liberationsans,text:ffffff', self.gradient.getOptions())

        poorly_formed = Pyxl('tag', '300', 'poorly:formed,seed:5')
        self.assertEqual('font:liberationsans,seed:5,text:ffffff', poorly_formed.getOptions())

        all_options = Pyxl('tag', '300', 'seed:5,font:liberationsans,text:555,dimensions:off')
        self.assertEquals('dimensions:hide,font:liberationsans,seed:5,text:555555', all_options.getOptions())

    def testPyxlLoadFonts(self):
        fonts = {'liberationsans':'fonts/LiberationSans.ttf'}

        self.assertDictEqual(fonts, self.solid.fonts)

    def testPyxlSetFont(self):
        font = 'fonts/LiberationSans.ttf'

        self.assertEqual(font, self.solid.options['font'])

        self.solid.setFont('nope')
        self.assertEqual(font, self.solid.options['font'])

    def testBuildPyxlName(self):
        
        name = md5('{}-{}-{}'.format('color:ffffff', '300x300', 'font:liberationsans,text:ffffff')).hexdigest() + '.jpg'

        self.assertEqual(name, buildPyxlName(self.solid))

if __name__ == '__main__':
    unittest.main()
