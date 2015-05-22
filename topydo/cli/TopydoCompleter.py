# Topydo - A todo.txt client written in Python.
# Copyright (C) 2015 Bram Schoenmakers <me@bramschoenmakers.nl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import re

from prompt_toolkit.completion import Completer, Completion

from topydo.lib.Config import config
from topydo.Commands import _SUBCOMMAND_MAP
from topydo.lib.RelativeDate import relative_date_to_date

def _date_suggestions():
    """
    Returns a list of relative date that is presented to the user as auto
    complete suggestions.
    """
    # don't use strftime, prevent locales to kick in
    days_of_week = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }

    dates = [
        'today',
        'tomorrow',
    ]

    # show days of week up to next week
    dow = datetime.date.today().weekday()
    for i in range(dow + 2 % 7, dow + 7):
        dates.append(days_of_week[i % 7])

    # and some more relative days starting from next week
    dates += ["1w", "2w", "1m", "2m", "3m", "1y"]

    return dates

class TopydoCompleter(Completer):
    def __init__(self, p_todolist):
        self.todolist = p_todolist

    def _subcommands(self, p_word_before_cursor):
        subcommands = [sc for sc in sorted(_SUBCOMMAND_MAP.keys()) if sc.startswith(p_word_before_cursor)]
        for command in subcommands:
            yield Completion(command, -len(p_word_before_cursor))

    def _projects(self, p_word_before_cursor):
        projects = [p for p in self.todolist.projects() if p.startswith(p_word_before_cursor[1:])]

        for project in projects:
            yield Completion("+" + project, -len(p_word_before_cursor))

    def _contexts(self, p_word_before_cursor):
        contexts = [c for c in self.todolist.contexts() if c.startswith(p_word_before_cursor[1:])]

        for context in contexts:
            yield Completion("@" + context, -len(p_word_before_cursor))

    def _dates(self, p_word_before_cursor):
        to_absolute = lambda s: relative_date_to_date(s).isoformat()

        start_value_pos = p_word_before_cursor.find(':') + 1
        value = p_word_before_cursor[start_value_pos:]

        for reldate in _date_suggestions():
            if not reldate.startswith(value):
                continue

            yield Completion(reldate, -len(value), display_meta=to_absolute(reldate))

    def get_completions(self, p_document, p_complete_event):
        # include all characters except whitespaces (for + and @)
        word_before_cursor = p_document.get_word_before_cursor(True)
        is_first_word = not re.match(r'\s*\S+\s', p_document.current_line_before_cursor)

        if is_first_word:
            return self._subcommands(word_before_cursor)
        elif word_before_cursor.startswith('+'):
            return self._projects(word_before_cursor)
        elif word_before_cursor.startswith('@'):
            return self._contexts(word_before_cursor)
        elif word_before_cursor.startswith(config().tag_due() + ':'):
            return self._dates(word_before_cursor)
        elif word_before_cursor.startswith(config().tag_start() + ':'):
            return self._dates(word_before_cursor)

        return []
