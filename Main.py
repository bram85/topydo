#!/usr/bin/env python
""" Entry file for the Python todo.txt CLI. """

import re
import sys

import Config
import TodoFile
import TodoList

def print_iterable(p_iter):
    """ Prints an iterable to the standard output, one item per line. """
    for item in sorted(p_iter):
        print item

def usage():
    """ Prints the usage of the todo.txt CLI """
    pass

def error(p_message):
    """ Prints a message on the standard error. """
    sys.stderr.write(p_message + '\n')

class Application(object):
    def __init__(self):
        self.todolist = TodoList.TodoList([])
        self.dirty = False

    def add(self):
        """ Adds a todo item to the list. """
        if sys.argv[2]:
            self.todolist.add(sys.argv[2])
            self.dirty = True

    def append(self):
        """ Appends a text to a todo item. """

        number = sys.argv[2]
        text = sys.argv[3]

        if number and text:
            try:
                number = int(number)
                self.todolist.append(number, text)
                self.dirty = True
            except ValueError:
                error("Invalid todo number given.")

    def do(self):
        number = sys.argv[2]

        try:
            number = int(number)
            self.todolist.set_completed(number)
            self.dirty = True
        except ValueError:
            error("Invalid todo number given.")

    def pri(self):
        number = sys.argv[2]
        priority = sys.argv[3]

        if number and priority:
            if re.match('^[A-Z]$', priority):
                try:
                    number = int(number)
                    self.todolist.todo(number).set_priority(priority)
                    self.dirty = True
                except AttributeError:
                    error("Invalid todo number given.")
                except ValueError:
                    error("Invalid todo number given.")
            else:
                error("Invalid priority given.")

    def list(self):
        print self.todolist
        # TODO: sort + filter

    def run(self):
        """ Main entry function. """
        todofile = TodoFile.TodoFile(Config.FILENAME)

        try:
            self.todolist = TodoList.TodoList(todofile.read())
        except Exception:
            pass # TODO

        subcommand = Config.DEFAULT_ACTION
        if len(sys.argv):
            subcommand = sys.argv[1]

        if subcommand == 'add':
            self.add()
        elif subcommand == 'app' or subcommand == 'append':
            self.append()
        elif subcommand == 'do':
            self.do()
        elif subcommand == 'ls':
            self.list()
        elif subcommand == 'lsprj' or subcommand == 'listproj':
            print_iterable(self.todolist.projects())
        elif subcommand == 'lscon' or subcommand == 'listcon':
            print_iterable(self.todolist.contexts())
        elif subcommand == 'pri':
            self.pri()
        else:
            usage()

        if self.dirty:
            todofile.write(str(self.todolist))

if __name__ == '__main__':
    Application().run()
