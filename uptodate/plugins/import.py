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

usage = _("uptodate [options] import file [name] ...")

summary = _("Import modules")

description = _("""Import is used in order to import modules.

Example:
uptodate import config""")

names = ['import']

options = [Option("-a", "--all", action="store_true", dest="all", help=_("import all modules in file")),
	]

def runCommand(opts, args, conf, out) :
        # load config to import
	import ConfigParser
	importConf = ConfigParser.SafeConfigParser()
	importFile = file(args[0])
	importConf.readfp(importFile)
	importFile.close()

	# module to import
	if len(args) <= 1 and not opts.all :
		raise InvalidNbOfArgsException(usage)
	
	if opts.all :
		modules = importConf.sections()
	else :
		modules = set(args[1:])
		wrongModules = modules - set(importConf.sections())
		if wrongModules :
			if opts.force :
				modules -= wrongModules
			else :
				raise ModuleNotFoundException(wrongModules)
	
	
	# now iterate sections
	for module in sorted(modules) :
		imp = True
		if conf.has_section(module) :
			if opts.force :
				conf.remove_section(module)
			elif opts.batch :
				raise ModuleExistsException(module)
			elif yes(_("Do you want to remove the module %s?") % module, False) :
				conf.remove_section(module)
			else :
				imp = False
		if imp :
			# copy section
			conf.add_section(module)
			for prop in importConf.options(module) :
				conf.set(module, prop, importConf.get(module, prop))
			if opts.verbose :
				printModule(conf, module, sys.stderr, True)

	return 0
