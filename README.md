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
-BN:$BUILD_NUM : Specify a build number and name for this compilated project
-PACK : Zip all the compilated project for a release (NOT IMPLEMENTED)


to do
=====
- IDE Project file parser (CodeBlocks is first to be handled)
- Verbosity level for building, not showing, they are already logged
- Embed css style for log
- compiler settings file
- ftp uploader for success build
...
