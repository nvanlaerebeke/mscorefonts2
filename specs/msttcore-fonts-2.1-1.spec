%define fontname msttcore

%define fontdir %{_datadir}/fonts/%{fontname} 

%define font_files andale32.exe arial32.exe arialb32.exe comic32.exe courie32.exe georgi32.exe impact32.exe times32.exe trebuc32.exe webdin32.exe verdan32.exe

%define update_files EUupdate.EXE

%define download_file wd97vwr32.exe

Summary: TrueType core fonts for the web
Name: %{fontname}-fonts
Obsoletes: msttcorefonts
#Provides: msttcorefonts
Version: 2.1
Release: 1
License: GPL
Group: User Interface/X
BuildArch: noarch
Requires: curl
Requires: cabextract
Requires: xorg-x11-font-utils
Requires: fontconfig
Packager: Rob Janes <janes.rob gmail com>
URL: http://corefonts.sourceforge.net/

%description
The TrueType core fonts for the web that was once available from
http://www.microsoft.com/typography/fontpack/. The src rpm is cleverly
constructed so that the actual fonts are downloaded from Sourceforge's site
at build time. Therefore this package technically does not 'redistribute'
the fonts, it just makes it easy to install them on a linux system.

%install
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
cd %{name}/fonts

mkdir -p $RPM_BUILD_ROOT/%{fontdir}
echo not-empty > $RPM_BUILD_ROOT/%{fontdir}/fonts.dir 
echo not-empty > $RPM_BUILD_ROOT/%{fontdir}/fonts.scale 

mkdir -p $RPM_BUILD_ROOT/etc/X11/xorg.conf.d/
cat -> $RPM_BUILD_ROOT/etc/X11/xorg.conf.d/09-msttcore-fontpath.conf <<'EOT'
Section "Files"
  FontPath "%{fontdir}"
EndSection
EOT

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%pre
TMP=/tmp/$$%{name}
echo "Using tmp directory $TMP" >&2
mkdir -p $TMP/downloads
cd $TMP/downloads

mirror=http://downloads.sourceforge.net/corefonts
mirror_update=http://downloads.sourceforge.net/mscorefonts2

andale32_md5="cbdc2fdd7d2ed0832795e86a8b9ee19a"
arial32_md5="9637df0e91703179f0723ec095a36cb5"
arialb32_md5="c9089ae0c3b3d0d8c4b0a95979bb9ff0"
comic32_md5="2b30de40bb5e803a0452c7715fc835d1"
courie32_md5="4e412c772294403ab62fb2d247d85c60"
georgi32_md5="4d90016026e2da447593b41a8d8fa8bd"
impact32_md5="7907c7dd6684e9bade91cff82683d9d7"
times32_md5="ed39c8ef91b9fb80f76f702568291bd5"
trebuc32_md5="0d7ea16cac6261f8513a061fbfcdb2b5"
webdin32_md5="230a1d13a365b22815f502eb24d9149b"
verdan32_md5="12d2a75f8156e10607be1eaa8e8ef120"
wd97vwr32_md5="efa72d3ed0120a07326ce02f051e9b42"
EUupdate_md5="79d4277864cee0269af46c78ac2ce8d2"

download_files="%{font_files} %{download_file} mirror_update %{update_files}"

failures=0

function check_file {
  local file="$1"
  found=no

  if [ ! -e "$file" ] || [ ! -f "$file" ] || [ ! -s "$file" ]; then
    return 1
  fi

  local variable_name=`basename "$file" | sed -e 's/\..*$//'`_md5
  local stored_checksum
  eval stored_checksum=\$$variable_name
  local computed_checksum=`md5sum < "$file" | cut -f1 -d" "`
  if [ "$stored_checksum" = "$computed_checksum" ]; then
    found=yes
    return 0
  else
    echo "$file checksum does not match: should be $stored_checksum, is $computed_checksum" >&2
    found=no
    return 9
  fi
}

function download_file {
  local mirror="$1" file="$2"
  if type wget > /dev/null 2>&1; then
    wget --timeout=5 -O $file $mirror/$file
  elif type curl > /dev/null 2>&1; then
    curl -R -L -o "$file" --connect-timeout 5 "$mirror/$file"
  fi
}

set +e # all errors are checked

current_mirror="$mirror"
for df in $download_files
do
  case "$df" in
  mirror_update) current_mirror="$mirror_update"; continue ;;
  esac

  failures=0
  found=no
  while [ $found != yes ]
  do
    check_file $df
    rc=$?
    if [ $rc -gt 0 ]; then # fail to find
      [ -e "$df" ] && rm -f "$df"

      if [ $failures -gt 0 ]; then
        if [ $rc -eq 1 ]; then
          echo "$file does not exist" >&2
        fi
      fi
    fi

    if [ $found != yes ]; then
      if [ $failures -gt 5 ]; then
        echo "failed to download $mirror/$df too many times." >&2
        exit 2
      elif [ $failures -gt 0 ]; then
        echo "failed to download $mirror/$df" >&2
      fi
      failures=`expr $failures + 1`

      download_file "$current_mirror" "$df"
    else
      cabextract --lowercase -F '*.ttf' --directory=%{fontdir} "$df"
      case "$df" in
      wd97vwr32.exe)
        cabextract --lowercase -F 'viewer1.cab' "$df"
        cabextract --lowercase -F '*.ttf' --directory=%{fontdir} viewer1.cab
        rm -f viewer1.cab
        ;;
      esac
      rm -f "$df"
    fi
  done
done

cd -
[ -d "$TMP" ] && rm -rf "$TMP"

%post
mkfontscale %{fontdir}
mkfontdir %{fontdir}

if [ -x %{_bindir}/fc-cache ]; then
   %{_bindir}/fc-cache -f -v || :
fi

# add fontdir temporarily, the 09-msttcore-fontpath.conf does it permanently but you have to logoff and on
xset fp+ %{fontdir} || :
xset fp rehash || :

%postun
if [ "$1" = "0" ]; then
  counter=0
  for ff in %{fontdir}/*.ttf; do
    if [ -f "$ff" ]; then
      if [ $counter -eq 0 ]; then
        echo "Removing ttf files in %{fontdir}" >&2
      fi

      rm -f "$ff"

      counter=`expr $counter + 1`
    fi
  done
  if [ -x %{_bindir}/fc-cache ]; then
    %{_bindir}/fc-cache -f -v || :
  fi

  xset -fp %{fontdir} || :
  xset fp rehash || :
fi

%files
%defattr(-,root,root,-)
%attr(-,root,root) %{fontdir}
/etc/X11/xorg.conf.d/09-msttcore-fontpath.conf

%changelog
* Sat Sep 8 2012  Rob Janes <janes.rob gmail com> 2.1-1
- added EUupdate.EXE European Union Expansion Update circa May 2007
- generates distributable rpm that downloads and unpacks the fonts at
  install time, not rpmbuild time
- available at https://downloads.sourceforge.net/project/mscorefonts2/specs/msttcore-fonts-2.1-1.spec

* Sat Sep 8 2012  Rob Janes <janes.rob gmail com> 2.0-7
- refactored sourceforge mirror stuff
- replaced wget with curl, which seems to be installed by default on fedora
- replaced ttmkfdir with mkfontscale and mkfontdir.  This creates fonts.dir file
  for the core X font system.  ttmkfdir has been supersceded by mkfontdir - they
  both create fonts.dir but mkfontdir is part of xorg-x11-font-utils.
- removed 09-msttcorefonts.conf and refactored fc-cache lines.  fc-cache walks subdirectories
  so the 09-msttcorefonts.conf to add the /usr/share/font/msttcore is redundant.  fc-cache
  indexes for the Xft font system, not the legacy core X font system.
- added 09-msttcore-fontpath.conf to /etc/X11/xorg.conf.d for core X font system
- added xset fp+ to add the fontdirectory to core X font for the current session so the installer
  doesn't have to relogin.
- available at https://downloads.sourceforge.net/project/mscorefonts2/specs/msttcore-fonts-2.0-7.spec

* Mon Aug 15 2011  Dennis Johnson
- BuildRequires ttmkfdir, cabextract, wget
- removes Requires
- fixes sourceforge mirror
- generates 09-msttcorefonts.conf
- restores call to ttmkfdir in %install section
- available from http://fenris02.fedorapeople.org/msttcore-fonts-2.0-6.spec

* Sat Dec 11 2010  Hnr Kordewiner <hnr@kordewiner.com> 2.0-5
- move 09-msttcorefonts.conf to this spec file
- drop %{ttmkfdir} - again
- msttcore fonts history site setup at http://moin.kordewiner.com/helpdesk/fedora/mscorefonts
- available from http://moin.kordewiner.com/helpdesk/fedora/mscorefonts?action=AttachFile&do=get&target=msttcore-fonts-2.0-5.spec

* Mon Jun 07 2010 Zied FAKHFAKH <fzied@dottn.com> 2.0-3
- removed chkfontpath dependency for Fedora >= 9
- removed prerun and post chkconfig reference
- divergent development, same purpose as Andrew Bartlett's but derived from Noa Resare's 2.0-1
- available from http://moin.kordewiner.com/helpdesk/fedora/mscorefonts?action=AttachFile&do=get&target=msttcorefonts-2.0-3.spec

* Tue Jun 16 2009  Dennis Johnson
- Provides msttcorefonts
- Requires ttmkfdir, cabextract
- restores call to ttmkfdir in %install section
- available from http://fenris02.fedorapeople.org/msttcore-fonts-2.0-4.spec

* Wed Jun 25 2008  Muayyad Saleh Alsadi <alsadi gmail com> 2.0-3
- drop %{ttmkfdir} completely 

* Mon Feb 18 2008 Andrew Bartlett <abartlet samba org> 2.0-2
- Make work with Fedora 9 fonts system
- available from http://moin.kordewiner.com/helpdesk/fedora/mscorefonts?action=AttachFile&do=get&target=msttcorefonts-2.0-2.spec

* Sun May 07 2006 Noa Resare <noa resare com> 2.0-1
- checksums downloads
- random mirror
- use redistributable word 97 viewer as source for tahoma.ttf
- available from http://corefonts.sourceforge.net/msttcorefonts-2.0-1.spec

* Mon Mar 31 2003 Daniel Resare <noa resare com> 1.3-4
- updated microsoft link
- updated sourceforge mirrors

* Mon Nov 25 2002 Daniel Resare <noa resare com> 1.3-3
- the install dir is now deleted when the package is uninstalled
- executable permission removed from the fonts
- executes fc-cache after install if it is available

* Thu Nov 07 2002 Daniel Resare <noa resare com> 1.3-2
- Microsoft released a new service-pack. New url for Tahoma font.

* Thu Oct 24 2002 Daniel Resare <noa resare com> 1.3-1
- removed python hack
- removed python hack info from description
- made tahoma inclusion depend on define
- added some info on the ttmkfdir define

* Tue Aug 27 2002 Daniel Resare <noa resare com> 1.2-3
- fixed spec error when tahoma is not included 

* Tue Aug 27 2002 Daniel Resare <noa resare com> 1.2-2
- removed tahoma due to unclear licensing
- parametrized ttmkfdir path (for mandrake users)
- changed description text to reflect the new microsoft policy

* Thu Aug 15 2002 Daniel Resare <noa resare com> 1.2-1
- changed distserver because microsoft no longer provides them

* Tue Apr 09 2002 Daniel Resare <noa resare com> 1.1-3
- fixed post/preun script to actually do what they were supposed to do

* Tue Mar 12 2002 Daniel Resare <noa resare com> 1.1-2
- removed cabextact from this package
- added tahoma font from ie5.5 update

* Fri Aug 25 2001 Daniel Resare <noa metamatrix se>
- initial version

