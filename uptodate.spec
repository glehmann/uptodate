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
Requires:	python >= 2.3
BuildRoot:	%{_tmppath}/%{name}-buildroot
BuildArch:	noarch
BuildRequires:	python

%description
uptodate is powerful and user friendly command line tool which helps you to
know when a new version is available. It searches for new versions in a web
page, a ftp directory, etc, and shows you added and removed version since the
last search. If you update some softs by hand, if you are a package maintainer,
or if you simply want to know when the new version of your favorite game (or
everything else with a version) is out, uptodate is for you !

%prep

%setup

%build

%install
python setup.py install --root=%buildroot

%clean
/bin/rm -Rf %buildroot


%files
%defattr(0644, root, root, 0755)
%attr(0755,root,root) %{_bindir}/*
%{_libdir}/python%{pyver}/site-packages/*
%{_datadir}/locale/*/*/*
%config(noreplace) %{_sysconfdir}/bash_completion.d/uptodate
%doc COPYING README

