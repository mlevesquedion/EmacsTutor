import random
from functools import wraps
from tkinter import *
from _tkinter import TclError


class EmacsTutor(Tk):

    def __init__(self):
        super().__init__()

        self.title('EmacsTutor')
        self.wm_iconbitmap('emacs.ico')

        self.text = Text(self)
        self.text.pack()

        self.text.insert(END, open('sample_text.txt').read())

        BINDINGS = {
            '<Control-f>': self.forward,
            '<Control-b>': self.backward,
            '<Control-n>': self.next_line,
            '<Control-p>': self.prev_line,
            '<Control-a>': self.line_start,
            '<Control-e>': self.line_end,
            '<Alt-greater>': self.end,
            '<Alt-less>': self.start,
            '<Alt-e>': self.next_sentence,
            '<Alt-a>': self.prev_sentence,
            '<Alt-f>': self.next_word,
            '<Alt-b>': self.prev_word
        }
        for keys, func in BINDINGS.items():
            self.text.bind(keys, self.update_after(func))

        self.func_to_bind = {v: k for k, v in BINDINGS.items()}

        self.text.tag_add('target', '1.0')
        self.text.tag_config('target', background='yellow')

        self.text.focus()

    def get_target_index(self):
        return self.text.tag_ranges('target')[0]

    def update(self):
        if self.get_target_index().string == self.get_cursor_index():
            self.text.tag_delete('target', '1.0')
            max_line = int(self.text.index('end').split('.')[0])
            new_line = random.randint(1, max_line- 1)
            max_col = int(self.text.index('{}.0 lineend'.format(new_line)).split('.')[0])
            new_col = random.randint(0, max_col)
            self.text.tag_add('target', '{}.{}'.format(new_line, new_col))
            self.text.tag_config('target', background='yellow')

    def update_after(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func()
            self.update()
            keys = self.func_to_bind[func]
            self.command_count[keys] += 1
            self.times.append(self.timer.tick())
            return "break"  # Override any existing binding
        return wrapper

    def get_cursor_index(self):
        return self.text.index('insert')

    def get_cursor_position(self):
        return self.get_cursor_index().split('.')

    def get_cursor_line(self):
        return self.get_cursor_position()[0]

    def get_cursor_col(self):
        return self.get_cursor_position()[1]

    def set_cursor_position(self, pos):
        line, col = pos
        if line is None:
            line = self.get_cursor_line()
        if col is None:
            col = self.get_cursor_col()
        self.text.mark_set('insert', '{}.{}'.format(line, col))

    def forward(self, event=None):
        col = self.get_cursor_col()
        col = int(col) + 1
        if self.text.index('insert') == self.text.index('end'):
            return
        next_newline = self.text.search('\n', 'insert')
        if next_newline == self.text.index('insert'):
            line = int(self.get_cursor_line())
            self.text.mark_set('insert', '{}.0'.format(line + 1))
            return
        self.set_cursor_position((None, col))

    def backward(self, event=None):
        col = self.get_cursor_col()
        col = int(col) - 1
        if col == -1:
            line = self.get_cursor_line()
            self.text.mark_set('insert', '{}.0'.format(int(line)-1))
            next_newline = self.text.search('\n', 'insert')
            line, col = next_newline.split('.')
            self.text.mark_set('insert', '{}.{}'.format(line, int(col) - 1))
        self.set_cursor_position((None, col))

    def next_line(self, event=None):
        line = self.get_cursor_line()
        line = int(line) + 1
        self.set_cursor_position((line, None))

    def prev_line(self, event=None):
        line = self.get_cursor_line()
        line = int(line) - 1
        self.set_cursor_position((line, None))

    def line_start(self, event=None):
        line = self.get_cursor_line()
        self.text.mark_set('insert', '{}.0'.format(line))

    def line_end(self, event=None):
        line = self.get_cursor_line()
        self.text.mark_set('insert', '{}.0 lineend'.format(line))

    def start(self, event=None):
        self.text.mark_set('insert', '1.0')

    def end(self, event=None):
        self.text.mark_set('insert', 'end')

    def next_sentence(self):
        pos = self.text.search('.', 'insert', stopindex='end')
        try:
            self.text.mark_set('insert', pos + '+1c')
        except TclError:
            self.text.mark_set('insert', 'end')

    def prev_sentence(self):
        pos = self.text.search('.', '1.0', stopindex='insert')
        if not pos:
            self.text.mark_set('insert', '1.0')
            return
        else:
            c = 1
            while pos:
                valid_pos = pos
                pos = self.text.search('.', '1.0+{}c'.format(c), stopindex='insert')
                c += 1
        self.text.mark_set('insert', valid_pos)

    def next_word(self):
        pos = self.text.search('\s', 'insert', stopindex='end', regexp=True)
        try:
            self.text.mark_set('insert', pos + '+1c')
        except TclError:
            self.text.mark_set('insert', 'end')

    def prev_word(self):
        pos = self.text.search(' ', '1.0', stopindex='insert')
        if not pos:
            self.text.mark_set('insert', '1.0')
            return
        else:
            c = 1
            while pos:
                valid_pos = pos
                pos = self.text.search('\s', '1.0+{}c'.format(c), stopindex='insert', regexp=True)
                c += 1
        self.text.mark_set('insert', valid_pos)


if __name__ == '__main__':
    EmacsTutor().mainloop()
