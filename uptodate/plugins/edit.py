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

from uptodate import *

usage = _("uptodate [options] edit name property [value]")

summary = _("Modify module's properties")

description = _("""Edit is used in order to modify module's properties. Modifiable properties are: added, removed, current, add-command, remove-command, url, regexp and comment. If url or regexp are modified, uptodate check if it can obtain versions before validating changes.

Example:
uptodate edit itk-app comment 'applications using InsightToolkit'""")

names = ["edit"]

options = []

def runCommand(opts, args, conf, out) :
	if len(args) == 2 and not opts.batch :
		# interactive edit
		module, prop = args
		if module not in conf.sections() :
			raise ModuleNotFoundException(module)
		if not prop in properties :
			raise PropertyNotFound(prop)

		import readline
		# arghhh
		# readline.insert_text() seems to so nothing :-(
		# how to set an initial value ??
		# readline.insert_text(conf.get(module, prop))
		value = raw_input(_('%s value: ') % prop)
		
	elif len(args) >= 3 :
		# command line edit
		module = args[0]
		prop = args[1]
		value = " ".join(args[2:])
		if module not in conf.sections() :
			raise ModuleNotFoundException(wrongModules)
		if not prop in properties :
			raise PropertyNotFound(prop)
		
	else :
		# invalid number of arguments !
		raise InvalidNbOfArgsException(usage)
	
	# modify prop value
	conf.set(module, prop, value)
	if opts.verbose :
		printModule(conf, module, sys.stderr, True)

	# test if everything is ok
	if not opts.force and prop in ["regexp", "url"] :
		current = getVersions(module, conf.get(module, 'url'), conf.get(module, 'regexp'))
		if len(current) == 0 :
			raise NoVersionFound()
		updateVersions(conf, module, current)
		# conf.set(module, 'current', repr(current))

	# we should avoid user creating wrong type.
	# test it at edit time (before saving)
	
	if not opts.force and prop == 'current' :
		# should be a list of str
		# we use {} as globals (and locals, according to eval doc) to be sure that user will not use value defined in edit
		if not isListOfStr(eval(value, {})) :
			raise PropertyTypeError()
		
	if not opts.force and prop in ['added', 'removed'] :
		# should be a dict, with time (float or int) as keys, and list of str as values
		evaluedValue = eval(value, {})
		for s in evaluedValue.keys() :
			if not (isinstance(s, int) or isinstance(s, float)) :
				raise PropertyTypeError()
		for s in evaluedValue.keys() :
			if not isListOfStr(s) :
				raise PropertyTypeError()
				
	if not opts.force and prop in ['add-command', 'remove-command'] :
		# should work fine with template
		try :
			Template(value).substitute({'module': 'module', 'version': 'version'})
		except KeyError :
			raise PropertyTypeError()
		
		
def isListOfStr(var) :
	if isinstance(var, list) :
		# more than a list, it should be a list of string
		for s in var :
			if not isinstance(s, str) :
				return False
		return True
	return False
	