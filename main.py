import os
import re

class OrgTodoParser():
    def __init__(self):
        pass
    pass

    def doit(self):

        # if (re.search('^\* TODO.*', item)):))

        fileDirectory = '/Users/terrydrymonacos/org-test/'
        fileList = os.listdir(fileDirectory)
        todoExpr = re.compile(r'^\*\sTODO\s(?P<text>(\w*\s){1,})(?P<tags>:(\w*.){0,})')


        fileList = list(filter( lambda x: x.endswith('.org'),os.listdir(fileDirectory)))
        for elem in fileList:
            with open(fileDirectory+elem, 'r') as fh:
                lines = fh.readlines()
                for item in lines:
                    if (re.search(todoExpr,item)):
                        foundObj = re.match(todoExpr, item)
                        todoMessage = foundObj.groupdict()['text']
                        ourTags = foundObj.groupdict()['tags']
                        print( ' Message: {} Tags: {}'.format(todoMessage,ourTags))


        print("hello")


def main():
    a = OrgTodoParser()
    a.doit()

if __name__ == "__main__":
    main()

