%define major	3
%define libname	%mklibname %{name} %{major}
%define devname	%mklibname %{name} -d

%global soversion %(echo %{version}|cut -d. -f1,4)

Summary:	A numerical analysis and data processing library
Name:		alglib
Version:	3.18.0
Release:	3
Group:		System/Libraries
License:	GPLv2+
URL:		https://www.alglib.net/
Source0:	%{url}/translator/re/%{name}-%{version}.cpp.gpl.tgz
# from debian with small changes
Source1:	ALGLIBConfig.cmake
# from debian with small changes
Source2:	CMakeLists.txt
# Extracted from manual.cpp.html
Source3:	bsd.txt

BuildRequires:	cmake
BuildRequires:	ninja

%description
ALGLIB is a cross-platform numerical analysis and data mining library.

ALGLIB features include:
  *  Data analysis (classification/regression, including neural networks)
  *  Optimization and nonlinear solvers
  *  Interpolation and linear/nonlinear least-squares fitting
  *  Linear algebra (direct algorithms, EVD/SVD), direct and iterative
     linear solvers, Fast Fourier Transform and many other algorithms
     (numerical integration, ODEs, statistics, special functions)

#-------------------------------------------------------------------------

%package -n %{libname}
Summary:	Shared %{name} library
Group:		System/Libraries

%description -n %{libname}
ALGLIB is a cross-platform numerical analysis and data mining library.

ALGLIB features include:
  *  Data analysis (classification/regression, including neural networks)
  *  Optimization and nonlinear solvers
  *  Interpolation and linear/nonlinear least-squares fitting
  *  Linear algebra (direct algorithms, EVD/SVD), direct and iterative
     linear solvers, Fast Fourier Transform and many other algorithms
     (numerical integration, ODEs, statistics, special functions)

This package provides the shared %{name} library.

%files -n %{libname}
%license gpl2.txt
%{_libdir}/lib%{name}.so.%{major}{,.*}

#-------------------------------------------------------------------------

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} >= %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
The %{develname} package contains libraries and header files for
developing applications that use %{name}.

%files -n %{devname}
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/cmake/ALGLIB/

#-------------------------------------------------------------------------

%package doc
Summary: 	API documentation for %{name}
License:	BSD
BuildArch:	noarch

%description doc
The %{name}-doc package contains the %{name} API documentation.

%files doc
%license bsd.txt
%doc manual.cpp.html

#-------------------------------------------------------------------------

%prep
%autosetup -p1 -n %{name}-cpp

# cmake files
cp %{SOURCE1} .
cp %{SOURCE2} .

# license
cp %{SOURCE3} .

# set version and soversion in cmake file
sed -i -e 's|\${VERSION}|%{version}|' -e 's|\${SOVERSION}|%{soversion}|' CMakeLists.txt

# Fix permissions and line endings
#chmod 644 gpl2.txt
#chmod 644 manual.cpp.html
sed -i 's|\r||g' manual.cpp.html


%build
# FIXME: disable FMA support to get it pass all tests
%ifarch aarch64
export CXXFLAGS="%{optflags} -ffp-contract=off"
export CFLAGS="%{optflags} -ffp-contract=off"
%endif
#FIXME: without this link fails on znver1
%global _empty_manifest_terminate_build 0
export CXXFLAGS="$CXXFLAGS -O2"
export CFLAGS="$CFLAGS -O2"

%cmake \
	-G Ninja
%ninja_build

%install
%ninja_install -C build

%check
pushd build
LD_LIBRARY_PATH=$PWD ./test_c || false
LD_LIBRARY_PATH=$PWD ./test_i || false
popd

