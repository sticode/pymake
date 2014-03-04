import os
import ide_project
import make
import sys


def search_pymake(dpath):
    
    pymake_f = None
    
    files = os.listdir(dpath)
    
    for f in files:
        
        if f.endswith(".pymake"):
            
            fpath = os.path.join(dpath, f)
            
            pymake_f = make.pymake_file(fpath)
            pymake_f.read()
    
    return pymake_f
            

def build_project(parser, build_name, compiler):
    
    
    fpymake = search_pymake(parser.root)
    
    if not fpymake == None:
        fpymake.do_clean()
    
    print "Compiling project : " + parser.project_name
    
    if build_name == None:
        build_name = 'Release'
    
    print "Build Config : " + build_name
    
    path = os.path.join(parser.root, "..")
    os.chdir(path)
    
    builder = parser.create_builder(compiler, build_name)
    
    if builder == None:
        print build_name+" not found !"
        exit()
    
    if not builder.build_objects():
        print "Error building " + parser.project_name
        exit()
    if not builder.link():
        print "Error linking " + parser.project_name
        exit()
        
    print p.name + " builded with success !"
    
    if not fpymake == None:
        fpymake.do_post_build()

def build_workspace(workspace, build_name, compiler):
    #compiler.set_env()
    
    fpymake = search_pymake(workspace.root)
    if not fpymake == None:
        fpymake.do_clean()
    
    print "Compiling workspace : " + workspace.name
    
    if build_name == None:
        build_name = 'Release' #need to get first build from projects
    
    print "Build Config : " + build_name
    
    for project in workspace.projects:
        project.parser.parse()
    
    workspace.resolve_order()
    
    os.chdir(workspace.root)
    
    projects = workspace.get_projects()
    
    
    for p in projects:
        
        builder = p.parser.create_builder(compiler, build_name)
        
        if builder == None:
            print "Build config not found !"
            exit()
        
        if not builder.build_objects():
            print "Error building " + p.name
            exit()
        if not builder.link():
            print "Error linking " + p.name
            exit()
        
        print p.name + " builded with success !"

    if not fpymake == None:
        fpymake.do_post_build()

def print_help():
    print "---------------------"
    print "        HELP         "
    print "---------------------"
    print "-CPP:$name -> C++ Compiler"
    print "-CC:$name -> C Compiler"
    print "-CPATH:$path -> Compiler root path"
    print "-P:$path -> project path or project file"
    print "-B:$build -> Build configuration to compile"
    print "-BN:$build_version -> Build Version"
    print "-PACK -> zip package of the compiled project (NOT IMPLEMENTED)"
    print "---------------------"

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
            
                build_project(parser, build_name, compiler)
                
            elif f.endswith('.workspace'):
                #workspace file
                workspace = ide_project.codeblock_workspace_parser(os.path.join(pfile, f))
                workspace.parse()
            
                build_workspace(workspace, build_name, compiler)
    else:
    
        if pfile.endswith('.cbp'):
            #code block projects file
            parser = ide_project.codeblock_parser(pfile)
            parser.parse()
            
            build_project(parser, build_name, compiler)
            
        elif pfile.endswith('.workspace'):
            #workspace file
            
            workspace = ide_project.codeblock_workspace_parser(pfile)
            workspace.parse()
            
            
            
            
            
            build_workspace(workspace, build_name, compiler)
        
    