#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import errno
import sys
from os import getuid, getgid

from time import time
from stat import S_IFDIR, S_IFREG
from fuse import FUSE, Operations, FuseOSError

from RegularFile import RegularFile
from clipboard import Clipboard

class ClipboardFile(Clipboard, RegularFile):
	def __init__(self, selection='primary'):
		Clipboard.__init__(self, selection)
		RegularFile.__init__(self)

class ClipboardFS(Operations):

	selections = ('primary', 'secondary', 'clipboard')

	def __init__(self):
		now = time()
		self.fd = 0
		self.contents = b"Hello Kitty\n"
		self.files = dict()
		self.files['/'] = ClipboardFS.create_directory_dict(now)
		for dirname in self.selections:
			self.files['/' + dirname] = ClipboardFS.create_directory_dict(now) 
			self.files['/' + dirname + '/board'] = ClipboardFile(dirname)


	@staticmethod
	def create_directory_dict(stat_time):
		return dict(
			st_mode=(S_IFDIR | 0o755),
			st_atime=stat_time,
			st_ctime=stat_time,
			st_mtime=stat_time,
			st_uid=getuid(),
			st_gid=getgid(),
			st_nlink=2)


	def getattr(self, path, fh=None):
		if path not in self.files.keys():
			for sel in self.selections:
				prefix = '/' + sel + '/'
				if path.startswith(prefix):
					elem = self.files[prefix + 'board']
					elem.size_target = path[len(prefix):]
					return elem
			raise FuseOSError(errno.ENOENT)

		elem = self.files[path]
		if isinstance(elem, ClipboardFile):
			elem.size_target = None
		return elem

	def destroy(self, path):
		print("Shutting down")

	def opendir(self, path):
		return self.fd

	def open(self, path, flags):
		return 1

	def read(self, path, size, offset, fh):
		for sel in self.selections:
			prefix = '/' + sel + '/'
			if path == prefix + 'board':
				return self.files[path].read()
			if path.startswith(prefix):
				return self.files[prefix + 'board'].read(target=path[len(prefix):])

	def readdir(self, path, fh):
		if path == "/":
			return ('.', '..') + self.selections
		for sel in self.selections:
			if path == "/" + sel:
				return ['.', '..', 'board'] + list(self.files['/' + sel + '/board'].targets())
		raise FuseOSError(errno.ENOENT)

	def write(self, path, data, offset, fh):
		if path == "/board":
			self.contents = data

if __name__ == "__main__":
	try:
		mount_path = sys.argv[1]
	except IndexError:
		print("Must specify the path to mount the filesystem on.", file=sys.stderr)
		sys.exit(-1)

	clipboard = ClipboardFS()
	FUSE(clipboard, mount_path, foreground=True)

