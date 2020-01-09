%define glib2_version 2.44.0
%define vala_version 0.18.0

Name:           dconf
Version:        0.26.0
Release:        3%{?dist}.1
Summary:        A configuration system

Group:          System Environment/Base
License:        LGPLv2+ and GPLv2+ and GPLv3+
URL:            http://live.gnome.org/dconf
#VCS:           git:git://git.gnome.org/dconf
Source0:        http://download.gnome.org/sources/dconf/0.22/dconf-%{version}.tar.xz

# https://bugzilla.redhat.com/show_bug.cgi?id=1386841
Patch0:         dconf-0.26.0-Remove-libdbus-1-support.patch
Patch1:         dconf-0.26.0-read-flag.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1281253
Patch2:         dconf-0.26.0-permissions.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1626372
Patch3:         dconf-0.26.0-db-mtime.patch

BuildRequires:  glib2-devel >= %{glib2_version}
BuildRequires:  libxml2-devel
BuildRequires:  dbus-devel
BuildRequires:  vala-devel >= %{vala_version}
BuildRequires:  gtk-doc
BuildRequires:  intltool

Requires:       dbus
Requires:       glib2%{?_isa} >= %{glib2_version}

%description
dconf is a low-level configuration system. Its main purpose is to provide a
backend to the GSettings API in GLib.

%package devel
Summary: Header files and libraries for dconf development
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
dconf development package. Contains files needed for doing software
development using dconf.

%prep
%setup -q
%patch0 -p1 -R -b .libdbus
%patch1 -p1 -b .read-flag
%patch2 -p1 -b .permissions
%patch3 -p1 -b .mtimes

autoreconf -ivf

%build
%configure --disable-static
make V=1 %{?_smp_mflags}


%install
make install DESTDIR=$RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dconf/profile
cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/dconf/profile/user
user-db:user
system-db:local
system-db:site
system-db:distro
EOF

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dconf/db/local.d/locks
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dconf/db/site.d/locks
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/dconf/db/distro.d/locks

# dconf-dbus-1 was removed in dconf 0.24,
# we keep just the library for compatibility
rm -fv $RPM_BUILD_ROOT%{_libdir}/pkgconfig/dconf-dbus-1.pc
rm -fv $RPM_BUILD_ROOT%{_includedir}/dconf-dbus-1/*
rmdir -v $RPM_BUILD_ROOT%{_includedir}/dconf-dbus-1/

%post
/sbin/ldconfig
gio-querymodules-%{__isa_bits} %{_libdir}/gio/modules
dconf update

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
  gio-querymodules-%{__isa_bits} %{_libdir}/gio/modules
  glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
fi

%posttrans
glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :


%files
%license COPYING
%dir %{_sysconfdir}/dconf
%dir %{_sysconfdir}/dconf/db
%dir %{_sysconfdir}/dconf/profile
%{_libdir}/gio/modules/libdconfsettings.so
%{_libexecdir}/dconf-service
%{_datadir}/dbus-1/services/ca.desrt.dconf.service
%{_bindir}/dconf
%{_libdir}/libdconf.so.*
%{_libdir}/libdconf-dbus-1.so.*
%{_datadir}/bash-completion/completions/dconf
%{_mandir}/man1/dconf-service.1.gz
%{_mandir}/man1/dconf.1.gz
%{_mandir}/man7/dconf.7.gz
%config(noreplace) %{_sysconfdir}/dconf/profile/user
%dir %{_sysconfdir}/dconf
%dir %{_sysconfdir}/dconf/profile
%dir %{_sysconfdir}/dconf/db
%dir %{_sysconfdir}/dconf/db/local.d
%dir %{_sysconfdir}/dconf/db/local.d/locks
%dir %{_sysconfdir}/dconf/db/site.d
%dir %{_sysconfdir}/dconf/db/site.d/locks
%dir %{_sysconfdir}/dconf/db/distro.d
%dir %{_sysconfdir}/dconf/db/distro.d/locks

%files devel
%{_includedir}/dconf
%{_libdir}/libdconf.so
%{_libdir}/pkgconfig/dconf.pc
%{_libdir}/libdconf-dbus-1.so
%{_datadir}/gtk-doc/html/dconf
%{_datadir}/vala

%changelog
* Fri Sep 14 2018 Marek Kasik <mkasik@redhat.com> - 0.26.0-3
- Check mtimes of files in /etc/dconf/db/*.d/ directories
- when running "dconf update"
- Resolves: #1626372

* Mon Mar  6 2017 Marek Kasik <mkasik@redhat.com> - 0.26.0-2
- Restore permissions on updated database
- Resolves: #1281253

* Fri Feb 10 2017 Marek Kasik <mkasik@redhat.com> - 0.26.0-1
- Update to 0.26.0
- Remove editor subpackage
- Return libdbus-1 library (not header or pkgconfig files)
- Resolves: #1386841

* Tue Mar 24 2015 Marek Kasik <mkasik@redhat.com> - 0.22.0-2
- Remove unused patches
- Resolves: #1174448

* Fri Sep 19 2014 Kalev Lember <kalevlember@gmail.com> - 0.22.0-1
- Update to 0.22.0
- Resolves: #1174448

* Fri Apr  4 2014 Marek Kasik <mkasik@redhat.com> - 0.16.0-6
- Don't hang shutdown
- Resolves: #1082994

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 0.16.0-5
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.16.0-4
- Mass rebuild 2013-12-27

* Wed Jul 31 2013 Ray Strode <rstrode@redhat.com> 0.16.0-3
- Add system dbs for distro, site, and machine local dconf databases
  Resolves: #990630

* Tue Jun 25 2013 Matthias Clasen <mclasen@redhat.com> - 0.16.0-2
- Fix a frequent crash (#975687)

* Mon Mar 25 2013 Kalev Lember <kalevlember@gmail.com> - 0.16.0-1
- Update to 0.16.0

* Mon Feb 11 2013 Kalev Lember <kalevlember@gmail.com> - 0.15.3-1
- Update to 0.15.3
- Install the HighContrast icons and update the icon cache scriptlets to take
  this into account

* Sat Dec 22 2012 Rex Dieter <rdieter@fedoraproject.org> - 0.15.2-2
- -devel: drop Requires: glib2-devel, already gets pulled in via pkgconfig deps
- -editor: add icon scriptlets
- tighten subpkg deps via %%{_isa}

* Tue Nov 20 2012 Richard Hughes <hughsient@gmail.com> - 0.15.2-1
- Update to 0.15.2

* Fri Nov 09 2012 Kalev Lember <kalevlember@gmail.com> - 0.15.0-3
- Move some of the rpm scriptlets back to %%posttrans
  (glib-compile-schemas, icon cache)

* Thu Nov  8 2012 Marek Kasik <mkasik@redhat.com> - 0.15.0-2
- Move dconf-editor's man page to the dconf-editor sub-package

* Wed Nov  7 2012 Marek Kasik <mkasik@redhat.com> - 0.15.0-1
- Update to 0.15.0
- Remove upstreamed patch

* Wed Nov  7 2012 Marek Kasik <mkasik@redhat.com> - 0.14.0-4
- Move %%posttrans commands to %%post (rpmlint related)

* Wed Nov  7 2012 Marek Kasik <mkasik@redhat.com> - 0.14.0-3
- Update License field
- Update Source URL
- Add link of corresponding bug for the memory leak patch

* Wed Nov  7 2012 Marek Kasik <mkasik@redhat.com> - 0.14.0-2.1
- Merge spec-file fixes from f18 branch

* Sun Oct 21 2012 Matthias Clasen <mclasen@redhat.com> - 0.14.0-2
- Fix a memory leak
- Update to 0.14.0

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 17 2012 Richard Hughes <hughsient@gmail.com> - 0.13.4-1
- Update to 0.13.4

* Thu Jun 07 2012 Richard Hughes <hughsient@gmail.com> - 0.13.0-2
- Add missing file to file list.

* Thu Jun 07 2012 Richard Hughes <hughsient@gmail.com> - 0.13.0-1
- Update to 0.13.0

* Sat May 05 2012 Kalev Lember <kalevlember@gmail.com> - 0.12.1-1
- Update to 0.12.1

* Tue Mar 27 2012 Kalev Lember <kalevlember@gmail.com> - 0.12.0-1
- Update to 0.12.0

* Tue Mar 20 2012 Kalev Lember <kalevlember@gmail.com> - 0.11.7-1
- Update to 0.11.7

* Fri Mar  9 2012 Matthias Clasen <mclasen@redhat.com> - 0.11.6-1
- Update to 0.11.6

* Mon Feb  6 2012 Matthias Clasen <mclasen@redhat.com> - 0.11.5-1
- Update to 0.11.5

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.11.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Nov 21 2011 Matthias Clasen <mclasen@redhat.com> - 0.11.2-1
- Update to 0.11.2

* Fri Nov  4 2011 Matthias Clasen <mclasen@redhat.com> - 0.11.0-2
- Fix a typo (#710700)

* Wed Nov  2 2011 Matthias Clasen <mclasen@redhat.com> - 0.11.0-1
- Update to 0.11.0

* Mon Sep 26 2011 Ray <rstrode@redhat.com> - 0.10.0-1
- Update to 0.10.0

* Mon Sep 19 2011 Matthias Clasen <mclasen@redhat.com> - 0.9.1-1
- Update to 0.9.1

* Tue Jul 26 2011 Matthias Clasen <mclasen@redhat.com> - 0.9.0-1
- Update to 0.9.0

* Wed May 11 2011 Tomas Bzatek <tbzatek@redhat.com> - 0.7.5-1
- Update to 0.7.5

* Fri May  6 2011 Matthias Clasen <mclasen@redhat.com> - 0.7.4-1
- Update to 0.7.4

* Wed Apr  6 2011 Matthias Clasen <mclasen@redhat.com> - 0.7.3-2
- Fix a crash in dconf-editor

* Tue Mar 22 2011 Tomas Bzatek <tbzatek@redhat.com> - 0.7.3-1
- Update to 0.7.3

* Thu Feb 10 2011 Matthias Clasen <mclasen@redhat.com> - 0.7.2-3
- Rebuild for newer gtk

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Feb  5 2011 Matthias Clasen <mclasen@redhat.com> - 0.7.2-1
- Update to 0.7.2

* Wed Feb  2 2011 Matthias Clasen <mclasen@redhat.com> - 0.7.1-1
- Update to 0.7.1

* Mon Jan 17 2011 Matthias Clasen <mclasen@redhat.com> - 0.7-1
- Update to 0.7

* Wed Sep 29 2010 jkeating - 0.5.1-2
- Rebuilt for gcc bug 634757

* Tue Sep 21 2010 Matthias Clasen <mclasen@redhat.com> - 0.5.1-1
- Update to 0.5.1

* Thu Aug  5 2010 Matthias Clasen <mclasen@redhat.com> - 0.5-2
- Fix up shared library symlinks (#621733)

* Tue Aug  3 2010 Matthias Clasen <mclasen@redhat.com> - 0.5-1
- Update to 0.5

* Mon Jul 12 2010 Matthias Clasen <mclasen@redhat.com> - 0.4.2-1
- Update to 0.4.2

* Wed Jun 30 2010 Colin Walters <walters@verbum.org> - 0.4.1-2
- Changes to support snapshot builds

* Sat Jun 26 2010 Matthias Clasen <mclasen@redhat.com> 0.4.1-1
- Update to 0.4.1
- Include dconf-editor (in a subpackage)

* Wed Jun 23 2010 Matthias Clasen <mclasen@redhat.com> 0.4-2
- Rebuild against glib 2.25.9

* Sat Jun 12 2010 Matthias Clasen <mclasen@redhat.com> 0.4-1
- Update to 0.4

* Tue Jun 08 2010 Richard Hughes <rhughes@redhat.com> 0.3.2-0.1.20100608
- Update to a git snapshot so that users do not get a segfault in every
  application using GSettings.

* Wed Jun 02 2010 Bastien Nocera <bnocera@redhat.com> 0.3.1-2
- Rebuild against latest glib2

* Mon May 24 2010 Matthias Clasen <mclasen@redhat.com> 0.3.1-1
- Update to 0.3.1
- Add a -devel subpackage

* Fri May 21 2010 Matthias Clasen <mclasen@redhat.com> 0.3-3
- Make batched writes (e.g. with delayed settings) work

* Thu May 20 2010 Matthias Clasen <mclasen@redhat.com> 0.3-2
- Make the registration of the backend work

* Wed May 19 2010 Matthias Clasen <mclasen@redhat.com> 0.3-1
- Initial packaging
