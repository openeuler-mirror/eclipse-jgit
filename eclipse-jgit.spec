Name:           eclipse-jgit
Version:        5.2.0
Release:        5
Summary:        Java implementation of the Git version control system
License:        BSD
URL:            http://www.eclipse.org/egit/
Source0:        https://git.eclipse.org/c/jgit/jgit.git/snapshot/jgit-5.2.0.201812061821-r.tar.xz

Patch0001:      0001-Ensure-the-correct-classpath-is-set-for-the-jgit-com.patch
Patch0002:      0002-Don-t-embed-versions-of-third-party-libs-use-feature.patch
Patch0003:      0003-Port-to-apache-sshd-2.1.0.patch

BuildArch:      noarch

BuildRequires:  maven-local mvn(args4j:args4j) mvn(com.google.code.gson:gson) mvn(com.googlecode.javaewah:JavaEWAH)
BuildRequires:  mvn(com.jcraft:jsch) mvn(com.jcraft:jzlib) mvn(javax.servlet:javax.servlet-api) mvn(junit:junit)
BuildRequires:  mvn(net.i2p.crypto:eddsa) mvn(org.apache.ant:ant) mvn(org.apache.commons:commons-compress)
BuildRequires:  mvn(org.apache.httpcomponents:httpclient) mvn(org.apache.httpcomponents:httpcore)
BuildRequires:  mvn(org.apache.maven.plugins:maven-antrun-plugin) mvn(org.apache.maven.plugins:maven-clean-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-install-plugin) mvn(org.apache.maven.plugins:maven-shade-plugin)
BuildRequires:  mvn(org.apache.maven.plugins:maven-source-plugin) mvn(org.apache.sshd:sshd-core)
BuildRequires:  mvn(org.apache.sshd:sshd-sftp) mvn(org.bouncycastle:bcprov-jdk15on) >= 1.61 mvn(org.codehaus.mojo:build-helper-maven-plugin)
BuildRequires:  mvn(org.eclipse.jetty:jetty-servlet) mvn(org.hamcrest:hamcrest-library) mvn(org.mockito:mockito-core)
BuildRequires:  mvn(org.osgi:osgi.core) mvn(org.slf4j:slf4j-api) mvn(org.slf4j:slf4j-simple) mvn(org.tukaani:xz) git
BuildRequires:  tycho jgit = %{version}

Requires:       eclipse-platform jzlib bouncycastle >= 1.61 jgit = %{version}-%{release}

%description
A pure Java implementation of the Git version control system.

%package       help
Summary:       Help documentation for %{name}
Provides:      jgit-javadoc = %{version}-%{release}
Obsoletes:     jgit-javadoc < %{version}-%{release}

%description   help
Man pages and other related help documents for %{name}.

%package -n    jgit
Summary:       Java-based command line Git interface

%description -n jgit
Command line Git tool built entirely in Java.

%prep
%autosetup -n jgit-5.2.0.201812061821-r -p1

rm .mvn/maven.config

%pom_remove_dep com.googlecode.javaewah:JavaEWAH
for p in $(find org.eclipse.jgit.packaging -name pom.xml) ; do
  grep -q dependencies $p && %pom_xpath_remove "pom:dependencies" $p
done

%pom_xpath_remove "pom:plugin[pom:artifactId='maven-compiler-plugin']/pom:executions/pom:execution[pom:id='compile-with-errorprone']" pom.xml
%pom_xpath_remove "pom:plugin[pom:artifactId='maven-compiler-plugin']/pom:executions/pom:execution[pom:id='default-compile']/pom:configuration" pom.xml
%pom_xpath_remove "pom:plugin[pom:artifactId='maven-compiler-plugin']/pom:dependencies" pom.xml

%pom_disable_module org.eclipse.jgit.target org.eclipse.jgit.packaging
%pom_disable_module org.eclipse.jgit.repository org.eclipse.jgit.packaging
%pom_xpath_remove "pom:build/pom:pluginManagement/pom:plugins/pom:plugin/pom:configuration/pom:target"   \
                  org.eclipse.jgit.packaging/pom.xml

%pom_disable_module org.eclipse.jgit.source.feature org.eclipse.jgit.packaging
%pom_disable_module org.eclipse.jgit.pgm.source.feature org.eclipse.jgit.packaging

%pom_change_dep -r org.osgi:org.osgi.core org.osgi:osgi.core
%pom_remove_plugin :jacoco-maven-plugin
%pom_remove_plugin :maven-javadoc-plugin
%pom_remove_plugin :maven-enforcer-plugin
%pom_remove_plugin :maven-enforcer-plugin org.eclipse.jgit.packaging
%pom_remove_plugin -r :japicmp-maven-plugin

%pom_remove_plugin org.codehaus.mojo:build-helper-maven-plugin org.eclipse.jgit.pgm

%pom_remove_dep log4j:log4j . org.eclipse.jgit.pgm
%pom_change_dep org.slf4j:slf4j-log4j12 org.slf4j:slf4j-simple . org.eclipse.jgit.pgm

cd org.eclipse.jgit.packaging
%mvn_package "::pom::" __noinstall
cd -
%mvn_package ":*.test" __noinstall

%build

%mvn_build --post install:install -- -Pjavac \
  -Dmaven.repo.local=$(pwd)/org.eclipse.jgit.packaging/.m2 -Dmaven.test.failure.ignore=true

cd org.eclipse.jgit.packaging
%mvn_build -j -- -Dfedora.p2.repos=$(pwd)/.m2
cd -


%install
xmvn-install -R .xmvn-reactor -n jgit -d %{buildroot}
install -dm755 %{buildroot}%{_javadocdir}/jgit
cp -pr .xmvn/apidocs/* %{buildroot}%{_javadocdir}/jgit
echo '%{_javadocdir}/jgit' >>.mfiles-javadoc

cd org.eclipse.jgit.packaging
%mvn_install
cd -

install -Dp -m755 org.eclipse.jgit.pgm/jgit.sh %{buildroot}%{_bindir}/jgit
%{!?_licensedir:%global license %doc}

install -dm 755 %{buildroot}%{_sysconfdir}/ant.d
cat > %{buildroot}%{_sysconfdir}/ant.d/jgit <<EOF
javaewah jzlib jsch jgit/org.eclipse.jgit jgit/org.eclipse.jgit.ant slf4j/slf4j-api slf4j/slf4j-simple httpcomponents/httpcore httpcomponents/httpclient commons-logging commons-codec
EOF
%files -f org.eclipse.jgit.packaging/.mfiles
%doc README.md LICENSE

%files -n jgit -f .mfiles
%doc README.md LICENSE
%{_bindir}/jgit
%config(noreplace) %{_sysconfdir}/ant.d/jgit

%files help -f .mfiles-javadoc

%changelog
* Thu Dec 12 2019 wangzhishun <wangzhishun1@huawei.com> - 5.2.0-5
- Package init
