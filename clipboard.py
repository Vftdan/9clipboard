#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from subprocess import Popen, PIPE, DEVNULL

XCLIP = '/usr/bin/xclip'

class Clipboard():

    def __init__(self, selection='primary'):
        self.selection = selection
        self.size_target = None

    def read(self, target=None):
        if target is not None:
            target = target.replace(' ', '/')
            proc = Popen([XCLIP, '-selection', self.selection, '-t', target, '-o',],  stdout=PIPE, stderr=DEVNULL)
        else:
            proc = Popen([XCLIP, '-selection', self.selection, '-o',],  stdout=PIPE, stderr=DEVNULL)
        return proc.stdout.read()

    def write(self, contents, target=None):
        if target is not None:
            target = target.replace(' ', '/')
            proc = Popen([XCLIP, '-selection', self.selection, '-t', target, '-i'], stdin=PIPE, stderr=DEVNULL)
        else:
            proc = Popen([XCLIP, '-selection', self.selection, '-i'], stdin=PIPE, stderr=DEVNULL)
        proc.communicate(input=contents)
        proc.terminate()
        return True

    def size(self,):
        return len(self.read(target=self.size_target))

    def targets(self,):
        for t in self.read(target='TARGETS').decode('utf-8').splitlines():
            yield t.replace('/', ' ')

if __name__ == "__main__":
    clipboard = Clipboard()

    if len(sys.argv) > 1:
        clipboard.write(str.encode(''.join(sys.argv[1:])))
    else:
        print(clipboard.read().decode())

    sys.exit(0)
