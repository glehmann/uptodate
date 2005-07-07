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

usage = _("uptodate [options] copy name name")

summary = _("Copy a module")

description = _("""Copy is used in order to copy a module.

Example:
uptodate copy itk-app InsightToolkit-Applications""")

names = ['copy', 'cp']

options = []

def runCommand(opts, args, conf, out) :
	if len(args) != 2 :
		raise InvalidNbOfArgsException(usage)

	module, new = args
	if module not in conf.sections() :
		raise ModuleNotFoundException(module)

	if not opts.force and conf.has_section(new) :
		if opts.batch or not yes(_("Do you want to remove the module %s?") % new, False) :
			raise ModuleExistsException(new)
		else :
			opts.force = True
	
	# remove new section if it already exist and --force is used
	if opts.force and  conf.has_section(new) :
		conf.remove_section(new)

	conf.add_section(new)
	for prop in conf.options(module) :
		conf.set(new, prop, conf.get(module, prop))
	if opts.verbose :
		printModule(conf, new, sys.stderr, True)
