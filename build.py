import os
import ide_project
import make
import sys

class post_script:
    
    def __init__(self, script):
        self.script = script
    
    def run(self):
        
        fp = open(self.script, 'r')
        
        lines = fp.readlines()
        
        fp.close()
        
        for l in lines:
            
            self.exec_line(l)
        
    def exec_line(self, line):
        
        line = line.strip()
        
        if line.startswith('run '):
            args = line[4:]
        elif line.startswith('copy '):
            args = line[5:]
        elif line.startswith('rm '):
            args = line[3:]
        elif line.startswith('pack '):
            args = line[5:]
        

def build_project(parser, build_name, compiler):
    
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

def build_workspace(workspace, build_name, compiler):
    #compiler.set_env()
    
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
                compiler.self.gpp = args[5:]
            elif args.startswith('-CC:'):
                compiler.self.gcc = args[4:]
            elif args.startswith('-CPATH:'):
                compiler.self.gpp_path = args[7:]
            elif args.startswith('-P:'):
                pfile = args[3:]
            elif args.startswith('-B:'):
                build_name = args[3:]
            elif args.startswith('-BN:'):
                build_num = args[4:]
                compiler.build_num = build_num
            elif args.startswith("-PACK"):
                pack_output = True
        
        ia = ia + 1
    
    compiler.set_env()
    
    if pfile == None:
        print "Invalid project file !"
        exit()
    
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
        
    