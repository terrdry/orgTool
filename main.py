import os
import re
import datetime
import argparse


class OrgError(OSError):
    pass



def create_argparser():
    """
    Create the argument parser and return the object that has access to the parameters
    :return: parser object
    """
    parser = argparse.ArgumentParser(description="Orgzly to Obsidian Markup")
    parser.add_argument("--srcdir",
                        action="store",
                        default="/Users/terrydrymonacos/Orgzly/",
                        metavar="source_directory",
                        help="Directory containing the Orgzly files")
    parser.add_argument("--postdays",
                        action="store",
                        default=0,
                        type=int,
                        metavar='post',
                        help="Select the number of days to include after today")
    parser.add_argument("--outfile",
                        action="store",
                        default="/Users/terrydrymonacos/Orgzly/today.md",
                        metavar='output',
                        help="location and name of output file")
    return parser


class OrgTodoParser:
    """
    Class that is responsible for reading a directory of files and processing the lines in this org
    :return: parser object
    """
    todoRegExpr = r'^\*\sTODO(?P<text>([a-zA-Z0-9\-]*\s){1,})(?P<tags>(\:[\w\-]*){0,})?'
    initRegExpr = r'^\*\sTODO\s.*'
    dateRegExpr = r'^SCHEDULED:\s<(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)\s(?P<dom>\w*)'

    def __init__(self, input_dir, postdays, output_file):
        """
        Initializaton constructor
        """
        self.input_dir = input_dir
        self.postdays = postdays
        self.output_file = output_file
        self.list_to_print = list()
        self.file_list = list()
        self.regex_init = re.compile(self.initRegExpr)
        self.regex_todo = re.compile(self.todoRegExpr, re.MULTILINE)

    def prepare_parsing(self):
        """
        Read files to be processed and feed them to process_todo()
        """
        self.file_list = list(filter(lambda x: x.endswith('.org'), os.listdir(self.input_dir)))
        self.process_todo(self.file_list, self.input_dir)

    def process_todo(self, file_list, file_directory):
        """
        Read individual files and filter their dates and print
        results to file
        """
        for elem in file_list:
            with open(file_directory + elem, 'r') as fh:
                self.read_file(fh)

        # process the list now and filter out the dates
        self.filter_dates()

        # Print out our result array
        self.print_to_file()

    def print_to_file(self):
        """
        Print the results to file
        """
        with open(self.output_file, "w") as fh:
            fh.writelines([self.to_org_format(elem) for elem in self.list_to_print])

    def read_file(self, fh):
        """
        Read the individual line and search for the TODO regex
        """
        lines = fh.readlines()
        if not len(lines):
            raise OrgError(12, f'file {fh.name} is empty')
        for k, item in enumerate(lines):
            todo_match = re.search(self.regex_init, item)
            found = False
            if todo_match:
                found = True
                todo_message = ""
                matches = re.finditer(self.regex_todo, item)
                our_tags = 0
                for matchNum, theMatch in enumerate(matches):
                    for group_num in range(0, len(theMatch.groups())):
                        if group_num == 1:
                            todo_message = theMatch.groupdict()['text'].strip('\n')
                        if group_num == 3:
                            our_tags = theMatch.groupdict()['tags']
                    self.list_to_print.append(dict({'todo_message': todo_message,
                                                    'tags': our_tags,
                                                    'date': ""
                                                    }
                                                   )
                                              )
            if found:
                self.grab_date(k, lines)

    def grab_date(self, k, lines):
        """
        Check to see that the next line may have a scheduled date
        If it is found, the date is stored to the array list_to_print
        """
        date_expr = re.compile(self.dateRegExpr, re.MULTILINE)
        if k+1 < len(lines):
            date_line = re.search(date_expr, lines[k+1])
            if date_line:
                # transform into date
                this_date = datetime.date(int(date_line.groupdict()["year"]),
                                          int(date_line.groupdict()["month"]),
                                          int(date_line.groupdict()["day"])
                                          )
                self.list_to_print[-1]['date'] = this_date

    def filter_dates(self):
        """
        filter out any dates that are in the future of today()
        """
        for k in range(len(self.list_to_print) - 1, -1, -1):
            if self.list_to_print[k]['date']:
                this_date = self.list_to_print[k]['date']
                now = datetime.date.today()
                time_delta = this_date - now
                if not(time_delta.days <= self.postdays):
                    del self.list_to_print[k]
            else:
                del self.list_to_print[k]

    def to_org_format(self, date_element):
        """
        Format the output to conform to Obsidian's HTML elements
        """
        return " - [ ] #todo {}  <span class='cm-strong'>{}</span>\n".format(date_element['todo_message'],
                                                                             date_element['date']
                                                                             )


def main(input_directory, postdays, output_file):

    """
    main function
    """
    a = OrgTodoParser(input_directory, postdays, output_file)
    a.prepare_parsing()


if __name__ == "__main__":
    parsed_line = create_argparser()
    parsed_args = parsed_line.parse_args()
    main(parsed_args.srcdir,
         parsed_args.postdays,
         parsed_args.outfile
         )
