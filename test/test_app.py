import unittest
from main import create_argparser

class OptionParser(unittest.TestCase):
    srcdir = "/home/terryd/todofiles/"
    postdays = 0
    outfile = '/home/terryd/orgzly/today.md'

    def test_normal_args(self):
        arg_string = '--srcdir %s --postdays %d --outfile %s' % \
                     (self.srcdir, self.postdays, self.outfile)
        arg_string = arg_string.split()

        parser = create_argparser()
        parsed_result = parser.parse_args(arg_string)
        self.assertEqual(parsed_result.srcdir, self.srcdir)
        self.assertEqual(parsed_result.postdays, self.postdays)
        self.assertEqual(parsed_result.outfile, self.outfile)

    def test_no_args(self):
        parser = create_argparser()
        parsed_result = parser.parse_args()

        self.assertEqual(parsed_result.srcdir, '/Users/terrydrymonacos/Orgzly/')
        self.assertEqual(parsed_result.postdays, 0)
        self.assertEqual(parsed_result.outfile, '/Users/terrydrymonacos/Orgzly/today.md')



