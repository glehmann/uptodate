#!/usr/bin/env python
#coding: iso-8859-15
#
# Copyright (C) 2005  Ga�tan Lehmann <gaetan.lehmann@jouy.inra.fr>
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

usage = _("uptodate [options] edit nom propri�t� [valeur]")

summary = _("Modifie les propri�t�s d'un module")

description = _("""Edit est utilis� pour modifier les propri�t�s d'un module. Les propri�t�s modifiables sont : url, regexp et comment. Si url ou regexp sont modifi�es, uptodate v�rifie qu'il peut obtenir des versions avant de valider les changements.

Exemple :
uptodate edit itk-app comment des applications utilisant InsightToolkit""")

names = ["edit"]

options = []

def runCommand(opts, args, conf, out) :
	if len(args) == 2 and not opts.batch :
		# interactive edit
		module, prop = args
		if module not in conf.sections() :
			raise ModuleNotFoundException(module)
		if not conf.has_option(module, prop) :
			raise PropertyNotFound(prop)

		import readline
		# arghhh
		# readline.insert_text() seems to so nothing :-(
		# how to set an initial value ??
		readline.insert_text(conf.get(module, prop))
		value = raw_input(_('%s value : ') % prop)
		
	elif len(args) >= 3 :
		# command line edit
		module = args[0]
		prop = args[1]
		value = " ".join(args[2:])
		if module not in conf.sections() :
			raise ModuleNotFoundException(wrongModules)
		if not conf.has_option(module, prop) :
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
