# PyQt5, PyInstaller and Qt5

## PyQt5 and PyInstaller using Anaconda
```bash
$ conda create --name youtube-dl-pyqt python=3.8.3 pyqt pyinstaller
```

## Export Conda Environment
```bash
$ conda env export > my_environment.yml
```

## Export Requirements from Conda
```bash
$ conda list -e > requirements.txt
```


## Install Qt in GNU/Linux Debian Stretch
```bash
$ sudo apt install qt5-default qt5-qmake qtbase5-dev qtbase5-dev-tools qtbase5-doc qtbase5-doc-html qtbase5-examples qtcreator qttranslations5-l10n
```

```bash
$ sudo apt install qt5-default qt5-qmake qtbase5-dev qtbase5-dev-tools qtcreator qttranslations5-l10n
```
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following additional packages will be installed:
  adwaita-icon-theme at-spi2-core fontconfig gdb glib-networking glib-networking-common
  glib-networking-services gsettings-desktop-schemas gstreamer1.0-plugins-base gtk-update-icon-cache
  hicolor-icon-theme libatk-bridge2.0-0 libatk1.0-0 libatk1.0-data libatspi2.0-0 libavahi-client3
  libavahi-common-data libavahi-common3 libbabeltrace-ctf1 libbabeltrace1 libbotan-1.10-1 libc6-dbg
  libcairo-gobject2 libcairo2 libcdparanoia0 libclang1-3.9 libcolord2 libcroco3 libcups2 libdatrie1
  libdouble-conversion1 libdrm-dev libdw1 libegl1-mesa libepoxy0 libevdev2 libgbm1 libgdk-pixbuf2.0-0
  libgdk-pixbuf2.0-common libgl1-mesa-dev libglew2.0 libglu1-mesa libglu1-mesa-dev libgraphite2-3
  libgstreamer-plugins-base1.0-0 libgtk-3-0 libgtk-3-bin libgtk-3-common libgudev-1.0-0 libharfbuzz0b
  libinput-bin libinput10 libjson-glib-1.0-0 libjson-glib-1.0-common liblcms2-2 libmtdev1 libogg0 libopus0
  liborc-0.4-0 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpcre16-3 libpixman-1-0 libproxy1v5
  libqbscore1.7 libqbsqtprofilesetup1.7 libqt5clucene5 libqt5concurrent5 libqt5core5a libqt5dbus5
  libqt5designer5 libqt5designercomponents5 libqt5gui5 libqt5help5 libqt5network5 libqt5opengl5
  libqt5opengl5-dev libqt5printsupport5 libqt5qml5 libqt5quick5 libqt5quicktest5 libqt5quickwidgets5
  libqt5script5 libqt5sql5 libqt5sql5-sqlite libqt5svg5 libqt5test5 libqt5webkit5 libqt5widgets5 libqt5xml5
  libqt5xmlpatterns5 librest-0.7-0 librsvg2-2 librsvg2-common libsoup-gnome2.4-1 libsoup2.4-1 libthai-data
  libthai0 libtheora0 libvisual-0.4-0 libvorbis0a libvorbisenc2 libwacom-bin libwacom-common libwacom2
  libwayland-client0 libwayland-cursor0 libwayland-egl1-mesa libwayland-server0 libx11-xcb-dev libx11-xcb1
  libxcb-dri2-0-dev libxcb-dri3-dev libxcb-glx0-dev libxcb-icccm4 libxcb-image0 libxcb-keysyms1
  libxcb-present-dev libxcb-randr0 libxcb-randr0-dev libxcb-render-util0 libxcb-render0 libxcb-render0-dev
  libxcb-shape0-dev libxcb-shm0 libxcb-sync-dev libxcb-util0 libxcb-xfixes0 libxcb-xfixes0-dev
  libxcb-xinerama0 libxcb-xkb1 libxcursor1 libxdamage-dev libxfixes-dev libxkbcommon-x11-0 libxkbcommon0
  libxshmfence-dev libxxf86vm-dev mesa-common-dev mesa-utils qml-module-qtgraphicaleffects
  qml-module-qtqml-models2 qml-module-qtquick-controls qml-module-qtquick-layouts qml-module-qtquick-window2
  qml-module-qtquick2 qmlscene qt3d5-doc qt5-doc qt5-gtk-platformtheme qt5-qmltooling-plugins qtbase5-doc
  qtchooser qtconnectivity5-doc qtcreator-data qtcreator-doc qtdeclarative5-dev-tools qtdeclarative5-doc
  qtgraphicaleffects5-doc qtlocation5-doc qtmultimedia5-doc qtquickcontrols2-5-doc qtquickcontrols5-doc
  qtscript5-doc qtsensors5-doc qtserialport5-doc qtsvg5-doc qttools5-dev-tools qttools5-doc qtwayland5-doc
  qtwebchannel5-doc qtwebengine5-doc qtwebkit5-doc qtwebkit5-examples-doc qtwebsockets5-doc qtx11extras5-doc
  qtxmlpatterns5-dev-tools qtxmlpatterns5-doc x11proto-damage-dev x11proto-dri2-dev x11proto-fixes-dev
  x11proto-gl-dev x11proto-xf86vidmode-dev xkb-data
Suggested packages:
  gdb-doc gdbserver gvfs colord cups-common glew-utils libvisual-0.4-plugins liblcms2-utils opus-tools
  qt5-image-formats-plugins qtwayland5 librsvg2-bin default-libmysqlclient-dev firebird-dev libegl1-mesa-dev
  libpq-dev unixodbc-dev cmake kdelibs5-data subversion
The following NEW packages will be installed:
  adwaita-icon-theme at-spi2-core fontconfig gdb glib-networking glib-networking-common
  glib-networking-services gsettings-desktop-schemas gstreamer1.0-plugins-base gtk-update-icon-cache
  hicolor-icon-theme libatk-bridge2.0-0 libatk1.0-0 libatk1.0-data libatspi2.0-0 libavahi-client3
  libavahi-common-data libavahi-common3 libbabeltrace-ctf1 libbabeltrace1 libbotan-1.10-1 libc6-dbg
  libcairo-gobject2 libcairo2 libcdparanoia0 libclang1-3.9 libcolord2 libcroco3 libcups2 libdatrie1
  libdouble-conversion1 libdrm-dev libdw1 libegl1-mesa libepoxy0 libevdev2 libgbm1 libgdk-pixbuf2.0-0
  libgdk-pixbuf2.0-common libgl1-mesa-dev libglew2.0 libglu1-mesa libglu1-mesa-dev libgraphite2-3
  libgstreamer-plugins-base1.0-0 libgtk-3-0 libgtk-3-bin libgtk-3-common libgudev-1.0-0 libharfbuzz0b
  libinput-bin libinput10 libjson-glib-1.0-0 libjson-glib-1.0-common liblcms2-2 libmtdev1 libogg0 libopus0
  liborc-0.4-0 libpango-1.0-0 libpangocairo-1.0-0 libpangoft2-1.0-0 libpcre16-3 libpixman-1-0 libproxy1v5
  libqbscore1.7 libqbsqtprofilesetup1.7 libqt5clucene5 libqt5concurrent5 libqt5core5a libqt5dbus5
  libqt5designer5 libqt5designercomponents5 libqt5gui5 libqt5help5 libqt5network5 libqt5opengl5
  libqt5opengl5-dev libqt5printsupport5 libqt5qml5 libqt5quick5 libqt5quicktest5 libqt5quickwidgets5
  libqt5script5 libqt5sql5 libqt5sql5-sqlite libqt5svg5 libqt5test5 libqt5webkit5 libqt5widgets5 libqt5xml5
  libqt5xmlpatterns5 librest-0.7-0 librsvg2-2 librsvg2-common libsoup-gnome2.4-1 libsoup2.4-1 libthai-data
  libthai0 libtheora0 libvisual-0.4-0 libvorbis0a libvorbisenc2 libwacom-bin libwacom-common libwacom2
  libwayland-client0 libwayland-cursor0 libwayland-egl1-mesa libwayland-server0 libx11-xcb-dev
  libxcb-dri2-0-dev libxcb-dri3-dev libxcb-glx0-dev libxcb-icccm4 libxcb-image0 libxcb-keysyms1
  libxcb-present-dev libxcb-randr0 libxcb-randr0-dev libxcb-render-util0 libxcb-render0 libxcb-render0-dev
  libxcb-shape0-dev libxcb-shm0 libxcb-sync-dev libxcb-util0 libxcb-xfixes0 libxcb-xfixes0-dev
  libxcb-xinerama0 libxcb-xkb1 libxcursor1 libxdamage-dev libxfixes-dev libxkbcommon-x11-0 libxkbcommon0
  libxshmfence-dev libxxf86vm-dev mesa-common-dev mesa-utils qml-module-qtgraphicaleffects
  qml-module-qtqml-models2 qml-module-qtquick-controls qml-module-qtquick-layouts qml-module-qtquick-window2
  qml-module-qtquick2 qmlscene qt3d5-doc qt5-default qt5-doc qt5-gtk-platformtheme qt5-qmake
  qt5-qmltooling-plugins qtbase5-dev qtbase5-dev-tools qtbase5-doc qtchooser qtconnectivity5-doc qtcreator
  qtcreator-data qtcreator-doc qtdeclarative5-dev-tools qtdeclarative5-doc qtgraphicaleffects5-doc
  qtlocation5-doc qtmultimedia5-doc qtquickcontrols2-5-doc qtquickcontrols5-doc qtscript5-doc qtsensors5-doc
  qtserialport5-doc qtsvg5-doc qttools5-dev-tools qttools5-doc qttranslations5-l10n qtwayland5-doc
  qtwebchannel5-doc qtwebengine5-doc qtwebkit5-doc qtwebkit5-examples-doc qtwebsockets5-doc qtx11extras5-doc
  qtxmlpatterns5-dev-tools qtxmlpatterns5-doc x11proto-damage-dev x11proto-dri2-dev x11proto-fixes-dev
  x11proto-gl-dev x11proto-xf86vidmode-dev xkb-data
The following packages will be upgraded:
  libx11-xcb1
1 upgraded, 190 newly installed, 0 to remove and 78 not upgraded.
Need to get 195 MB of archives.
After this operation, 497 MB of additional disk space will be used.


### EXTRAS

> qt5-default qt5-doc qt5-doc-html qt5-qmake qtbase5-dev qtbase5-dev-tools qtbase5-doc qtbase5-doc-html qtbase5-examples qtcreator qttools5-dev qttools5-dev-tools qttools5-doc qttools5-doc-html qttools5-examples qttranslations5-l10n 