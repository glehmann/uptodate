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

usage = _("uptodate [options] history [name] ...")

summary = _("Affiche l'historique des versions")

description = _("""History est utilis� pour afficher l'historique des versions des modules pass�s en parametre.

Ex :
uptodate history itk-app --last 3""")

names = ['history']

options = [Option("-a", "--all", action="store_true", dest="all", help=_("exporter tous les modules")),
	Option("-A", "--added", action="store_true", dest="added", help=_("afficher l'historique des ajouts de versions")),
	Option("-r", "--removed", action="store_true", dest="removed", help=_("afficher l'historique des suppressions de versions")),
	]

def runCommand(opts, args, conf, out) :
	if not opts.added and not opts.removed :
		# by default, both removed and added are displayed
		opts.added = True
		opts.removed = True
	
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

	# create a list with added and removed versions for all given modules
	hList = []
	for module in modules :
		if opts.added :
			added = eval(conf.get(module, 'added'))
			for t, versions in added.iteritems() :
				hList.append((t, True, module, versions))
		if opts.removed :
			removed = eval(conf.get(module, 'removed'))
			for t, versions in removed.iteritems() :
				hList.append((t, False, module, versions))

	addedTemp = _('  + %s : %s (%s)')
	removedTemp = _('  - %s : %s (%s)')
	for t, add, module, versions in sorted(hList, reverse = True) :
	    if add :
		print >> out, addedTemp % (module, andJoin(map(repr, versions)), makeTime(t)) 
	    else :
		print >> out, removedTemp % (module, andJoin(map(repr, versions)), makeTime(t)) 