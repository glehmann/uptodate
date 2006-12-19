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

usage = _("uptodate [options] auto name url version")

summary = _("Add a new module with no need of a regular expression")

description = _("""Auto is used in order to add a new module with no need of the regular expression used to get versions.
You must give:
+ the module's name. If the name is in the received data from the URL, it'll influence the choice of the regular expression.
+ the URL of a file or a directory. The file or the directory may be distant (website, ftp) or local.
+ an existing version number. This version number allows to find the regular expression which will be used to obtain new versions.
You can add a comment to describe the module, to store the homepage, etc.

Examples:
+ zope
uptodate auto zope http://www.zope.org/Products/ 2.7.4

+ InsightToolkit, from the sourceforge download page:
uptodate auto InsightToolkit 'http://sourceforge.net/project/showfiles.php?group_id=108122&package_id=116777' 2.0.1

+ jpackage non free files, from a ftp directory :
uptodate auto jpackage ftp://sunsite.informatik.rwth-aachen.de/pub/Linux/jpackage/1.6/generic/SRPMS.non-free/ j2ee-connector-1.5-3jpp.nosrc.rpm

+ jpackage releases, from a ftp directory :
uptodate auto jpackage-release ftp://sunsite.informatik.rwth-aachen.de/pub/Linux/jpackage/ 1.6""")

names = ["auto"]

options = add.options
options.append( Option("-k", "--keep", action="store_true", dest="keep", help=_("keep the history, if the module already exist")) )


def runCommand(opts, args, conf, out) :
	versionRegExp = r'([^<>\n\r]+)'
    
	# test addcommand and removeCommand values
	try :
		Template(opts.addCommand).substitute({'module': 'module', 'version': 'version'})
		Template(opts.removeCommand).substitute({'module': 'module', 'version': 'version'})
	except KeyError :
		raise PropertyTypeError()

	if len(args) != 3 :
		raise InvalidNbOfArgsException(usage)

	module, url, version = args
  
	if conf.has_section(module) :
		if opts.keep :
			# just do nothing for now
			pass
		elif opts.force :
			# well, still nothing to do
			pass
		elif opts.batch or not yes(_("Do you want to remove the module %s?") % module, False) :
			# the user don't want to erase its module
			raise ModuleExistsException(module)
		else :
			# the user want to erase the module - just do like when --force is used
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
	
	if not opts.batch :
		# ask to user to select a regexp
		print >> sys.stderr, _("Available regular expressions:")
		for i, candidate in enumerate(candidates) :
			print >> sys.stderr, "%i. %s" % (i, candidate)
			print >> sys.stderr, '    %s' % andJoin(map(repr, set(re.findall(candidate, urlData))))
			print >> sys.stderr
		# get number
		import readline
		selectRegExp = -1
		while selectRegExp == -1 :
			try :
			        userAnwser = raw_input(_("Choose a regular expression (0):"))
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
		if conf.has_section(module) :
			if opts.keep :
				# update the module's attributes
				conf.set(module, 'url', url)
				conf.set(module, 'regexp', regexp)
				pass
			elif opts.force :
				# remove the module, and create
				conf.remove_section(module)
				add.createModule(conf, module, url, regexp, opts.comment, opts.addCommand, opts.removeCommand)
		else :
			# there is no such module - create one
			add.createModule(conf, module, url, regexp, opts.comment, opts.addCommand, opts.removeCommand)
		# and update the version of the new module
		updateVersions(conf, module, current)
		# conf.set(module, 'current', repr(current))
    
		if opts.verbose :
			printModule(conf, module, sys.stderr, True)
	else :
		# no version found... exit
		raise NoVersionFound()
