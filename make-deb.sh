#!/bin/bash

APP=qsologbook
VER=0.1
REL=1
PKGDIR=build/${APP}_${VER}-${REL}

mkdir -p $PKGDIR/DEBIAN
mkdir -p $PKGDIR/usr/bin
mkdir -p $PKGDIR/usr/share/${APP}
mkdir -p $PKGDIR/usr/share/applications
mkdir -p $PKGDIR/usr/share/icons/hicolor/256x256/apps
mkdir -p $PKGDIR/usr/share/doc/${APP}


# Project files:
cp QsoLogBook.py \
   Cat.py \
   ConfigWindow.py \
   Crypto.py \
   LastQSOs.py \
   LogDatabase.py \
   Lotw.py \
   QrzApi.py \
   Qso.py \
   QsoLogBook.py \
   config.ini \
   $PKGDIR/usr/share/${APP}/


# Icon (PNG 256x256)
cp qsologbook.png $PKGDIR/usr/share/icons/hicolor/256x256/apps/


# Launcher
cp qsologbook $PKGDIR/usr/bin/
chmod 0755 $PKGDIR/usr/bin/${APP}


# Debian Control file
cat > $PKGDIR/DEBIAN/control << 'EOF'
Package: qsologbook
Version: 0.3-1
Section: utils
Priority: optional
Architecture: all
Maintainer: John M. Belstner <john@w9en.com>
Description: QsoLogBook - Amateur Radio Logbook Application (Tkinter + SQLite)
 Depends: python3 (>= 3.9), python3-tk, python3-requests, python3-cryptography, python3-serial, tqsl, desktop-file-utils, hicolor-icon-theme
EOF


# Debian Post-install and post-remove files
cat > $PKGDIR/DEBIAN/postinst << 'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 0755 $PKGDIR/DEBIAN/postinst

cat > $PKGDIR/DEBIAN/postrm << 'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -q /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 0755 $PKGDIR/DEBIAN/postrm


# Documentation
gzip -9c << 'EOF' > $PKGDIR/usr/share/doc/${APP}/changelog.Debian.gz
qsologbook (0.3-1) stable; urgency=low

  * Initial release.

 -- John M. Belstner <john@w9en.com>  Sat, 11 Oct 2025 12:00:00 -0700
EOF

cat > $PKGDIR/usr/share/doc/${APP}/copyright << 'EOF'
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: QsoLogBook
Source: https://github.com/john-belstner/QsoLogBook

Files: *
Copyright: 2025 John M. Belstner
License: GPL-3.0
EOF


# Create the .deb file
fakeroot dpkg-deb --build $PKGDIR

