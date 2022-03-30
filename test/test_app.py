import unittest
import os
import datetime
from unittest import mock

def return_todoy_offset(offset):
    time_delta = datetime.timedelta(days=offset)
    return(datetime.date.today()+time_delta).isoformat()


test_string = f"""
* TODO Yoga :home:
SCHEDULED: <{return_todoy_offset(0)} Tue .+1d>
:PROPERTIES:
:LAST_REPEAT: [2022-03-28 Mon 08:23]
:END:

Morning Greeting

* TODO Meditate :betterment:
SCHEDULED: <{return_todoy_offset(10)} Tue .+1d>
:PROPERTIES:
:LAST_REPEAT: [2022-03-28 Mon 08:23]
:END:

Morning  ritual, please

* TODO Metamucil :medical:
SCHEDULED: <{return_todoy_offset(-10)} Tue .+1d>
:PROPERTIES:
:LAST_REPEAT: [2022-03-28 Mon 06:59]
:END:
"""

from main import create_argparser, OrgTodoParser
import builtins


class OptionParser(unittest.TestCase):
    """ Unit test for the argument parsing"""
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


class TodoParser(unittest.TestCase):
    """ Unit test for the file parsing"""

    def test_constructor_init(self):
        input_dir = "/home/someone/"
        postdays = 2
        output_file = "/home/orgzly/"
        todo_parser = OrgTodoParser(input_dir, postdays, output_file)
        self.assertEqual(todo_parser.input_dir, input_dir)
        self.assertEqual(todo_parser.postdays, postdays)
        self.assertEqual(todo_parser.output_file, output_file)

    def test_org_format(self):
        input_dir = "/home/someone/"
        postdays = 2
        output_file = "/home/orgzly/"

        test_date_element = {'todo_message': "do this",
                             'date': "2022-03-14"
                             }
        todo_parser = OrgTodoParser(input_dir, postdays, output_file)
        self.assertEqual(todo_parser.to_org_format(test_date_element),
                         " - [ ] #todo do this  <span class='cm-strong'>2022-03-14</span>\n")

    def test_filter_dates(self):
        todo_parser = OrgTodoParser("", 0, "")
        the_past = datetime.timedelta(days=-100)
        the_future = datetime.timedelta(days=100)
        todo_parser.list_to_print = [
            {
                'todo_message': "do this yesterday",
                'date': datetime.date.today() + the_past
            },
            {
                'todo_message': "this is not scheduled",
                'date': ''
            },
            {
                'todo_message': "do this today",
                'date': datetime.date.today()
            },
            {
                'todo_message': "do this in the future",
                'date': datetime.date.today() + the_future
            },
        ]
        todo_parser.filter_dates()
        self.assertEqual(len(todo_parser.list_to_print), 2)

    def test_filter_dates_future(self):
        todo_parser = OrgTodoParser("", 0, "")
        the_future = datetime.timedelta(days=100)
        the_penultimate = datetime.timedelta(days=200)
        the_infinity = datetime.timedelta(days=300)
        todo_parser.list_to_print = [
            {
                'todo_message': "do this in a 100 days",
                'date': datetime.date.today() + the_future
            },
            {
                'todo_message': "do this in 200 days",
                'date': datetime.date.today() + the_penultimate
            },
            {
                'todo_message': "this is not scheduled",
                'date': ''
            },
            {
                'todo_message': "do this in 300 days ",
                'date': datetime.date.today() + the_infinity
            },
        ]
        todo_parser.filter_dates()
        self.assertEqual(len(todo_parser.list_to_print), 0)

    def test_filter_dates_only_today(self):
        todo_parser = OrgTodoParser("", 0, "")
        the_penultimate = datetime.timedelta(days=200)
        the_infinity = datetime.timedelta(days=300)
        todo_parser.list_to_print = [
            {
                'todo_message': "do this today",
                'date': datetime.date.today()
            },
            {
                'todo_message': "this is not scheduled",
                'date': ''
            },
            {
                'todo_message': "do this in 200 days",
                'date': datetime.date.today() + the_penultimate
            },
            {
                'todo_message': "do this in 300 days ",
                'date': datetime.date.today() + the_infinity
            },
        ]
        todo_parser.filter_dates()
        self.assertEqual(len(todo_parser.list_to_print), 1)

    # def test_prepare_parsing(self):
    #     os.listdir = Mock()
    #     OrgTodoParser.process_todo = Mock()
    #     os.listdir.return_value = ['a.org', 'file.foo', 'file2.org']
    #     OrgTodoParser.process_todo.return_value = None
    #
    #     todo_parser = OrgTodoParser("", 0, "")
    #     todo_parser.prepare_parsing()
    #
    #     self.assertEqual(len(todo_parser.file_list), 2)

    # @unittest.mock.patch('builtins.open')
    @mock.patch.object(builtins, 'open', new_callable=mock.mock_open, read_data=test_string)
    def testFileRead(self, mock_open):
        list_of_files = ['a.org']

        todo_parser = OrgTodoParser("", 0, "")
        todo_parser.process_todo(list_of_files, '/home/terryd/')
        pass
