%global gittag 5.4.0.201906121030-r
Name:                eclipse-jgit
Version:             5.4.0
Release:             1
Summary:             Eclipse JGit
License:             BSD
URL:                 https://www.eclipse.org/jgit/
Source0:             https://git.eclipse.org/c/jgit/jgit.git/snapshot/jgit-%{gittag}.tar.xz
Patch0:              0001-Ensure-the-correct-classpath-is-set-for-the-jgit-com.patch
Patch1:              0002-Don-t-embed-versions-of-third-party-libs-use-feature.patch
BuildArch:           noarch
ExcludeArch:         s390 %{arm} %{ix86}
BuildRequires:       tycho jgit = %{version}
Requires:            eclipse-platform jgit = %{version}
%description
A pure Java implementation of the Git version control system.

%prep
%setup -n jgit-%{gittag} -q
%patch0 -p1
%patch1 -p1
rm .mvn/maven.config
for p in $(find org.eclipse.jgit.packaging -name pom.xml) ; do
  grep -q dependencies $p && %pom_xpath_remove "pom:dependencies" $p
done
%pom_disable_module org.eclipse.jgit.target org.eclipse.jgit.packaging
%pom_disable_module org.eclipse.jgit.repository org.eclipse.jgit.packaging
%pom_xpath_remove "pom:build/pom:pluginManagement/pom:plugins/pom:plugin/pom:configuration/pom:target" org.eclipse.jgit.packaging/pom.xml
%pom_disable_module org.eclipse.jgit.source.feature org.eclipse.jgit.packaging
%pom_remove_plugin :maven-enforcer-plugin org.eclipse.jgit.packaging
pushd org.eclipse.jgit.packaging
%mvn_package "::pom::" __noinstall
popd

%build
pushd org.eclipse.jgit.packaging
%mvn_build -j
popd

%install
pushd org.eclipse.jgit.packaging
%mvn_install
popd

%files -f org.eclipse.jgit.packaging/.mfiles
%license LICENSE
%doc README.md

%changelog
* Mon Aug 17 2020 yanan li <liyanan032@huawei.com> - 5.4.0-1
- Package init
