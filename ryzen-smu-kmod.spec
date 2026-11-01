%global gitname    ryzen_smu
%global giturl     https://github.com/amkillam/%{gitname}
%global gitcommit  d2983668300dd2a598e5a7dc40e71ce0678cc270
%global gitshortcommit %(c=%{gitcommit}; echo ${c:0:7})
%global gitsnapinfo git20260914.%{gitshortcommit}
%global debug_package %{nil}
# (un)define the next line to either build for the newest or all current kernels
#define buildforkernels newest
#define buildforkernels current
%define buildforkernels akmod

# name should have a -kmod suffix
Name:           ryzen-smu-kmod

Version:        0.1.7^%{gitsnapinfo}
Release:        2%{?dist}
Summary:        Driver that exposes the AMD Ryzen SMU

Group:          System Environment/Kernel

License:        GPLv3
URL:            https://github.com/darrencocco/ryzen-smu-kmod
Source0:        %{giturl}/archive/%{gitcommit}.tar.gz#/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  kmodtool
BuildRequires:  make
BuildRequires:  gcc

ExclusiveArch:  x86_64

%description
A Linux kernel driver that exposes access to the SMU (System Management Unit) for certain AMD Ryzen Processors

%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

# Define the userspace tools package
%package -n ryzen-smu
Summary: Userspace tools for ryzen-smu kernel module
Provides: ryzen-smu-kmod-common = %{version}
Requires: ryzen-smu-kmod >= %{version}

%description -n ryzen-smu
Userspace tools and utilities for the ryzen-smu kernel module that provide access to the SMU (System Management Unit) for certain AMD Ryzen Processors.

%prep
%autosetup -n %{gitname}-%{gitcommit} -p 1

# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# print kmodtool output for debugging purposes:
kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

find . -type f -name '*.c' -exec sed -i "s/#VERSION#/%{version}/" {} \+

for kernel_version  in %{?kernel_versions} ; do
  mkdir -p _kmod_build_${kernel_version%%___*}
  cp -a *.c _kmod_build_${kernel_version%%___*}/
  cp -a *.h _kmod_build_${kernel_version%%___*}/
  cp -a Makefile _kmod_build_${kernel_version%%___*}/
done

%build
# Build kernel modules
for kernel_version  in %{?kernel_versions} ; do
  make V=1 %{?_smp_mflags} -C ${kernel_version##*___} M=${PWD}/_kmod_build_${kernel_version%%___*} VERSION=v%{version} modules
done

# Build userspace tools
make -C userspace

%install
# Install kernel modules
for kernel_version in %{?kernel_versions}; do
 mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 install -D -m 755 _kmod_build_${kernel_version%%___*}/ryzen_smu.ko %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
 chmod a+x %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/ryzen_smu.ko
done
%{?akmod_install}

# Install userspace tools
mkdir -p %{buildroot}%{_bindir}
mv userspace/monitor_cpu %{buildroot}%{_bindir}/monitor_cpu

# Files for userspace package
%files -n ryzen-smu
%{_bindir}/monitor_cpu
%doc README.md
%license LICENSE

%changelog
* Sun Nov 01 2026 Darren Cocco <linux.fedora.packaging@darren.cocco.id.au> 0.1.7^git20260914.d298366-2
- Bumped dist number for updated dependencies.

* Mon Sep 14 2026 Darren Cocco <linux.fedora.packaging@darren.cocco.id.au> 0.1.7^git20260914.d298366-1
- Updated to git commit d2983668300dd2a598e5a7dc40e71ce0678cc270, updated support for kernel 7.2+.

* Thu Jul 09 2026 Darren Cocco <linux.fedora.packaging@darren.cocco.id.au> 0.1.7^git20260709.1be4fb1-1
- Updated to git commit 1be4fb1cd9d60b5ddefc2a4201a898766a731400, added support Ryzen AI 9 HX 370.

* Fri May 01 2026 darrencocco
- Initial release
