Creating packages for OS X
==========================

Packaging your application for the OS X 10.6 platform can only be done inside OS X.

The package will only work for the 64 bit OS X. We no longer support 32 bit OS X platforms.

.. note::
    Currently, packages for OS X can only be generated with Python 2.7. Python 3.3+ support is on the way...

.. _osx_requirements:

Official Packaging method
-------------------------

Due to a lot of problems with including libraries and files on OS X with other methods
we now have a simpler and easier way to package Kivy apps on OS X.

Since kivy 1.9 kivy package on OS X is a self contained portable distribution.
It is now possible to package kivy apps using the method described below to make
it easier to include frameworks like sdl2 and gstreamer::

1: Make sure you have the Kivy.app(unmodified) from the download page.
2: run the following commands::

    > mkdir  packaging
    > cd packaging
    packaging> git clone https://github.com/kivy/kivy-sdk-packager
    packaging> cd kivy-sdk-packager/osx
    osx> cp -a /Applications/Kivy.app ./Kivy.App

This step above is important, you have to make sure to preserve the paths and permissions. A command like cp -rf will copy but make the app unusable and lead to error later on.

Now all you need to do is to include your compiled app into the Kivy.app, simply run the following command::

    osx> ./package-app.sh path/to/your/app

This should copy Kivy.app to `yourapp.app` and include a compiled copy of your app into this package.

That's it, your self contained package is ready to be deployed!

when you double click this app you can see your app run.

This is a pretty big sized app right now however you can simply remove the unneeded parts from this package.

For example if you don't use Gstreamer, simply remove it from YourApp.app/Contents/Frameworks.
Similarly you can remove the examples dir from /Applications/Kivy.app/Contents/Resources/kivy/examples/
or kivyt/tools,  kivy/docs...

This way the whole app can be made to only include the parts that you use inside your app.

You can edit the icons and other settings of your app by editing the YourApp/Contents/info.plist to suit your needs, simply double click this file and make your changes.

Last step is to make a dmg of your app using the following command::

    osx> create-osx-dmg.sh YourApp.app

This should give you a compressed dmg that will even further minimize the size of your distributed app.



Unofficial Method using Pyinstaller
-----------------------------------

Requirements
------------

    * Latest Kivy (the whole portable package, not only the github sourcecode)
    * `PyInstaller 3.0 <http://www.pyinstaller.org/#Downloads>`_

Please ensure that you have installed the Kivy DMG and installed the `make-symlink` script.
The `kivy` command must be accessible from the command line.

Thereafter, download and decompress the PyInstaller 2.0 package.

.. _mac_Create-the-spec-file:

Create the spec file
--------------------

As an example, we'll package the touchtracer demo, using a custom icon. The
touchtracer code is in the `../kivy/examples/demo/touchtracer/` directory, and the main
file is named `main.py`. Replace both path/filename according to your system.

#. Open a console.
#. Go to the pyinstaller directory, and create the initial specs::

    cd pyinstaller-3.0
    kivy pyinstaller.py --windowed --name touchtracer ../kivy/examples/demo/touchtracer/main.py

#. The specs file is named `touchtracer/touchtracer.spec` and located inside the
   pyinstaller directory. Now we need to edit the spec file to add kivy hooks
   to correctly build the executable.
   Open the spec file with your favorite editor and put theses lines at the
   start of the spec::

    from kivy.tools.packaging.pyinstaller_hooks import get_hooks

   In the `Analysis()` function, remove the `hookspath=None` parameter and
   the `runtime_hooks` parameter if present. `get_hooks` will return the required
   values for both parameters, so at the end of `Analysis()` add `**get_hooks()`.
   E.g.::

    a = Analysis(['/usr/local/share/kivy-examples/demo/touchtracer/main.py'],
                 pathex=['/Users/kivy-dev/Projects/kivy-packaging'],
                 binaries=None,
                 datas=None,
                 hiddenimports=[],
                 excludes=None,
                 win_no_prefer_redirects=None,
                 win_private_assemblies=None,
                 cipher=block_cipher,
                 **get_hooks())

   This will add the required hooks so that pyinstaller gets the required kivy files.

   Then, you need to change the `COLLECT()` call to add the data of touchtracer
   (`touchtracer.kv`, `particle.png`, ...). Change the line to add a Tree()
   object. This Tree will search and add every file found in the touchtracer
   directory to your final package.

   You will need to specify to pyinstaller where to look for the frameworks
   included with kivy too, your COLLECT section should look something like this::

    coll = COLLECT( exe, Tree('../kivy/examples/demo/touchtracer/'),
                   Tree("../../../../../../Applications/Kivy.app/Contents/Frameworks/"),
                   Tree("../../../../../Applications/Kivy.app/Contents/Frameworks/SDL2_ttf.framework/Versions/A/Frameworks/Freetype.Framework"),
                   a.binaries,
                   #...
                   )

The Tree inclusion of frameworks is a work around a pyinstaller bug that is not able to find the exact path of libs including @executable_path.

There is a issue open on pyinstaller issue tracker for this. https://github.com/pyinstaller/pyinstaller/issues/1338

Make sure the path to the frameworks is relative to the current directory you are on.

#. We are done. Your spec is ready to be executed!

.. _Build the spec and create DMG:

Build the spec and create a DMG
-------------------------------

#. Open a console.
#. Go to the pyinstaller directory, and build the spec::

    cd pyinstaller-3.0
    kivy pyinstaller.py touchtracer/touchtracer.spec

#. The package will be the `touchtracer/dist/touchtracer` directory. Rename it to .app::

    pushd touchtracer/dist
    mv touchtracer touchtracer.app
    hdiutil create ./Touchtracer.dmg -srcfolder touchtracer.app -ov
    popd

#. You will now have a Touchtracer.dmg available in the `touchtracer/dist` directory.

Including Gstreamer
-------------------

If you want to read video files, audio, or camera, you will need to include
gstreamer. By default, only pygst/gst files are discovered, but all the gst plugins
and libraries are missing. You need to include them in your .spec file too, by
adding one more arguments to the `COLLECT()` method::

    import os
    gst_plugin_path = os.environ.get('GST_PLUGIN_PATH').split(':')[0]

    coll = COLLECT( exe, Tree('../kivy/examples/demo/touchtracer/'),
                   Tree(os.path.join(gst_plugin_path, '..')),
                   a.binaries,
                   #...
                   )
