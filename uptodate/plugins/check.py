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
import os
# from string import Template

usage = _("uptodate [options] check [nom] ...")

summary = _("Cherche les nouvelles versions")

description = _("""Check est utilisé pour chercher les nouvelles versions des modules donnés en paramètres. Par défaut, les nouvelles versions et les versions supprimées sont affichées.
Les versions trouvées sont enregistrées afin de pouvoir afficher les modifications à la prochaine éxécution de cette commande.
Vous pouvez exectuer cette commande périodiquement (avec cron par exemple) pour suivre l'évolution des versions.

Exemple :
uptodate check zope 
zope : '2.7.5' ajoutée.
zope : '2.7.4' supprimée.""")

names = ["check", "update", "up"]

options = [Option("-a", "--all", action="store_true", dest="all", help=_("rechercher les nouvelles versions de tous les modules")),
	Option("-A", "--added", action="store_true", dest="added", help=_("afficher les versions ajoutées depuis la dernière recherche")),
	Option("-r", "--removed", action="store_true", dest="removed", help=_("afficher les versions supprimées depuis la dernière recherche")),
	]

def runCommand(opts, args, conf, out) :
	if not opts.added and not opts.removed :
		# by default, both removed and added are displayed
		opts.added = True
		opts.removed = True
	
	if len(args) == 0 and not opts.all :
		# no module to check... print usage and exit
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
		if opts.verbose :
			print >> sys.stderr, _("%s : Recherche de nouvelles versions.") % module
		# get module properties
		url = conf.get(module, 'url')
		regexp = conf.get(module, 'regexp').replace('\\\\', '\\')
		currentVersions = eval(conf.get(module, 'current'))
		if conf.has_option(module, 'add-command') :
			addCommand = Template(conf.get(module, 'add-command'))
		else :
			addCommand = Template("")
		if conf.has_option(module, 'remove-command') :
			removeCommand = Template(conf.get(module, 'remove-command'))
		else :
			removeCommand = Template("")
		
		# get new versions
		newVersions = getVersions(module, url, regexp)
		# test if a version can be found
		if len(newVersions) != 0 :
			updateVersions(conf, module, newVersions)
			# conf.set(module, 'current', repr(newVersions))
			
			added = set(newVersions) - set(currentVersions)
			removed = set(currentVersions) - set(newVersions)
			# display added and removed versions
			if added and opts.added :
				if len(added) == 1 :
					print >> out, _("%s : %s ajoutée.") % (module, repr(list(added)[0]))
				else :
					print >> out, _("%s : %s ajoutées.") % (module, andJoin(map(repr, added)))
			if removed and opts.removed :
				if len(removed) == 1 :
					print >> out, _("%s : %s supprimée.") % (module, repr(list(removed)[0]))
				else :
					print >> out, _("%s : %s supprimées.") % (module, andJoin(map(repr, removed)))
					
			# execute commands
			if not opts.dryRun :
				if addCommand.template :
					for version in added :
						d = {'module': module, 'version': version}
						command = addCommand.substitute(d)
						if opts.verbose :
							print >> sys.stderr,  _("%s : exécute + : %s") % (module, command)
						os.system(command)
				if removeCommand.template :
					for version in removed :
						command = removeCommand.substitute(d)
						if opts.verbose :
							print >> sys.stderr, _("%s : exécute - : %s") % (module, command)
						os.system(command)
		else :
			# no version found
			print >> sys.stderr, _("Attention : aucune version trouvée pour %s. Les versions actuellement connues sont conservées.") % module
			# return
