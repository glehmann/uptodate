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

usage = _("uptodate [options] add nom url regexp")

summary = _("Ajoute un nouveau module")

description = _("""Add est utilisé pour ajouter un nouveau module. Un module posssède un nom et contient les informations nécessaires pour aller chercher les nouvelles versions :
+ une URL d'un fichier ou d'un repertoire. Le fichier ou le répertoire peuvent être distant (site web, site ftp) ou local
+ une expression régulière permettant de trouver les versions dans les informations récupérées grâce à l'URL précédente
Vous pouvez également ajouter un commentaire pour décrire le module, pour garder la page d'accueil du programme dont vous voulez suivre la version, etc.
Ces informations doivent être fournie sur la ligne de commande.

Exemple :
uptodate add zope http://www.zope.org/Products/ 'Download Zope (.{1,10})\\s*</a>' -C 'A leading open source application server'""")

names = ['add']

options = [Option("-A", "--add-command", dest="addCommand", default="", metavar="COMMANDE", help=_("la commande à exécuter lors de l'ajout d'une version")),
        Option("-C", "--comment", dest="comment", default="", metavar="COMMENTAIRE", help=_("associe le commentaire au module")),
        Option("-r", "--remove-command", dest="removeCommand", default="", metavar="COMMANDE", help=_("la commande a exécuter lors de la suppression d'une version")),
	]

def runCommand(opts, args, conf, out) :
	if len(args) != 3 :
		raise InvalidNbOfArgsException(usage)
		
	module, url, regexp = args
	add(module, url, regexp, opts, conf, out)


def add(module, url, regexp, opts, conf, out) :
	# test addcommand and removeCommand values
	try :
		Template(opts.addCommand).substitute({'module': 'module', 'version': 'version'})
		Template(opts.removeCommand).substitute({'module': 'module', 'version': 'version'})
	except KeyError :
		raise PropertyTypeError()

	if not opts.force and conf.has_section(module) :
		if opts.batch or not yes(_("Voulez vous supprimer le module %s ?") % module, False) :
			raise ModuleExistsException(module)
		else :
			opts.force = True
	
	current = getVersions(module, url, regexp)
	
	# test if a version can be found
	if len(current) != 0 :
		if opts.force and conf.has_section(module) :
			conf.remove_section(module)
		createModule(conf, module, url, regexp, opts.comment, opts.addCommand, opts.removeCommand)
		updateVersions(conf, module, current)
		# conf.set(module, 'current', repr(current))
		
		if opts.verbose :
			printModule(conf, module, sys.stderr, True)
	else :
		# no version found... exit
		raise NoVersionFound()
	

def createModule(conf, module, url, regexp, comment='', addCommand='', remCommand='', versions=[]) :
	"""Create a new module in config file
	"""
	conf.add_section(module)
	conf.set(module, 'url', url)
	conf.set(module, 'regexp', regexp)
	conf.set(module, 'comment', comment)
	conf.set(module, 'add-command', addCommand)
	conf.set(module, 'remove-command', remCommand)
	updateVersions(conf, module, versions)

	
