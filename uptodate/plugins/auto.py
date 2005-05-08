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
import add

usage = _("uptodate [options] auto nom url version")

summary = _("Ajoute un nouveau module sans avoir à fournir d'expression régulière")

description = _("""Auto est utilisé pour ajouter un nouveau module sans avoir a fournir l'expression régulière qui permet de récupérer les versions.
Vous devez fournir :
+ un nom. Si le nom est présent à l'URL fournie, il influencera le choix de l'expression régulière.
+ une URL d'un fichier ou d'un repertoire. Le fichier ou le répertoire peuvent être distant (site web, site ftp) ou local
+ un numéro de version présent à l'URL fournie. Ce numéro permet de trouver l'expression régulière qui sera utilisé pour obtenir les nouvelles versions.
Vous pouvez également ajouter un commentaire pour décrire le module, pour garder la page d'accueil du programme dont vous voulez suivre la version, etc.
Ces informations doivent être fournie sur la ligne de commande.

Exemples :
+ zope
uptodate auto zope http://www.zope.org/Products/ 2.7.4

+ InsightToolkit, depuis la page de téléchargement de sourceforge :
uptodate auto InsightToolkit 'http://sourceforge.net/project/showfiles.php?group_id=108122&package_id=116777' 2.0.1

+ jpackage non free files, depuis un répertoire ftp :
uptodate auto jpackage ftp://sunsite.informatik.rwth-aachen.de/pub/Linux/jpackage/1.6/generic/SRPMS.non-free/ j2ee-connector-1.5-3jpp.nosrc.rpm

+ jpackage releases, depuis un repertoire ftp :
uptodate auto jpackage-release ftp://sunsite.informatik.rwth-aachen.de/pub/Linux/jpackage/ 1.6""")

names = ["auto"]

options = add.options + [Option("-i", "--interactive", action="store_true", dest="choose", help=_("choisir une expression régulière dans la liste proposée par uptodate")),
	]

def runCommand(opts, args, conf, out) :
	versionRegExp = r'([^<>\n\r]+)'
    
	if len(args) != 3 :
		raise InvalidNbOfArgsException(usage)

	module, url, version = args
	
	if not opts.force and conf.has_section(module) :
		if opts.batch or not yes(_("Voulez vous supprimer le module %s ?") % module, False) :
			raise ModuleExistsException(module)
		else :
			opts.force = True
	
	# load data which will be used to search regexp
	urlData = loadData(url)

	# find text around version string given by user
	bordersRegexps = []
	# text is keep from version to ', " or < (or >, depending of side)
	bordersRegexps.append(('', r'([>"\'][^>"\']*)%s([^>"]{0,20}[<"\'])', ''))
	# for ftp listing
	bordersRegexps.append((r'[drwxls\-]{10}\s+' + r'\S+\s+' * 7, r'(\S*)%s(\S*)', ''))
	# finally, use what we can find
	bordersRegexps.append(('', '(.*)%s(.*)', ''))
		
	borders = []
	# select borders
	for (prefix, bRegexp, suffix) in bordersRegexps :
		borders = re.findall(prefix + bRegexp % escape(version) + suffix, urlData)
		if borders != [] :
			break
	
	if len(borders) == 0 :
		raise NoVersionFound()

	# generate regexp candidates, and select the best one
	candidates = set()
	regexp = ""
	for border in borders :
		lBorder, rBorder = border
		
		# remove part of border if version is found in it
		if version in lBorder :
			lBorder = lBorder[lBorder.find(version)+len(version):]
		if version in rBorder :
			rBorder = rBorder[:lBorder.find(version)]
			
		# escape characters so they can be used in regexp
		lBorder = escape(lBorder)
		rBorder = escape(rBorder)
		
		# create regexp candidate
		candidate = prefix + lBorder + versionRegExp + rBorder + suffix
	
		# finally, add regexp candidate to the list
		candidates.add(candidate)


	# sort canditates
	# best candidates have the module name near the version
	# find candidates with module name in it
	bestCandidates = [c for c in candidates if module in c]
	# define a function able to give distance from module to version
	def disModuleVersion(s) :
		vPos = s.find(versionRegExp)
		mPos = s.find(module)
		if vPos > mPos :
			return vPos - (mPos + len(module))
		else :
			return mPos - (vPos + len(versionRegExp))

	# define another method which add -length, so it can be used as a second sort parameter (largest is the best)
	def lenModuleVersion(s) :
		return (disModuleVersion(s), -len(s))
	
	# use this second function to sort bestCandidates
	# don't use it for python 2.3 : bestCandidates.sort(key=lenModuleVersion)
	bestCandidates = sorted(bestCandidates, key=lenModuleVersion)

	# sort the other candidate (largest is the best)	
	otherCandidates = sorted(candidates - set(bestCandidates), key=len, reverse=True)

	candidates = bestCandidates + otherCandidates
	regexp = candidates[0]
	
	if opts.choose :
		# ask to user to select a regexp
		print >> sys.stderr, _("Les expressions régulières disponibles sont :")
		for i, candidate in enumerate(candidates) :
			print >> sys.stderr, "%i. %s" % (i, candidate)
			print >> sys.stderr, '    %s' % andJoin(map(repr, set(re.findall(candidate, urlData))))
			print >> sys.stderr
		# get number
		import readline
		selectRegExp = -1
		while selectRegExp == -1 :
			try :
			        userAnwser = raw_input(_("Choisissez une expression régulière (0) :"))
				selectRegExp = int(userAnwser)
				if selectRegExp < 0 or selectRegExp >= len(candidates) :
					selectRegExp = -1
			except ValueError :
				if userAnwser == "" :
				    selectRegExp = 0
			except EOFError :
				# transform EOF in keyboard interrupt
				raise KeyboardInterrupt()
		# replace automatically selected regexp with user one
		regexp = candidates[selectRegExp]

	# get versions founds with selected regexp
	current = list(set(re.findall(regexp, urlData)))

	# test if a version can be found
	if len(current) != 0 :
		if opts.force and conf.has_section(module) :
			conf.remove_section(module)
		add.createModule(conf, module, url, regexp, opts.comment, opts.addCommand, opts.removeCommand)
		updateVersions(conf, module, current)
		# conf.set(module, 'current', repr(current))
		
		if opts.verbose :
			printModule(conf, module, sys.stderr, True)
	else :
		# no version found... exit
		raise NoVersionFound()
