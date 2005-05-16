#!/usr/bin/env python
#coding: iso-8859-15
#
# Copyright (C) 2005  Gaëtan Lehmann <gaetan.lehmann@jouy.inra.fr>
#
# this file is part of uptodate
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

# this module sets python 2.3 compatibility


# python 2.4 now have set in __builtin__ module

import sets
set = sets.Set
del sets

# python 2.4 enhance sort method in list object with key and reverse parameters, and introduced sorted function which do the same as sort but on a copied list
# as it's far more difficult to modify sort method, we implement a sorted fuction for python 2.3

def sorted(iterable, cmp=None, key=None, reverse=False) :
	i = list(iterable)
	if key :
		d = {}
		for v in iterable :
			k = key(v)
			if not d.has_key(k) :
				d[k] = []
			d[k].append(v)
		keys = d.keys()
		keys.sort(cmp)
		i = []
		for k in keys :
			i += d[k]
	else :
		i.sort(cmp)
	if reverse :
		i.reverse()
	return i
	
# string.Template allow us to create templated command without problem : 
# configparser use standard substitution, so an error in template can make the config file invalid. With the new template, we avoid this problem
# thoses classes are stollen from python 2.4 string module
import re
class _TemplateMetaclass(type):
	pattern = r"""
	%(delim)s(?:
	(?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
	(?P<named>%(id)s)      |   # delimiter and a Python identifier
	{(?P<braced>%(id)s)}   |   # delimiter and a braced identifier
	(?P<invalid>)              # Other ill-formed delimiter exprs
	)
	"""
	
	def __init__(cls, name, bases, dct):
		super(_TemplateMetaclass, cls).__init__(name, bases, dct)
		if 'pattern' in dct:
			pattern = cls.pattern
		else:
			pattern = _TemplateMetaclass.pattern % {
				'delim' : re.escape(cls.delimiter),
				'id'    : cls.idpattern,
				}
		cls.pattern = re.compile(pattern, re.IGNORECASE | re.VERBOSE)


class Template:
	"""A string class for supporting $-substitutions."""
	__metaclass__ = _TemplateMetaclass
	
	delimiter = '$'
	idpattern = r'[_a-z][_a-z0-9]*'
	
	def __init__(self, template):
		self.template = template
	
	# Search for $$, $identifier, ${identifier}, and any bare $'s
	
	def _invalid(self, mo):
		i = mo.start('invalid')
		lines = self.template[:i].splitlines(True)
		if not lines:
			colno = 1
			lineno = 1
		else:
			colno = i - len(''.join(lines[:-1]))
			lineno = len(lines)
		raise ValueError('Invalid placeholder in string: line %d, col %d' %
				(lineno, colno))
	
	def substitute(self, *args, **kws):
		if len(args) > 1:
			raise TypeError('Too many positional arguments')
		if not args:
			mapping = kws
		elif kws:
			mapping = _multimap(kws, args[0])
		else:
			mapping = args[0]
		# Helper function for .sub()
		def convert(mo):
			# Check the most common path first.
			named = mo.group('named') or mo.group('braced')
			if named is not None:
				val = mapping[named]
				# We use this idiom instead of str() because the latter will
				# fail if val is a Unicode containing non-ASCII characters.
				return '%s' % val
			if mo.group('escaped') is not None:
				return self.delimiter
			if mo.group('invalid') is not None:
				self._invalid(mo)
			raise ValueError('Unrecognized named group in pattern',
					self.pattern)
		return self.pattern.sub(convert, self.template)
	
	def safe_substitute(self, *args, **kws):
		if len(args) > 1:
			raise TypeError('Too many positional arguments')
		if not args:
			mapping = kws
		elif kws:
			mapping = _multimap(kws, args[0])
		else:
			mapping = args[0]
		# Helper function for .sub()
		def convert(mo):
			named = mo.group('named')
			if named is not None:
				try:
					# We use this idiom instead of str() because the latter
					# will fail if val is a Unicode containing non-ASCII
					return '%s' % mapping[named]
				except KeyError:
					return self.delimiter + named
			braced = mo.group('braced')
			if braced is not None:
				try:
					return '%s' % mapping[braced]
				except KeyError:
					return self.delimiter + '{' + braced + '}'
			if mo.group('escaped') is not None:
				return self.delimiter
			if mo.group('invalid') is not None:
				return self.delimiter
			raise ValueError('Unrecognized named group in pattern',
					self.pattern)
		return self.pattern.sub(convert, self.template)
