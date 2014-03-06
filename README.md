pymake
======

Custom python make script for C++/C project


how it work
======
pymake only support CodeBlock workspace and project file.
You can compile a project by using build.py

build.py [args]

Use the following arguments :

-CPP:$BIN_NAME : C++ Compiler

-CC:$BIN_NAME : C Compiler

-CPATH:$PATH : Root path of the Compiler

-P:$PATH_PROJECT : Path to the project file or workspace file

-B:$CONFIG : Build configuration name

-V:$num : Verbose level for console output

-BN:$BUILD_NUM : Specify a build number and name for this compilated project

-PACK : Zip all the compilated project for a release (NOT IMPLEMENTED)


to do
=====
- IDE Project file parser ; Code::Blocks working, VS support maybe in the future
- Verbosity level for building, not showing, they are already logged -> mostly done
- Embed css style for log -> a good looking style
- compiler settings file -> mostly done
- ftp uploader for success build
- directory input, with file scanning, find a *.workspace or *.cbp and a .pymake for setting like post build script -> DONE
...
