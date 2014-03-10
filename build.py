import os
import ide_project
import make
import sys
import shutil
import time

class filesize:
    
    def __init__(self, fsize):
        self.size = float(fsize)
        
    def get_str(self):
        
        kb = self.size / 1024
        mb = kb / 1024
        gb = mb / 2014
        
        if gb >= 1:
            #gb output format
            return "{:4.3f}".format(gb) + " GB(s)"
        elif mb >= 1:
            return "{:4.3f}".format(mb) + " MB(s)"
        elif kb >= 1:
            return "{:4.3f}".format(kb) + " KB(s)"
        else:
            return "{:4.3f}".format(self.size) + " B(s)"
        
        

def search_pymake(dpath):
    
    pymake_f = None
    
    files = os.listdir(dpath)
    
    for f in files:
        
        if f.endswith(".pymake"):
            
            fpath = os.path.join(dpath, f)
            
            pymake_f = make.pymake_file(fpath)
            pymake_f.read()
    
    return pymake_f
            

def build_project(parser, build_name, compiler, verbosity):
    start_tm = time.time()
    
    fpymake = search_pymake(parser.root)
    
    if not fpymake == None:
        fpymake.do_pre_build()
        fpymake.verbose_lvl = verbosity
        fpymake.add_var('BUILD', build_name)
        fpymake.add_var('ROOT', parser.root)
        fpymake.add_var('G++', compiler.gpp)
        fpymake.add_var('CPATH', compiler.gpp_path)
        fpymake.add_var('GC', compiler.gcc)
        fpymake.add_var('BUILD_NUM', str(compiler.build_num))
        
    print "Compiling project : " + parser.project_name
    
    if build_name == None:
        b = parser.get_builds()
        build_name = b[0]
    
    print "Build Config : " + build_name
    
    path = os.path.join(parser.root, "..")
    os.chdir(path)
    
    builder = parser.create_builder(compiler, build_name)
    
    if builder == None:
        print build_name+" not found !"
        exit()
    
    builder.verbose_lvl = verbosity
    builder.do_clean()
    
    if not builder.build_objects():
        print "Error building " + parser.project_name
        exit()
    if not builder.link():
        print "Error linking " + parser.project_name
        exit()
        
    print parser.project_name + " builded with success !"
    
    if not fpymake == None:
        fpymake.do_post_build()
        
        
    ts = time.time() - start_tm
    
    print "Project builded in " + "{:10.4f}".format(ts) + " sec(s)"
    
    fsize = filesize(os.path.getsize(os.path.join(builder.projname, builder.output)))
    
    print "Output size : " + fsize.get_str()
    
    print "Build completed !"

def build_workspace(workspace, build_name, compiler, verbosity):
    #compiler.set_env()
    start_tm = time.time()
    
    fpymake = search_pymake(workspace.root)
    if not fpymake == None:
        fpymake.do_pre_build()
        fpymake.verbose_lvl = verbosity
        fpymake.add_var('BUILD', build_name)
        fpymake.add_var('ROOT', workspace.root)
        fpymake.add_var('G++', compiler.gpp)
        fpymake.add_var('CPATH', compiler.gpp_path)
        fpymake.add_var('GC', compiler.gcc)
        fpymake.add_var('BUILD_NUM', str(compiler.build_num))
    
    print "Compiling workspace : " + workspace.name
    
    for project in workspace.projects:
        project.parser.parse()
    
    if build_name == None:
        #build_name = 'Release' #need to get first build from projects
        b = workspace.get_builds()
        build_name = b[0]
        
    
    print "Build Config : " + build_name
    
    
    workspace.resolve_order()
    
    os.chdir(workspace.root)
    
    projects = workspace.get_projects()
    
    
    for p in projects:
        
        builder = p.parser.create_builder(compiler, build_name)
        
        if builder == None:
            print "Build config not found !"
            exit()
            
        builder.verbose_lvl = verbosity
        builder.do_clean()
        
        if not builder.build_objects():
            print "Error building " + p.name
            exit()
        if not builder.link():
            print "Error linking " + p.name
            exit()
        
        print p.name + " builded with success !"
        
        fsize = filesize(os.path.getsize(os.path.join(builder.projname, builder.output)))
    
        print "Output size : " + fsize.get_str()
        
        for d in p.depends:
            
            pfile = os.path.basename(d)
            
            pdep = workspace.get_project_by_pfile(pfile)
            
            if not pdep == None:
                bdep = pdep.parser.get_build(build_name)
                
                if not bdep == None:
                    #copying dll
                    src = os.path.join(pdep.name, bdep.output)
                    dst = os.path.join(p.name, os.path.dirname(builder.output), os.path.basename(src))
                    
                    if verbosity >= 3:
                        print "Copying " + src + " -> " + dst
                        
                    shutil.copy(src, dst)

    if not fpymake == None:
        fpymake.do_post_build()

    
    ts = time.time() - start_tm
    
    print "Workspace builded in " + "{:10.4f}".format(ts) + " sec(s)"
    
    print "Build completed !"

def print_help():
    print "----------------------------------------"
    print "        HELP         "
    print "----------------------------------------"
    print "-CPP:$name -> C++ Compiler"
    print "-CC:$name -> C Compiler"
    print "-CPATH:$path -> Compiler root path"
    print "-P:$path -> project path or project file"
    print "-B:$build -> Build configuration to compile"
    print "-BN:$build_version -> Build Version"
    print "-V:$level -> Verbosity level of the building"
    print "-PACK -> zip package of the compiled project (NOT IMPLEMENTED)"
    print "----------------------------------------"

if __name__ == '__main__':
    #args parsing
    print "-------------------"
    print "    pymake"
    print "-------------------"
    print "Author : jordsti"
    print "jord52@gmail.com"
    print "-------------------"
    compiler = make.compiler()
    pack_output = False
    pfile = None
    build_name = None
    build_num = "0"
    verbosity = 0
    ia = 0
    for args in sys.argv:
        
        if not ia == 0:
            
            if args.startswith('-CPP:'):
                compiler.gpp = args[5:]
            elif args.startswith('-CC:'):
                compiler.gcc = args[4:]
            elif args.startswith('-CPATH:'):
                compiler.gpp_path = args[7:]
            elif args.startswith('-P:'):
                pfile = args[3:]
            elif args.startswith('-B:'):
                build_name = args[3:]
            elif args.startswith('-BN:'):
                build_num = args[4:]
                compiler.build_num = build_num
            elif args.startswith("-PACK"):
                pack_output = True
            elif args.startswith("-HELP"):
                print_help()
                exit()
            elif args.startswith("-V:"):
                verbosity = int(args[3:])
                
        
        ia = ia + 1
    
    compiler.set_env()
    compiler.build_num = build_num
    
    if pfile == None:
        print "Invalid project file !"
        exit()
    
    if os.path.isdir(pfile):
        
        files = os.listdir(pfile)
        
        for f in files:

            if f.endswith('.cbp'):
                parser = ide_project.codeblock_parser(os.path.join(pfile, f))
                parser.parse()
            
                build_project(parser, build_name, compiler, verbosity)
                
            elif f.endswith('.workspace'):
                #workspace file
                workspace = ide_project.codeblock_workspace_parser(os.path.join(pfile, f))
                workspace.parse()
            
                build_workspace(workspace, build_name, compiler, verbosity)
    else:
    
        if pfile.endswith('.cbp'):
            #code block projects file
            parser = ide_project.codeblock_parser(pfile)
            parser.parse()
            

            build_project(parser, build_name, compiler, verbosity)
            
            
        elif pfile.endswith('.workspace'):
            #workspace file
            
            workspace = ide_project.codeblock_workspace_parser(pfile)
            workspace.parse()

            build_workspace(workspace, build_name, compiler, verbosity)
                    
