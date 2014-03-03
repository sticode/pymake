#ide project file parser
import xml.etree.ElementTree as ET
import make
#to do:
#generate a build_project
#maybe add workspace support for multiple project compilation

class build_target:
    def __init__(self, target_name):
        self.name = target_name
        self.includes = []
        self.link_args = []
        self.lib_dirs = []
        self.obj_args = []
        self.output = None
        self.type = 0
        self.working_dir = None
        self.obj_output = None
    
    def fix_output(self):
        if self.type == 1:
            self.output += ".exe"
    
    def print_data(self):
        #debug purpose
        print "Build Target : " + self.name
        print "Include :"
        for i in self.includes:
            print "\t" + i
        
        print "Linker args :"
        for a in self.link_args:
            print "\t" + a
        print "Objects args :"
        for a in self.obj_args:
            print "\t" + a
        
        print "Lib dirs :"
        for l in self.lib_dirs:
            print "\t" + l
        
        print "Output : " + self.output
        print "Type : " + str(self.type)
        print "Working Dir : " + self.working_dir
        print "Obj output : " + self.obj_output

class ide_parser:

    def __init__(self):
        self.proj_file = None
        self.ide = None
        self.objects = []
        self.builds = []
        self.project_name = None
        #.
        #..
        #...
    def child_init(self, proj_file):
        self.proj_file = proj_file
        self.ide = None
        self.objects = []
        self.builds = []
        self.project_name = None
        
    def add_include(self, inc, build_name = 'ALL'):

        if build_name == 'ALL':
            for b in self.builds:
                b.includes.append(inc)
        else:
            b = self.get_build(build_name)
            if not b == None:
                b.includes.append(inc)

    def add_link_args(self, args, build_name = 'ALL'):

        if build_name == 'ALL':
            for b in self.builds:
                b.link_args.append(args)
        else:
            b = self.get_build(build_name)
            if not b == None:
                b.link_args.append(args)
                
    def add_lib_dir(self, lib, build_name = 'ALL'):

        if build_name == 'ALL':
            for b in self.builds:
                b.lib_dirs.append(lib)
        else:
            b = self.get_build(build_name)
            if not b == None:
                b.lib_dirs.append(lib)


    def add_obj_args(self, args, build_name = 'ALL'):

        if build_name == 'ALL':
            for b in self.builds:
                b.obj_args.append(args)
        else:
            b = self.get_build(build_name)
            if not b == None:
                b.obj_args.append(args)
    
    def get_build(self, build_name):

        for b in self.builds:
            if b.name == build_name:
                return b

        return None

    def parse(self):
        #parsing project
        #.
        #..
        #...
        print "empty method..."
    def create_builder(self):
        #create maker
        return None

class project:
    
    def __init__(self, name, parser):
        self.name = name
        self.parser = parser
        self.depends = []
        self.order = 0

class workspace_parser:
    
    def __init__(self, work_file):
        self.wspace = work_file
        self.projects = []
    
    def child_init(self):
        self.projects = []
    
    def parse(self):
        return None
    
    def get_project(self, name):
        
        for p in self.projects:
            if p.name == name:
                return p
            
        return None
    
    def resolve_order(self):
        #todo
        return None

class codeblock_parser(ide_parser):

    def __init__(self,  proj_file):
        self.child_init(proj_file)
        self.ide = 'CodeBlocks'

    def create_builder(self, compiler, build_name):
        
        build = self.get_build(build_name)
        if not build == None:
            build.fix_output()
            compiler.reset()
            compiler.includes = build.includes
            compiler.link_args = build.link_args
            compiler.objs_prefix = build.obj_args
        else:
            return None
        
        builder = make.build_project(self.project_name, compiler, build.name)
        builder.output = build.output
        builder.objs = self.objects
        
        return builder
        
    def parse(self):
        #parsing codeblock xml
        tree = ET.parse(self.proj_file)
        root = tree.getroot()

        for child in root:
            if child.tag == 'Project':
                for pchild in child:
                    if pchild.tag == 'Build':
                        self.read_build(pchild)
                    elif pchild.tag == 'Compiler':
                        for cc in pchild:
                            if cc.tag == 'Add':
                                for a in cc.attrib:
                                    data = cc.attrib[a]
                                    if a == 'option':
                                        self.add_obj_args(data)
                                    elif a == 'directory':
                                        self.add_include(data)
            
                    elif pchild.tag == 'Linker':
                        for lc in pchild:
                            if lc.tag == 'Add':
                                for a in lc.attrib:
                                    data = lc.attrib[a]
                                    if a == 'option':
                                        self.add_link_args(data)
                                    elif a == 'directory':
                                        self.add_lib_dir(data)
            
                    elif pchild.tag == 'Unit':
                        for a in pchild.attrib:
                            data = pchild.attrib[a]
                            if a == 'filename':
                                if data.endswith('.cpp'):
                                    oname = data.split('.')[0]
                                    obj = make.object_info(oname)
                                    self.objects.append(obj)
                                elif data.endswith('.c'):
                                    oname = data.split('.')[0]
                                    obj = make.object_info(oname, '.c')
                                    self.objects.append(obj)
                    elif pchild.tag == 'Option':
                        for a in pchild.attrib:
                            data = pchild.attrib[a]
                            if a == 'title':
                                self.project_name = data
                                
                    
    def read_build(self, xml_tag):
            
        for child in xml_tag:
                
            if child.tag == 'Target':
                build_name = child.attrib['title']
                build = build_target(build_name)
                self.builds.append(build)
                for tc in child:
                    
                    if tc.tag == 'Option':
                        for a in tc.attrib:
                            data = tc.attrib[a]
                            if a == 'output':
                                build.output = data
                            elif a == 'working_dir':
                                build.working_dir = data
                            elif a == 'object_output':
                                build.obj_output = data
                            elif a == 'type':
                                build.type = int(data)
                    elif tc.tag == 'Compiler':
                        for cc in tc:
                            if cc.tag == 'Add':
                                for a in cc.attrib:
                                    data = cc.attrib[a]
                                    if a == 'option':
                                        build.obj_args.append(data)
                                    elif a == 'directory':
                                        build.includes.append(data)
                    elif tc.tag == 'Linker':
                        for lc in tc:
                            if lc.tag == 'Add':
                                for a in lc.attrib:
                                    data = lc.attrib[a]
                                    if a == 'option':
                                        build.link_args.append(data)
                                    elif a == 'directory':
                                        build.lib_dirs.append(data)
                                


class codeblock_workspace_parser(workspace_parser):
    
    def __init__(self, wspace):
        self.wspace = wspace
        self.child_init()
        
    def parse(self):
        
        tree = ET.parse()
        

#testing zone
parser = codeblock_parser("test/sample_codeblocks.cbp")

parser.parse()
builder = parser.create_builder(make.compiler(), "Release")

for o in builder.objs:
    print o.name
