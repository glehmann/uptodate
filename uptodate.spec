%define name		uptodate
%define version		0.2
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
      2.7.4 \
      A leading open source application server
   
 uptodate add --auto command takes three arguments:
 + a name
 + url where it will search version
 + the current version number
 + an optional comment

uptodate add --auto try to find a regular expression which will be used
to find new versions. If uptodate add --auto can't find a regular
expression, or if the regular expression isn't good enough for you, you
can use uptodate add :

   uptodate add zope \
      http://www.zope.org/Products/ \
      'Download Zope (.{1,10})\s*</a>' \
      A leading open source application server
      
arguments are the same, but the third is regular expression instead of 
version.

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
mkdir -p %buildroot%{_sysconfdir}/bash_completion.d

cp uptodate %buildroot%{_bindir}
cp uptodate.bash_completion %buildroot%{_sysconfdir}/bash_completion.d/uptodate

%clean
/bin/rm -Rf %buildroot


%files
%defattr(0644, root, root, 0755)
%attr(0755,root,root) %{_bindir}/*
%config(noreplace) %{_sysconfdir}/bash_completion.d/uptodate
%doc COPYING README version


%changelog
* Mon Mar 28 2005 Gaetan Lehmann <gaetan.lehmann@jouy.inra.fr> 0.2-1mdk
- 0.2

* Sat Mar 26 2005 Gaetan Lehmann <gaetan.lehmann@jouy.inra.fr> 0.1-1mdk
- initial contrib


