#!/usr/bin/env python
#coding: iso-8859-15
#
# uptodate helps you to keep your system uptodate
#
# Copyright (C) 2005  Gaëtan Lehmann <gaetan.lehmann@jouy.inra.fr>
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

VERSION = "0.3"


import gettext
gettext.install('uptodate')




import sys
import os.path
from optparse import OptionParser, IndentedHelpFormatter
from uptodate import *




														
# COMMANDS = [(['add'], commandAdd),
# 	    (['check'], commandCheck),
# 	    (['edit'], commandEdit),
# 	    (['remove', 'rm', 'del'], commandRemove),
# 	    (['display'], commandDisplay),
# 	    (['copy', 'cp'], commandCopy),
# 	    (['rename', 'mv'], commandRename),
# 	    (['auto'], commandAuto),
# 	    (['import'], commandImport),
# 	    (['export'], commandExport),
# 	    (['history'], commandHistory),
# 	    ]

def addGlobalOptions(parser) :
	parser.add_option("-c", "--config-file", dest="configPath", default=os.path.expanduser("~/.uptodate"), metavar=_("FICHIER"), help=_("fichier de configuration (%default)"))
	parser.add_option("-d", "--dry-run", action="store_true", dest="dryRun", help=_("ne pas sauvegarder les changements"))
	parser.add_option("-o", "--output", dest="outputPath", default="-", metavar=_("FICHIER"), help=_("ecrire dans FICHIER (sortie standard par défaut)"))
	parser.add_option("-b", "--batch", action="store_true", dest="batch", help=_("ne pas poser de question"))
	parser.add_option("-f", "--force", action="store_true", dest="force", help=_("ignorer les ???"))
	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help=_("afficher ce qui est fait"))
	parser.add_option("--list-option", action="store_true", dest="listOption", help=_("afficher les options et les commandes disponibles"))

	
def makeDescription() :
	DESCRIPTION=_('''uptodate vous permet de suivre les versions de tout ce qui a une version

uptodate est un programme en ligne de commande facile à utiliser qui vous aide à
savoir quand une nouvelle version est disponible. Il recherche les versions dans
une page web, un repertoire ftp, etc, et vous montre les versions ajoutées et
supprimées depuis la dernière recherche.
Si vous mettez à jour certains logiciels à la main, si vous êtes mainteneur de
paquetages (rpm, deb, ...), ou si vous voulez simplement savoir quand la
nouvelle version de votre jeu favori (ou de tout autre chose avec une version)
est disponible, uptodate est fait pour vous !

Auteur : Gaëtan Lehmann <gaetan.lehmann@jouy.inra.fr>
Site web: http://gleh.dyndns.org/uptodate/

Commandes :
%s
Executez "uptodate command --help" pour plus d\'informations.

Codes de sortie :
%s''')
	ERRORS = {
		ERROR_INVALID_NB_OF_ARGS: _("Nombre d'arguments invalide"),
		ERROR_NO_VERSION_FOUND: _("Aucune version trouvée"),
		ERROR_MODULE_NOT_FOUND: _("Impossible de trouver le module"),
		ERROR_PROPERTY_NOT_FOUND: _("Impossible de trouver la propriété"),
		ERROR_MODULE_EXISTS: _("Le module existe déjà"),
		ERROR_UNKNOWN_COMMAND: _("Commande inconnue"),
		ERROR_IO: _("Erreur d'entrée/sortie"),
		ERROR_KB_INTERRUPT: _("Interuption au clavier"),
		ERROR_PROPERTY_TYPE: _('Type de propriété invalide'),
	}

	# generate command description
	formattedCommands = {}
	fill = 0
	for mod in initCommands() :
		names = mod.names
		namesString = names[0]
		if len(names) > 1 :
			namesString += ' (%s)' % ', '.join(names[1:])
		formattedCommands[namesString] = mod.summary.splitlines()[0].strip()
		namesLen = len(namesString)
		if namesLen > fill :
			fill = namesLen
	comString = ""
	fill = max([len(c) for c in formattedCommands.keys()])
	for names in sorted(formattedCommands.keys()) :
                comString += "  %s  %s\n" % (names.ljust(fill), formattedCommands[names])


	# generate exit code description
	errString = ""
	fill = max([len(str(c)) for c in ERRORS.keys()])
	for error in sorted(ERRORS.keys()) :
		errString += _("  %s  %s\n") % (str(error).ljust(fill), ERRORS[error])
		
	# generate complete description
	return DESCRIPTION % (comString, errString)

	
def main(argv) :
	# create a dict to have easy access to command names and functions
	commands = {}
	for mod in initCommands() :
		# print mod
		for name in mod.names :
			commands[name] = mod
        
	# and create option parser
	parser = OptionParser(usage = _("uptodate [options] commande [options] [arguments]"),
			      description = makeDescription(),
			      version = "uptodate %s" % VERSION,
			      formatter = UptodateHelpFormatter())
	addGlobalOptions(parser)
	parser.disable_interspersed_args()
	opts, args = parser.parse_args()

	if len(args) > 0 :
		command = args[0]
		if command in commands.keys() :
			parser = OptionParser(formatter=UptodateCommandHelpFormatter())
			# add command options
			for option in commands[command].options :
				parser.add_option(option)
			# add global options
			addGlobalOptions(parser)
			# set usage and description from command
			parser.set_description(commands[command].description)
			parser.set_usage(commands[command].usage)
			# and reparse options !
			opts, args = parser.parse_args()
			# drop command from args
			del args[0]
		else :
			raise UnknownCommandException(command)
	else:
		if opts.listOption :
			listOptions(parser)
			# also display commands !
			for command in commands.keys() :
				print command
			return
    		else :
			raise InvalidNbOfArgsException(parser.get_usage())
	
	
	# load config in a file to be able to load it from stdin
	import ConfigParser
	conf = ConfigParser.SafeConfigParser()
	try :
		# try to load config
		confFile = file(opts.configPath)
	except :
		# load fail... try to create it
		file(opts.configPath, True).close()
		confFile = file(opts.configPath)
	conf.readfp(confFile)
	confFile.close()
	
	if opts.listOption :
		listOptions(parser)
		listModules(conf)
		return

	# set output file
	out = file(opts.outputPath, True)
	
	# execute command
	retVal = commands[command].runCommand(opts, args, conf, out)
	
	# save config file, if needed
	if not opts.dryRun :
		confFile = file(opts.configPath, 'w')
		conf.write(confFile)
		confFile.close()

	return 0






if __name__ == '__main__':
	import sys
	try :
		sys.exit(main(sys.argv[1:]))
		
	except IOError, e:
		sys.stderr.write(sys.argv[0]+": ")
		if e.filename :
			sys.stderr.write(e.filename+": ")
		sys.stderr.write(str(e.strerror)+"\n")
		sys.exit(ERROR_IO)

	except KeyboardInterrupt, e :
		sys.stderr.write(str(e)+"\n")
		sys.exit(ERROR_KB_INTERRUPT)
		
	except InvalidNbOfArgsException, e :
		print >> sys.stderr, e.args[0]
		sys.exit(ERROR_INVALID_NB_OF_ARGS)

	except ModuleExistsException, e :
		print >> sys.stderr, _("Erreur : Le module %s existe déjà.") % e.args[0]
		sys.exit(ERROR_MODULE_EXISTS)

	except NoVersionFound, e :
		print >> sys.stderr, _("Erreur : Aucune version trouvée")
		sys.exit(ERROR_NO_VERSION_FOUND)

	except ModuleNotFoundException, e :
		sing = _("Erreur : Le module %s n'existe pas.")
		plur = _("Erreur : Les modules % n'existent pas.")
		args = e.args[0]
		if isinstance(args, str) :
			msg = sing % args
		elif len(args) == 1 :
			args = list(args)
			msg = sing % args[0]
		else :
			args = list(args)
			msg = plur % andjoin(list(args))
		print >> sys.stderr, msg
		sys.exit(ERROR_MODULE_NOT_FOUND)

	except PropertyNotFoundException, e :
		print >> sys.stderr, _("Erreur : La propriété %s n'existe pas.") % e.args[0]
		sys.exit(ERROR_PROPERTY_NOT_FOUND)

	except UnknownCommandException, e :
		print >> sys.stderr, _("Erreur : La commande %s n'existe pas.") % e.args[0]
		sys.exit(ERROR_UNKNOWN_COMMAND)
		
	except PropertyTypeError, e :
		print >> sys.stderr, _("Erreur : Le type de la propriété est invalide.")
		sys.exit(ERROR_PROPERTY_TYPE)
		
