Summary: Simple kernel loader which boots from a FAT filesystem
Name: syslinux
Version: 6.02
Release: 1
License: GPLv2+
Group: System/Boot
URL: http://syslinux.zytor.com/wiki/index.php/The_Syslinux_Project
Source0: http://www.kernel.org/pub/linux/utils/boot/syslinux/%{name}-%{version}.tar.xz
Source101: syslinux-rpmlintrc
Patch0001: 0001-Add-install-all-target-to-top-side-of-HAVE_FIRMWARE.patch
Patch0002: 0002-Don-t-build-efi32.patch

# this is to keep rpmbuild from thinking the .c32 / .com / .0 / memdisk files
# in noarch packages are a reason to stop the build.
%define _binaries_in_noarch_packages_terminate_build 0

ExclusiveArch: %{ix86} x86_64
BuildRequires: nasm >= 0.98.38-1, perl
BuildRequires: libuuid-devel
%ifarch %{ix86}
Requires: mtools, libc.so.6
%define my_cc gcc -m32
%endif
%ifarch x86_64
Requires: mtools
%define my_cc gcc
%endif

# NOTE: extlinux belongs in /sbin, not in /usr/sbin, since it is typically
# a system bootloader, and may be necessary for system recovery.
%define _sbindir /sbin

%description
SYSLINUX is a suite of bootloaders, currently supporting DOS FAT
filesystems, Linux ext2/ext3 filesystems (EXTLINUX), PXE network boots
(PXELINUX), or ISO 9660 CD-ROMs (ISOLINUX).  It also includes a tool,
MEMDISK, which loads legacy operating systems from these media.

%package perl
Summary: Syslinux tools written in perl
Group: Applications/System

%description perl
Syslinux tools written in perl

%package devel
Summary: Headers and libraries for syslinux development.
Group: Development/Libraries

%description devel
Headers and libraries for syslinux development.

%package extlinux
Summary: The EXTLINUX bootloader, for booting the local system.
Group: System/Boot
Requires: syslinux

%description extlinux
The EXTLINUX bootloader, for booting the local system, as well as all
the SYSLINUX/PXELINUX modules in /boot.

%ifarch %{ix86}
%package tftpboot
Summary: SYSLINUX modules in /tftpboot, available for network booting
Group: Applications/Internet
BuildArch: noarch
ExclusiveArch: %{ix86} x86_64
Requires: syslinux

%description tftpboot
All the SYSLINUX/PXELINUX modules directly available for network
booting in the /tftpboot directory.
%endif

%ifarch %{x86_64}
%package efi64
Summary: SYSLINUX binaries and modules for 64-bit UEFI systems
Group: System/Boot

%description efi64
SYSLINUX binaries and modules for 64-bit UEFI systems
%endif

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1
%patch2 -p1

%build
make CC='%{my_cc}' bios clean all
%ifarch %{x86_64}
make CC='%{my_cc}' efi64 clean all
%endif

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_prefix}/lib/syslinux
mkdir -p %{buildroot}%{_includedir}
make CC='%{my_cc}' bios install-all \
	INSTALLROOT=%{buildroot} BINDIR=%{_bindir} SBINDIR=%{_sbindir} \
	LIBDIR=%{_prefix}/lib DATADIR=%{_datadir} \
	MANDIR=%{_mandir} INCDIR=%{_includedir} \
	TFTPBOOT=/tftpboot EXTLINUXDIR=/boot/extlinux \
	LDLINUX=ldlinux.c32
%ifarch %{x86_64}
make CC='%{my_cc}' efi64 install netinstall \
	INSTALLROOT=%{buildroot} BINDIR=%{_bindir} SBINDIR=%{_sbindir} \
	LIBDIR=%{_prefix}/lib DATADIR=%{_datadir} \
	MANDIR=%{_mandir} INCDIR=%{_includedir} \
	TFTPBOOT=/tftpboot EXTLINUXDIR=/boot/extlinux \
	LDLINUX=ldlinux.c32
%endif

mkdir -p %{buildroot}/%{_docdir}/%{name}/sample
install -m 644 sample/sample.* %{buildroot}/%{_docdir}/%{name}/sample/
mkdir -p %{buildroot}/etc
( cd %{buildroot}/etc && ln -s ../boot/extlinux/extlinux.conf . )

# don't ship libsyslinux, at least, not for now
rm -f %{buildroot}%{_prefix}/lib/libsyslinux*
rm -f %{buildroot}%{_includedir}/syslinux.h

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc NEWS README* COPYING 
%doc doc/* 
%doc sample
%doc %{_docdir}/syslinux/sample/sample.msg
%{_mandir}/man1/gethostip*
%{_mandir}/man1/syslinux*
%{_mandir}/man1/extlinux*
%{_bindir}/gethostip
%{_bindir}/isohybrid
%{_bindir}/memdiskfind
%{_bindir}/syslinux
%dir %{_datadir}/syslinux
%dir %{_datadir}/syslinux/dosutil
%{_datadir}/syslinux/dosutil/*
%{_datadir}/syslinux/diag/*
%{_datadir}/syslinux/*.com
%{_datadir}/syslinux/*.c32
%{_datadir}/syslinux/*.bin
%{_datadir}/syslinux/*.0
%{_datadir}/syslinux/memdisk

%files perl
%defattr(-,root,root)
%{_mandir}/man1/lss16toppm*
%{_mandir}/man1/ppmtolss16*
%{_mandir}/man1/syslinux2ansi*
%{_bindir}/keytab-lilo
%{_bindir}/lss16toppm
%{_bindir}/md5pass
%{_bindir}/mkdiskimage
%{_bindir}/ppmtolss16
%{_bindir}/pxelinux-options
%{_bindir}/sha1pass
%{_bindir}/syslinux2ansi
%{_bindir}/isohybrid.pl

%files devel
%defattr(-,root,root)
%dir %{_datadir}/syslinux/com32
%{_datadir}/syslinux/com32/*

%files extlinux
%{_sbindir}/extlinux
%config /etc/extlinux.conf
/boot/extlinux
%exclude /tftpboot

%ifarch %{ix86}
%files tftpboot
/tftpboot
%endif

%ifarch %{x86_64}
%files efi64
%dir %{_datadir}/syslinux/efi64
%{_datadir}/syslinux/efi64
%endif

%post extlinux
# If we have a /boot/extlinux.conf file, assume extlinux is our bootloader
# and update it.
if [ -f /boot/extlinux/extlinux.conf ]; then \
	extlinux --update /boot/extlinux ; \
elif [ -f /boot/extlinux.conf ]; then \
	mkdir -p /boot/extlinux && \
	mv /boot/extlinux.conf /boot/extlinux/extlinux.conf && \
	extlinux --update /boot/extlinux ; \
fi
