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

import optparse
import sys
import urllib
import re


import gettext
gettext.install('uptodate')

# error codes

ERROR_INVALID_NB_OF_ARGS = 1
ERROR_NO_VERSION_FOUND = 2
ERROR_MODULE_NOT_FOUND = 3
ERROR_PROPERTY_NOT_FOUND = 4
ERROR_MODULE_EXISTS = 5
ERROR_UNKNOWN_COMMAND = 6
ERROR_IO = 7
ERROR_KB_INTERRUPT = 8

# define uptodate internals exceptions

class InvalidNbOfArgsException(Exception) :
        pass

class NoVersionFound(Exception) :
        pass

class ModuleNotFoundException(Exception) :
        pass

class ModuleExistsException(Exception) :
        pass

class UnknownCommandException(Exception) :
        pass

class PropertyNotFoundException(Exception) :
        pass


	
# helper functions

def printModule(conf, module, out, verbose=False) :
        """
        printModule(conf, module, out, verbose)

        print module info to out file. Infos comes from conf object.
        """
        url = conf.get(module, 'url')
        regexp = conf.get(module, 'regexp').replace('\\\\', '\\')
        current = eval(conf.get(module, 'current'))
        comment = conf.get(module, 'comment')
        if conf.has_option(module, 'added') :
                added = eval(conf.get(module, 'added'))
        else :
                added = {}
        if conf.has_option(module, 'removed') :
                removed = eval(conf.get(module, 'removed'))
        else :
                removed = {}

        if verbose :
                template = _(
"""%(module)s
  commentaire : %(comment)s
  historique : %(history)s
  versions actuelles : %(current)s
  URL : %(url)s
  expression régulière : %(regexp)s
""")

                if added or removed:
                        # create a list with added and removed versions
                        hList = []
                        for t, versions in added.iteritems() :
                                hList.append((t, True))
                        for t, versions in removed.iteritems() :
                                hList.append((t, False))
                        historyString = ""
                        for t, a in sorted(hList, reverse=True) :
                                if a :
                                        historyString += _('\n    + %s : %s') % (makeTime(t), andJoin(map(repr, added[t])))
                                else :
                                        historyString += _('\n    - %s : %s') % (makeTime(t), andJoin(map(repr, removed[t])))
                else :
                        historyString = _('aucun')

                if removed :
                        removedString = ""
                        for t in sorted(removed.keys(), reverse=True) :
                                removedString += _('\n      - %s : %s') % (makeTime(t), andJoin(map(repr, removed[t])))
                else :
                        removedString = _('aucune')
		
		print >> out, template % {'module': module, 'comment': comment, 'url': url, 'regexp': regexp, 'current': andJoin(map(repr, current)), 'history': historyString}
	else :
		s = module
		if comment :
			s += " (%s)" % comment
		if added :
			lastTime = sorted(added.keys(), reverse=True)[0]
			s += '  + %s (%s)' % (andJoin(map(repr, added[lastTime])), makeTime(lastTime))
		if removed :
			lastTime = sorted(removed.keys(), reverse=True)[0]
			s += '  - %s (%s)' % (andJoin(map(repr, removed[lastTime])), makeTime(lastTime))
		
		print >> out, s
		
def makeTime(t) :
	import time
	template = _('%(d)i/%(M)i/%(y)i %(h)ih%(m)i')
	tTuple = time.gmtime(t)
	tDict = {'y': tTuple[0], 'M': tTuple[1], 'd': tTuple[2], 'h': tTuple[3], 'm': tTuple[4], 's': tTuple[5]}
	return template % tDict

def andJoin(iterable) :
	last = _(" et ")
	sep = _(", ")
	if len(iterable) == 0 :
		msg = ""
	elif len(iterable) == 1 :
		msg = iterable[0]
	else :
		msg = sep.join(iterable[:-1]) + last + iterable[-1]
	return msg


def yes(question, default=None) :
	import readline
	if default != None and default :
		values = _('Y/n')
	elif default != None and not default :
		values = _('y/N')
	else :
		values = _('y/n')
		
	try :
		ret = raw_input("%s (%s) " % (question, values)).lower()
	except EOFError :
		# transform EOF in keyboard interrupt
		raise KeyboardInterrupt()
	
	if ret in [_("n"), _("no")] :
		return False
	if ret in [_("y"), _("yes")] :
		return True
	if default != None and ret == "" :
		return default
	# invalid answer... reask the question
	return yes(question, default)


def listOptions(parser) :
	for opt in parser.option_list :
		print opt._long_opts[0]


def listModules(conf) :
	for module in conf.sections() :
		print module
	

def loadData(url) :
    try :
	    urlFile = urllib.urlopen(url)
	    urlData = urlFile.read()
	    urlFile.close()
    except IOError, e :
	    if e.errno == 21 :
		    # url is a directory !
		    # we use 'ls -l' to have the same output than a ftp dir
		    import commands
		    (retVal, urlData) = commands.getstatusoutput('ls -l %s' % url)
		    if retVal != 0 :
			    # something goes wrong...
			    raise urlData
	    else :
		    # re-throw exception :-)
		    raise e
    return urlData


def getVersions(module, url, regexp) :
    urlData = loadData(url)
    new = re.findall(regexp, urlData)
    return list(set(new))


def updateVersions(conf, name, newVersions) :
	import time
	
	if not conf.has_option(name, 'current') :
		conf.set(name, 'current', repr([]))
	if not conf.has_option(name, 'added') :
		conf.set(name, 'added', repr({}))
	if not conf.has_option(name, 'removed') :
		conf.set(name, 'removed', repr({}))
	
	current = set(eval(conf.get(name, 'current')))
	added = eval(conf.get(name, 'added'))
	removed = eval(conf.get(name, 'removed'))
	
	newAdded = list(set(newVersions) - current)
	newRemoved = list(current - set(newVersions))
	newVersions = list(newVersions)
	# print current, added, removed
	# print newVersions, newAdded, newRemoved

	currentTime = time.time()

	conf.set(name, 'current', repr(newVersions))
	if newAdded != [] :
		added[currentTime] = newAdded
		conf.set(name, 'added', repr(added))
	if newRemoved != [] :
		removed[currentTime] = newRemoved
		conf.set(name, 'removed', repr(removed))
	
def file(fName, output=False, notNone=False, append=False) :
        """Renvoi un fichier en fonction du nom de fichier passé en paramètre.
        
        fName est le chemin d'acces complet a un fichier.
        fName = "-" est interprété comme l'entrée (ou la sortie, si output=True) standard.
        output = True indique que le ficher doit etre ouvert en ecriture
        notNone = True provoque le renvoi d'un fichier ouvert sur /dev/null plutot que None quand fName = ""
        append provoque l'ouverture du ficheir en mode append. Doit etre utilisé avec output = True
        """
	import __builtin__
        if append :
                wMode = "a"
        else :
                wMode = "w"
        
        #le nom de fichier est vide...
        if fName == "" :
                if notNone :
                        if output :
                                return file("/dev/null", wMode)
                        else :
                                return file("/dev/null")
                else :
                        return None
        
        elif fName == "-" :
                #la sortie ou l'entree standard
                if output :
                        return sys.stdout
                else :
                        return sys.stdin
        else :
                # un fichier normal
                if output :
                        return __builtin__.file(fName, wMode)
                else :
                        return __builtin__.file(fName)


def escape(s) :
	for c in '\\{}[]()?.' :
		s = s.replace(c, '\\'+c)
	return s


class UptodateHelpFormatter(optparse.IndentedHelpFormatter) :
	def format_description(self, description) :
		return description


class UptodateCommandHelpFormatter(optparse.IndentedHelpFormatter) :
	def format_description(self, description) :
		if not description :
			return ""
		import textwrap
		desc_width = self.width - self.current_indent
		indent = " "*self.current_indent
		newDesc = ""
		for line in description.splitlines() :
			newDesc += textwrap.fill(line.strip(),
						 desc_width,
						 initial_indent=indent+'  ',
						 subsequent_indent=indent) + "\n"
		return newDesc



# python 2.3 compatibility
if sys.version < '2.4' :
	# set compatibility
	import sets
	set = sets.Set
	# sorted function
	def sorted(iterable, cmp=None, key=None, reverse=False) :
		i = list(iterable)
		if key :
			d = {}
			for v in iterable :
				k = key(v)
				if not d.has_key(k) :
					d[k] = []
				d[k].append(v)
			keys = d.keys()
			keys.sort(cmp)
			i = []
			for k in keys :
				i += d[k]
		else :
			i.sort(cmp)
		if reverse :
			i.reverse()
		return i
	

def initCommands() :
	import plugins
	import os, os.path
	
	commandsDir = os.path.dirname(plugins.__file__)
	commands = []
	for com in os.listdir(commandsDir):
		if com.endswith(".py") and com != "__init__.py" :
			commands.append(__import__("uptodate.plugins."+com[:-3], globals, locals, "uptodate.plugins"))
	return commands
	

Option = optparse.Option


