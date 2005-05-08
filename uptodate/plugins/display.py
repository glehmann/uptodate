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

usage = _("uptodate [options] display [nom] ...")

summary = _("Affiche les informations sur les modules")

description = _("""Display est utilisé pour afficher les informations sur les modules fournis en paramètre.

Exemple :
uptodate display itk-app""")

names = ['display']

options = [Option("-a", "--all", action="store_true", dest="all", help=_("afficher tous les modules")),
	]

def runCommand(opts, args, conf, out) :
	if len(args) == 0 and not opts.all :
		raise InvalidNbOfArgsException(usage)
	
	if opts.all :
		modules = conf.sections()
	else :
		modules = set(args)
		wrongModules = modules - set(conf.sections())
		if wrongModules :
			if opts.force :
				modules -= wrongModules
			else :
				raise ModuleNotFoundException(wrongModules)


	for module in sorted(modules) :
		printModule(conf, module, out, opts.verbose)
