import os
import re
import datetime
import argparse


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
    parser.add_argument("--predays",
                        action="store",
                        default=-1,
                        type=int,
                        metavar='pre',
                        help="Select the number of days to include before today")
    parser.add_argument("--postdays",
                        action="store",
                        default=1,
                        type=int,
                        metavar='post',
                        help="Select the number of days to include after today")
    parser.add_argument("--outfile",
                        action="store",
                        default="/Users/terrydrymonacos/Orgzly/today.md",
                        metavar='output',
                        help="location and name of output file")
    return parser

class OrgTodoParser():
    todoRegExpr = r'^\*\sTODO(?P<text>([a-zA-Z0-9\-]*\s){1,})(?P<tags>(\:[\w\-]*){0,})?'
    initRegExpr = r'^\*\sTODO\s.*'
    dateRegExpr = r'^SCHEDULED:\s<(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)\s(?P<dom>\w*)'

    def __init__(self, input_directory, predays, postdays, output_file):
        self.input_directory = input_directory
        self.predays = predays
        self.postdays = postdays
        self.output_file = output_file
        self.todo_list_toprint = None

    def parseTodo(self):
        init_expr = re.compile(self.initRegExpr)
        todo_expr = re.compile(self.todoRegExpr, re.MULTILINE)

        file_list = list(filter(lambda x: x.endswith('.org'), os.listdir(self.input_directory)))
        self.grab_todo(file_list, self.input_directory, init_expr, todo_expr)

    def grab_todo(self, file_list, file_directory, init_expr, todo_expr):
        self.todo_list_toprint = list()
        for elem in file_list:
            with open(file_directory + elem, 'r') as fh:
                lines = fh.readlines()
                for k, item in enumerate(lines):
                    todo_match = re.search(init_expr, item)
                    found = False
                    if todo_match:
                        found = True
                        matches = re.finditer(todo_expr, item)
                        our_tags = 0
                        for matchNum, theMatch in enumerate(matches):
                            for group_num in range(0, len(theMatch.groups())):
                                if group_num == 1:
                                    todo_message = theMatch.groupdict()['text'].strip('\n')
                                if group_num == 3:
                                    our_tags = theMatch.groupdict()['tags']
                            self.todo_list_toprint.append(dict({'todo_message': todo_message,
                                                                'tags': our_tags,
                                                                'date': ""
                                                                }
                                                               )
                                                          )
                    if found:
                        self.grab_date(k, lines)
        # process the list now and filter out the dates
        self.filter_date()

        # Print out our result array
        with open(self.output_file, "w") as fh:
            foo = [self.to_org_format(elem) for elem in self.todo_list_toprint]
            fh.writelines([self.to_org_format(elem) for elem in self.todo_list_toprint])

    def grab_date(self, k, lines):
        # let's see if the next record has our Scheduled Date
        date_expr = re.compile(self.dateRegExpr, re.MULTILINE)
        if k+1 < len(lines):
            date_line = re.search(date_expr, lines[k+1])
            if date_line:
                # transform into date
                this_date = datetime.date(int(date_line.groupdict()["year"]),
                                          int(date_line.groupdict()["month"]),
                                          int(date_line.groupdict()["day"])
                                          )
                self.todo_list_toprint[-1]['date'] = this_date


    def filter_date(self):
        for k in range(len(self.todo_list_toprint)-1, -1, -1):
            if self.todo_list_toprint[k]['date']:
                this_date = self.todo_list_toprint[k]['date']
                now = datetime.date.today()
                time_delta = this_date - now
                if not( time_delta.days <= self.postdays):
                #if not(-self.predays <= time_delta.days <= self.postdays):
                    del self.todo_list_toprint[k]
            else:
                del self.todo_list_toprint[k]

    def to_org_format(self, date_element):
        return " - [ ] #todo {}         <==<span class='cm-strong'>{}</span>\n".format(date_element['todo_message'], date_element['date'])


def main(input_directory, predays, postdays, output_file):
    a = OrgTodoParser(input_directory, predays, postdays, output_file)
    a.parseTodo()


if __name__ == "__main__":
    parser = create_argparser()
    parsed_args = parser.parse_args()
    main(parsed_args.srcdir,
         parsed_args.predays,
         parsed_args.postdays,
         parsed_args.outfile
         )

