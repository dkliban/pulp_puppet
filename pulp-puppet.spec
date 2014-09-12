# Copyright (c) 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0


%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

%if 0%{?rhel} == 5
%define pulp_admin 0
%define pulp_server 0
%define pulp_puppet_tools 0
%else
%define pulp_admin 1
%define pulp_server 1
%define pulp_puppet_tools 1
%endif # End RHEL 5 if block

# ---- Pulp (puppet) -----------------------------------------------------------

Name: pulp-puppet
Version: 2.5.0
Release: 0.1.alpha%{?dist}
%define nondist_release %(echo %{release} | sed 's/%{?dist}//')
Summary: Support for Puppet content in the Pulp platform
Group: Development/Languages
License: GPLv2
URL: https://fedorahosted.org/pulp/
Source0: https://github.com/pulp/pulp_puppet/archive/%{name}-%{version}-%{nondist_release}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  rpm-python

%description
Provides a collection of platform plugins, client extensions and agent
handlers that provide Puppet support.

%prep
%setup -q

%build
pushd pulp_puppet_common
%{__python} setup.py build
popd

%if %{pulp_admin}
pushd pulp_puppet_extensions_admin
%{__python} setup.py build
popd
%endif # End pulp_admin if block

pushd pulp_puppet_extensions_consumer
%{__python} setup.py build
popd

%if %{pulp_server}
pushd pulp_puppet_plugins
%{__python} setup.py build
popd
%endif # End pulp_server if block

pushd pulp_puppet_handlers
%{__python} setup.py build
popd

%if %{pulp_puppet_tools}
pushd pulp_puppet_tools
%{__python} setup.py build
popd
%endif # End pulp_puppet_tools if block

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/%{_sysconfdir}/pulp/

pushd pulp_puppet_common
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd

%if %{pulp_admin}
pushd pulp_puppet_extensions_admin
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd

mkdir -p %{buildroot}/%{_usr}/lib/pulp/admin/extensions

cp -R pulp_puppet_extensions_admin/etc/pulp %{buildroot}/%{_sysconfdir}
%endif # End pulp_admin if block

pushd pulp_puppet_extensions_consumer
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd

%if %{pulp_server}
pushd pulp_puppet_plugins
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd

mkdir -p %{buildroot}/%{_sysconfdir}/pulp/vhosts80
mkdir -p %{buildroot}/srv/pulp
mkdir -p %{buildroot}/%{_usr}/lib/pulp/plugins/types
mkdir -p %{buildroot}/%{_var}/lib/pulp/published/puppet/http
mkdir -p %{buildroot}/%{_var}/lib/pulp/published/puppet/https

cp -R pulp_puppet_plugins/etc/httpd %{buildroot}/%{_sysconfdir}
cp pulp_puppet_plugins/etc/pulp/vhosts80/puppet.conf %{buildroot}/%{_sysconfdir}/pulp/vhosts80/
# WSGI app
cp -R pulp_puppet_plugins/srv/pulp/puppet_forge_post33_api.wsgi %{buildroot}/srv/pulp/
cp -R pulp_puppet_plugins/srv/pulp/puppet_forge_pre33_api.wsgi %{buildroot}/srv/pulp/
# Types
cp -R pulp_puppet_plugins/pulp_puppet/plugins/types/* %{buildroot}/%{_usr}/lib/pulp/plugins/types/
%endif # End pulp_server if block

pushd pulp_puppet_handlers
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd

%if %{pulp_puppet_tools}
pushd pulp_puppet_tools
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd
%endif # End pulp_puppet_tools if block

# Directories
mkdir -p %{buildroot}/%{_sysconfdir}/pulp/agent/conf.d
mkdir -p %{buildroot}/%{_usr}/lib/pulp/agent/handlers
mkdir -p %{buildroot}/%{_bindir}

# Agent Handlers
cp pulp_puppet_handlers/etc/pulp/agent/conf.d/* %{buildroot}/%{_sysconfdir}/pulp/agent/conf.d/

# Remove tests
rm -rf %{buildroot}/%{python_sitelib}/test

%clean
rm -rf %{buildroot}


# define required pulp platform version.
%global pulp_version %{version}


# ---- Puppet Common -----------------------------------------------------------

%package -n python-pulp-puppet-common
Summary: Pulp Puppet support common library
Group: Development/Languages
Requires: python-pulp-common = %{pulp_version}
Requires: python-setuptools

%description -n python-pulp-puppet-common
A collection of modules shared among all Puppet components.

%files -n python-pulp-puppet-common
%defattr(-,root,root,-)
%dir %{python_sitelib}/pulp_puppet
%{python_sitelib}/pulp_puppet/__init__.py*
%{python_sitelib}/pulp_puppet/common/
%dir %{python_sitelib}/pulp_puppet/extensions
%{python_sitelib}/pulp_puppet/extensions/__init__.py*
%{python_sitelib}/pulp_puppet_common*.egg-info
%doc COPYRIGHT LICENSE AUTHORS


# ---- Plugins -----------------------------------------------------------------
%if %{pulp_server}
%package plugins
Summary: Pulp Puppet plugins
Group: Development/Languages
Requires: python-pulp-common = %{pulp_version}
Requires: python-pulp-puppet-common = %{pulp_version}
Requires: pulp-server = %{pulp_version}
Requires: python-semantic-version >= 2.2.0
Requires: python-setuptools
Requires: python-pycurl

%description plugins
Provides a collection of platform plugins that extend the Pulp platform
to provide Puppet specific support.

%files plugins

%defattr(-,root,root,-)
%{_sysconfdir}/pulp/vhosts80/puppet.conf
%{python_sitelib}/pulp_puppet/forge/
%{python_sitelib}/pulp_puppet/plugins/
%config(noreplace) %{_sysconfdir}/httpd/conf.d/pulp_puppet.conf
%{_usr}/lib/pulp/plugins/types/puppet.json
%{python_sitelib}/pulp_puppet_plugins*.egg-info
/srv/pulp/puppet_forge_post33_api.wsgi
/srv/pulp/puppet_forge_pre33_api.wsgi

%defattr(-,apache,apache,-)
%{_var}/lib/pulp/published/puppet/

%doc COPYRIGHT LICENSE AUTHORS
%endif # End pulp_server if block


# ---- Admin Extensions --------------------------------------------------------
%if %{pulp_admin}
%package admin-extensions
Summary: The Puppet admin client extensions
Group: Development/Languages
Requires: python-pulp-common = %{pulp_version}
Requires: python-pulp-puppet-common = %{pulp_version}
Requires: pulp-admin-client = %{pulp_version}
Requires: python-setuptools
Obsoletes: python-pulp-puppet-extension

%description admin-extensions
A collection of extensions that supplement and override generic admin
client capabilites with Puppet specific features.

%files admin-extensions
%defattr(-,root,root,-)
%{_sysconfdir}/pulp/admin/conf.d/puppet.conf
%{python_sitelib}/pulp_puppet/extensions/admin/
%{python_sitelib}/pulp_puppet_extensions_admin*.egg-info
%doc COPYRIGHT LICENSE AUTHORS
%endif # End pulp_admin if block


# ---- Consumer Extensions --------------------------------------------------------

%package consumer-extensions
Summary: The Puppet consumer client extensions
Group: Development/Languages
Requires: python-pulp-puppet-common = %{pulp_version}
Requires: pulp-consumer-client = %{pulp_version}
Requires: python-setuptools

%description consumer-extensions
A collection of extensions that supplement generic consumer
client capabilites with Puppet specific features.

%files consumer-extensions
%defattr(-,root,root,-)
%{python_sitelib}/pulp_puppet/extensions/consumer/
%{python_sitelib}/pulp_puppet_extensions_consumer*.egg-info
%doc COPYRIGHT LICENSE AUTHORS

# ---- Agent Handlers ----------------------------------------------------------

%package handlers
Summary: Pulp agent puppet handlers
Group: Development/Languages
Requires: python-pulp-agent-lib = %{pulp_version}
Requires: python-pulp-common = %{pulp_version}
Requires: puppet >= 2.7.14

%description handlers
A collection of handlers that provide Puppet specific
functionality within the Pulp agent.  This includes Puppet install, update,
uninstall, bind, and unbind.

%files handlers
%defattr(-,root,root,-)
%{python_sitelib}/pulp_puppet/handlers/
%{_sysconfdir}/pulp/agent/conf.d/puppet_bind.conf
%{_sysconfdir}/pulp/agent/conf.d/puppet_module.conf
%{python_sitelib}/pulp_puppet_handlers*.egg-info
%doc COPYRIGHT LICENSE AUTHORS


# ---- Tools -----------------------------------------------------------------
%if %{pulp_puppet_tools}
%package tools
Summary: Pulp puppet tools
Group: Development/Languages
Requires: puppet >= 2.7
Requires: git >= 1.7

%description tools
A collection of tools used to manage puppet modules.

%files tools
%defattr(-,root,root,-)
%{python_sitelib}/pulp_puppet/tools/
%{python_sitelib}/pulp_puppet_tools*.egg-info
%{_bindir}/pulp-puppet-module-builder
%doc COPYRIGHT LICENSE AUTHORS
%endif # End pulp_puppet_tools if block


%changelog
* Tue Sep 09 2014 Randy Barlow <rbarlow@redhat.com> 2.5.0-0.1.alpha
- 1131062 - propogate cancelation even when download exception occurs
  (cduryee@redhat.com)
- 1128274 - Puppet module sync against a directory now updates the progress
  report (jcline@redhat.com)
- 1092572 - Publish puppet files before removing the existing files so that
  there is less time when the puppet modules are not available during a
  republish. (bcourt@redhat.com)
- 1123446 - Syncing against a directory uses 'modulename' rather than
  'authorname-modulename' as the module name (jcline@redhat.com)

* Thu Sep 04 2014 Randy Barlow <rbarlow@redhat.com> 2.4.1-0.7.beta
- Pulp rebuild

* Thu Aug 28 2014 Randy Barlow <rbarlow@redhat.com> 2.4.1-0.6.beta
- Pulp rebuild

* Tue Aug 26 2014 Randy Barlow <rbarlow@redhat.com> 2.4.1-0.5.rc1
- Pulp rebuild

* Mon Aug 25 2014 Randy Barlow <rbarlow@redhat.com> 2.4.1-0.4.beta
- 1130312 - Add release notes for 2.4.1. (rbarlow@redhat.com)

* Fri Aug 22 2014 Randy Barlow <rbarlow@redhat.com> 2.4.1-0.3.beta
- Pulp rebuild

* Wed Aug 20 2014 Randy Barlow <rbarlow@redhat.com> 2.4.1-0.2.alpha
- 1123446 - Syncing against a directory uses 'modulename' rather than
  'authorname-modulename' as the module name (jcline@redhat.com)

* Sat Aug 09 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-1
- Pulp rebuild

* Thu Jul 31 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.30.beta
- Pulp rebuild

* Tue Jul 29 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.29.beta
- Pulp rebuild

* Tue Jul 29 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.28.beta
- Pulp rebuild

* Tue Jul 29 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.27.beta
- Pulp rebuild

* Mon Jul 28 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.26.beta
- Pulp rebuild

* Wed Jul 16 2014 Unknown name 2.4.0-0.25.beta
- Pulp rebuild

* Fri Jul 11 2014 Brian Bouterse <bmbouter@gmail.com> 2.4.0-0.24.beta
- Pulp rebuild

* Wed Jun 25 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.23.beta
- Pulp rebuild

* Tue Jun 24 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.22.beta
- Pulp rebuild

* Tue Jun 17 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.21.beta
- Pulp rebuild

* Tue Jun 10 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.20.beta
- 1103311 - Extract any unit_key fields from metadata (daviddavis@redhat.com)

* Thu May 29 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.19.beta
- Pulp rebuild

* Wed May 21 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.18.beta
- 1096931 - slightly changed repo update command behavior to not send empty
  distributor configs (mhrivnak@redhat.com)
- 1051700 - Don't build admin extensions, plugins, or tools on EL 5.
  (rbarlow@redhat.com)

* Tue May 20 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.17.beta
- Pulp rebuild

* Fri May 16 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.16.beta
- Pulp rebuild

* Fri May 16 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.15.beta
- Pulp rebuild

* Thu May 15 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.14.beta
- 1073143 - improved CLI docs for --queries option (mhrivnak@redhat.com)
- 1093429 - Changing parameter name for repo create due to API change
  (mhrivnak@redhat.com)

* Thu May 08 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.13.beta
- 1082802 - Stop downloading modules when canceled. (rbarlow@redhat.com)
- 1091038 - Puppet repo update command needs to extend the generic update repo
  command so that the return value from the server is processed properly.
  (bcourt@redhat.com)

* Fri May 02 2014 Barnaby Court <bcourt@redhat.com> 2.4.0-0.11.beta
- 1090522 - puppet handler requires puppet >= 2.7.14. (jortel@redhat.com)
- 1072580 - Do not use module names in sync reports. (rbarlow@redhat.com)

* Thu Apr 24 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.10.beta
- Pulp rebuild

* Mon Apr 14 2014 Randy Barlow <rbarlow@redhat.com> 2.4.0-0.9.beta
- 1045214 - Enable synchronization over SSL. (rbarlow@redhat.com)

* Mon Apr 07 2014 Barnaby Court <bcourt@redhat.com> 2.4.0-0.8.beta
- Pulp rebuild

* Wed Apr 02 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.7.beta
- Pulp rebuild

* Wed Apr 02 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.7.alpha
- 1074057 - Fix progress report for directory synchronization
  (bcourt@redhat.com)
- 1058500 - fixed puppet distributor to publish to /var/lib/pulp/published
  instead of to /var/www/pulp_puppet (skarmark@redhat.com)

* Thu Mar 13 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.6.alpha
- Pulp rebuild

* Thu Mar 13 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.5.alpha
- Pulp rebuild

* Wed Mar 12 2014 Barnaby Court <bcourt@redhat.com> 2.4.0-0.4.alpha
- Pulp rebuild

* Mon Feb 24 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.3.alpha
- 1014001 - Puppet forge API and handler now support puppet >= 3.3
  (mhrivnak@redhat.com)

* Tue Jan 28 2014 Jeff Ortel <jortel@redhat.com> 2.4.0-0.2.alpha
- 1034978 - Move general formatting for puppet_module copy & remove to the base
  class in pulp (bcourt@redhat.com)
- 1040958 - puppet uploader isn't returning a properly formatted upload report
  (bcourt@redhat.com)

* Thu Dec 12 2013 Jeff Ortel <jortel@redhat.com> 2.4.0-0.1.alpha
- 995076 - make sure to call finalize on the nectar config object
  (jason.connor@gmail.com)
- 1032132 - removed unused progress_report positional argument
  (jason.connor@gmail.com)
- 1024739 - Rename /etc/pulp/vhosts80/pulp_puppet.conf to puppet.conf.
  (rbarlow@redhat.com)
- 1021099 - Rename puppet.conf -> pulp_puppet.conf (bcourt@redhat.com)

* Wed Nov 06 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.29.beta
- Pulp rebuild

* Wed Nov 06 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.28.beta
- Pulp rebuild

* Fri Nov 01 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.27.beta
- 1024739 - Rename /etc/pulp/vhosts80/pulp_puppet.conf to puppet.conf.
  (rbarlow@redhat.com)

* Tue Oct 29 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.26.beta
- Pulp rebuild

* Mon Oct 28 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.25.beta
- 1021099 - Rename puppet.conf -> pulp_puppet.conf (bcourt@redhat.com)

* Wed Oct 23 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.24.beta
- Pulp rebuild

* Fri Oct 18 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.23.beta
- Pulp rebuild

* Wed Oct 16 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.22.beta
- Pulp rebuild

* Tue Oct 15 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.21.beta
- Pulp rebuild

* Mon Oct 14 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.20.beta
- Pulp rebuild

* Fri Oct 11 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.19.beta
- Pulp rebuild

* Thu Oct 10 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.18.beta
- 1014734 - Update documentation to include Puppet 3.3.x incompatibility.
  (bcourt@redhat.com)

* Wed Oct 02 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.17.beta
- Pulp rebuild

* Thu Sep 26 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.16.alpha
- 976435 - load puppet importer config from a file using a common method.
  (bcourt@redhat.com)

* Thu Sep 26 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.15.alpha
- Pulp rebuild

* Wed Sep 18 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.14.alpha
- Pulp rebuild

* Wed Sep 18 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.13.alpha
- 1009114 - create install_path if not already exists. (jortel@redhat.com)
- 1002691 - pass puppet forge host in options. (jortel@redhat.com)
- 975103 - Removing metadata 'types' field from default rendering of puppet
  modules and adding it only when --details flag is specified
  (skarmark@redhat.com)

* Fri Sep 13 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.12.alpha
- Pulp rebuild

* Thu Sep 12 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.11.alpha
- Pulp rebuild

* Thu Sep 12 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.10.alpha
- Pulp rebuild

* Tue Sep 10 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.9.alpha
- Pulp rebuild

* Fri Sep 06 2013 Barnaby Court <bcourt@redhat.com> 2.3.0-0.8.alpha
- 946966 - made the forge-like API honor semantic versioning
  (mhrivnak@redhat.com)
- 915330 - Fix performance degradation of importer and distributor
  configuration validation as the number of repositories increased
  (bcourt@redhat.com)

* Fri Aug 30 2013 Barnaby Court <bcourt@redhat.com> 2.3.0-0.7.alpha
- Pulp rebuild

* Thu Aug 29 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.6.alpha
- Pulp rebuild

* Thu Aug 29 2013 Barnaby Court <bcourt@redhat.com> 2.3.0-0.5.alpha
- Pulp rebuild

* Tue Aug 27 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.4.alpha
- Pulp rebuild

* Tue Aug 27 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.3.alpha
- Pulp rebuild

* Thu Aug 01 2013 Jeff Ortel <jortel@redhat.com> 2.3.0-0.2.alpha
- Purge changelog prior to 2.0 (jortel@redhat.com)

* Tue Jun 04 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.16.alpha
- 968543 - remove conditional in pulp_version macro. (jortel@redhat.com)

* Thu May 30 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.15.alpha
- Pulp rebuild

* Fri May 24 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.14.alpha
- Pulp rebuild

* Thu May 23 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.13.alpha
- Pulp rebuild

* Thu May 23 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.12.alpha
- Pulp rebuild

* Tue May 21 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.11.alpha
- Pulp rebuild

* Mon May 20 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.10.alpha
- Pulp rebuild

* Mon May 20 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.9.alpha
- Pulp rebuild

* Fri May 17 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.8.alpha
- 946966 - an uploaded module can now have a version that includes the '-'
  character. (mhrivnak@redhat.com)

* Mon May 13 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.5.alpha
- Pulp rebuild

* Mon May 13 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.3.alpha
- Pulp rebuild

* Fri Apr 19 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.2.alpha
- Pulp rebuild

* Fri Apr 12 2013 Jeff Ortel <jortel@redhat.com> 2.2.0-0.1.alpha
- 950740 - add support {?dist} in the Release: in .spec files.
  (jortel@redhat.com)

* Mon Mar 04 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.19.alpha
- 902514 - Removed the <VirtualHost> block, which apache was ignoring anyway,
  in favor of using the platform's authoritative one. (mhrivnak@redhat.com)

* Tue Feb 26 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.18.alpha
- Pulp rebuild

* Tue Feb 26 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.17.alpha
- Pulp rebuild

* Mon Feb 25 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.16.alpha
- Pulp rebuild

* Fri Feb 22 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.14.alpha
- Pulp rebuild

* Thu Feb 21 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.13.alpha
- Pulp rebuild

* Tue Feb 19 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.12.alpha
- Pulp rebuild

* Thu Feb 14 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.10.alpha
- Pulp rebuild

* Thu Feb 14 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.9.alpha
- Pulp rebuild

* Wed Feb 13 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.8.alpha
- Pulp rebuild

* Wed Feb 13 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.7.alpha
- Pulp rebuild

* Tue Feb 12 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.5.alpha
- Pulp rebuild

* Tue Feb 12 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.4.alpha
- Pulp rebuild

* Tue Feb 05 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.3.alpha
- Pulp rebuild

* Tue Feb 05 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.2.alpha
- Pulp rebuild

* Sat Jan 19 2013 Jeff Ortel <jortel@redhat.com> 2.1.0-0.1.alpha
- 887372 - importer now gracefully fails when a feed URL is not present in the
  config (mhrivnak@redhat.com)
- 861211 - Adding a "--queries" option to repo create and update that takes a
  CSV list of query terms, and deprecating the previous "--query" option.
  (mhrivnak@redhat.com)
- 887959 - renaming pulp_puppet.conf to puppet.conf (skarmark@redhat.com)
- 887959 - renaming pulp_puppet.conf to puppet.conf (skarmark@redhat.com)
- 887959 - renaming pulp_puppet.conf file to puppet.conf so that it get's
  loaded after pulp_rpm.conf (skarmark@redhat.com)
- 887959 - Removing NameVirtualHost entries from plugin httpd conf files and
  adding it only at one place in main pulp.conf (skarmark@redhat.com)
- 886689 - puppet distributor output from the CLI now includes a relative path
  to the published content. (mhrivnak@redhat.com)
- 882414 - Using an exception from the pulp server that allows a helpful error
  message to be returned to clients. (mhrivnak@redhat.com)
- 882404 - now validating file name format when uploading modules.
  (mhrivnak@redhat.com)
- 882427 - No longer displaying traceback to user when a sync fails to import a
  module (mhrivnak@redhat.com)
- 882419 - adding publish commands to the CLI (mhrivnak@redhat.com)
- 882421 - added unit remove command. (mhrivnak@redhat.com)
- 866491 - Added translation from server-side property name to client-side flag
  (jason.dobies@redhat.com)
- 862290 - Added support for non-Puppet repo listing (jason.dobies@redhat.com)
- 880229 - I think we need to create these as well. (jason.dobies@redhat.com)
- 880229 - Apache needs to be able to write to the publish directories
  (jason.dobies@redhat.com)

* Thu Dec 20 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.19.rc
- Pulp rebuild

* Wed Dec 19 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.19.beta
- Pulp rebuild

* Tue Dec 18 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.18.beta
- 887959 - renaming pulp_puppet.conf to puppet.conf (skarmark@redhat.com)
- 887959 - renaming pulp_puppet.conf to puppet.conf (skarmark@redhat.com)
- 887959 - renaming pulp_puppet.conf file to puppet.conf so that it get's
  loaded after pulp_rpm.conf (skarmark@redhat.com)
- 887959 - Removing NameVirtualHost entries from plugin httpd conf files and
  adding it only at one place in main pulp.conf (skarmark@redhat.com)

* Thu Dec 13 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.17.beta
- Pulp rebuild

* Thu Dec 13 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.15.beta
- 886689 - puppet distributor output from the CLI now includes a relative path
  to the published content. (mhrivnak@redhat.com)
- 882414 - Using an exception from the pulp server that allows a helpful error
  message to be returned to clients. (mhrivnak@redhat.com)
- 882404 - now validating file name format when uploading modules.
  (mhrivnak@redhat.com)
- 882427 - No longer displaying traceback to user when a sync fails to import a
  module (mhrivnak@redhat.com)

* Mon Dec 10 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.14.beta
- Pulp rebuild

* Fri Dec 07 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.13.beta
- Pulp rebuild

* Thu Dec 06 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.12.beta
- 882419 - adding publish commands to the CLI (mhrivnak@redhat.com)
- 882421 - added unit remove command. (mhrivnak@redhat.com)

* Thu Nov 29 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.11.beta
- Pulp rebuild

* Thu Nov 29 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.10.beta
- 866491 - Added translation from server-side property name to client-side flag
  (jason.dobies@redhat.com)
- 862290 - Added support for non-Puppet repo listing (jason.dobies@redhat.com)
- 880229 - I think we need to create these as well. (jason.dobies@redhat.com)
- 880229 - Apache needs to be able to write to the publish directories
  (jason.dobies@redhat.com)

* Mon Nov 26 2012 Jay Dobies <jason.dobies@redhat.com> 2.0.6-0.9.beta
- Pulp rebuild

* Wed Nov 21 2012 Jay Dobies <jason.dobies@redhat.com> 2.0.6-0.8.beta
- Pulp rebuild

* Wed Nov 21 2012 Jay Dobies <jason.dobies@redhat.com> 2.0.6-0.7.beta
- Pulp rebuild

* Tue Nov 20 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.3.beta
- Pulp rebuild

* Mon Nov 12 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.2.beta
- Pulp rebuild

* Mon Nov 12 2012 Jeff Ortel <jortel@redhat.com> 2.0.6-0.1.beta
- Pulp rebuild
