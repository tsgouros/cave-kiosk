#!/bin/bash
#
# An install script to take the pieces of the kiosk software and
# install them into a given web directory, and pointing to a given
# apps directory.  The script copies the files here into the correct
# place and creates a link to the given apps directory.  Note that the
# web server will require the FollowSymLinks to be turned on.
#
# Usage: install.sh WEBDIR APPDIR PSDFILEPATH
#
# If no arguments are given, the web directory defaults to
# /var/www/html and the apps to ~cavedemo/yurt-kiosk.
#
# 
WEBDIR=${1:-/var/www/html}
APPDIR=${2:-/users/cavedemo/yurt-kiosk}
PSDFILEPATH=${3:-/users/cavedemo/etc/psd.txt}
KIOSKSOURCEDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

echo "from ${KIOSKSOURCEDIR}"
echo "copy to ${WEBDIR}"
echo "link to ${APPDIR}"
echo "password path: ${PSDPATH}"

# This is the external-facing root of the html tree.
HTMLDIR=/kiosk
# KIOSKTARGETDIR is the absolute name of the html root.
KIOSKTARGETDIR=${WEBDIR}${HTMLDIR}
mkdir -p ${KIOSKTARGETDIR}

# Copy all the JS code to the target directory.  Kiosk.js must be edited along 
# the way to insert the password file path.
cp -R ${KIOSKSOURCEDIR}/src/js ${KIOSKTARGETDIR}/
sed -e "s@PSDFILEPATH@${PSDFILEPATH}@g" ${KIOSKSOURCEDIR}/src/js/kiosk.js >${KIOSKTARGETDIR}/js/kiosk.js

# If the password file does not exist in its place, copy in a scratch version.
if [ ! -e $PSDFILEPATH ] ; then
    cp -R ${KIOSKSOURCEDIR}/etc/psd.txt ${PSDFILEPATH} ;
fi

# Copy the Perl code to the target directory, editing along the way.  Also make
# sure the permissions are correct.
sed -e "s@KIOSKTARGETDIR@${KIOSKTARGETDIR}@g" ${KIOSKSOURCEDIR}/src/perl/kiosk.cgi >${KIOSKTARGETDIR}/index.cgi
chmod 775 ${KIOSKTARGETDIR}/index.cgi
sed -e "s@PSDFILEPATH@${PSDFILEPATH}@g" ${KIOSKSOURCEDIR}/src/perl/psd.cgi >${KIOSKTARGETDIR}/psd.cgi
chmod 775 ${KIOSKTARGETDIR}/psd.cgi
cp -R ${KIOSKSOURCEDIR}/src/perl/stderr.cgi ${KIOSKTARGETDIR}/
chmod 775 ${KIOSKTARGETDIR}/stderr.cgi

# Make sure the apps link is set up.
ln -s -f ${APPDIR} ${KIOSKTARGETDIR}/apps

# The image and CSS files can just be copied into place.
cp -R ${KIOSKSOURCEDIR}/css ${KIOSKTARGETDIR}/
cp -R ${KIOSKSOURCEDIR}/img ${KIOSKTARGETDIR}/

# All done. Hopefully.
