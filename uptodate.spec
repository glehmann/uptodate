%define name		uptodate
%define version		0.1
%define release		1

Name:		%{name}
Summary:	Uptodate helps you to keep your system uptodate
Version:	%{version}
Release:	%mkrel %{release}
URL:		http://gleh.dyndns.org/uptodate/
Source0:	http://gleh.dyndns.org/uptodate/uptodate-%{version}.tar.bz2
License:	GPL
Group:		Networking/Other
Requires:	python >= 2.4
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildArch:	noarch

%description
uptodate can tell you when a new version of a program is avaible. To
do that, you have to add a module. Lets try with zope :

   uptodate add zope \
      http://www.zope.org/Products/ \
      'Download Zope (.{1,10})\s*</a>' \
      A leading open source application server

uptodate add command takes three arguments:
 + a name
 + url where it will search version
 + a regular expression to locate version in the text
 + an optional comment

Future release will try to find the regular expression for you.

You can now check for new versions with

   uptodate check zope

it will display something like

   zope: '2.7.4' removed.
   zope: '2.7.5' added.

if versions found in the text have changed.


%prep
%setup


%build


%install
mkdir -p %buildroot%{_bindir}
cp uptodate %buildroot%{_bindir}

%clean
/bin/rm -Rf %buildroot


%files
%defattr(0755, root, root, 0755)
%{_bindir}/*
%doc COPYING README version


%changelog
* Sat Mar 26 2005 Gaetan Lehmann <gaetan.lehmann@jouy.inra.fr> 0.1-1mdk
- initial contrib


