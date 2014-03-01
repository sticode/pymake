import os
import subprocess
import sys
import shutil
import datetime

#Python building script
#Author : Jord Sti (jord52@gmail.com)

class build_log:

    def __init__(self, bname, output):
        self.name = bname
        self.output = output
        self.header = '<html><head><title>'+self.name+' Build log</title><link rel="stylesheet" href="../log.css" type="text/css" /></head><body><h2>'+self.name+'</h2>';
        self.datet = datetime.datetime.now()
        self.datestr = str(self.datet.day)+"-"+str(self.datet.month)+"-"+str(self.datet.year)+" "+str(self.datet.hour)+":"+str(self.datet.minute)
        self.content = ""
        self.footer = '<div class="footer">Build log : ' + self.datestr + '</div></body></html>'

    def add_obj(self, obj):
        self.content += '<div class="addobj">Adding Object : '+obj+'</div>'

    def end_proj(self, success = True):
        if success:
            self.content += '<div class="project_end">Project compiled !</div>'
        else:
            self.content += '<div class="project_error">Project building failed !</div>'

    def build_obj(self, cmd):
        self.content += '<div class="build_obj">'+cmd+'</div>'

    def std_err(self, err):
        self.content += '<div class="std_err">'+err+'</div>'

    def link_proj(self, cmd):
        self.content += '<div class="linking">'+cmd+'</div>'


    def save(self):
        fp = open(self.output, 'w')
        self.content = self.header + self.content + self.footer
        fp.write(self.content)
        fp.close()
        
class subexec:

    def __init__(self, args):
        self.args = args
        self.stdout = ""
        self.stderr = ""
    def run(self):
        p = subprocess.Popen(self.args , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        line = p.stdout.readline()

        while len(line) > 0:
            self.stdout += line
            line = p.stdout.readline()

        line = p.stderr.readline()

        while len(line) > 0:
            self.stderr += line
            line = p.stderr.readline()
        
class dll_copy:
    def __init__(self):
        self.dlldir = "bin"
        self.deploy = "deploy"
    def copy(self):
        dlls = os.listdir(self.dlldir)
        for d in dlls:
            if d.endswith(".dll"):
                print "Copying : "+d
                shutil.copy(os.path.join(self.dlldir, d), os.path.join(self.deploy, d))
    

class assets_copy:

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def copy(self):
        files = os.listdir(self.src)

        if not os.path.exists(self.dst):
            os.makedirs(self.dst)

        for f in files:
            if os.path.isfile(os.path.join(self.src, f)):
                dst = os.path.join(self.dst, f)
                src = os.path.join(self.src, f)
                if not self.ignore_file(f):
                    print src + " -> " + dst
                    shutil.copy(src, dst)
                
            elif os.path.isdir(os.path.join(self.src, f)):
                self.copydir(f)

    def copydir(self, dname):

        files = os.listdir(os.path.join(self.src, dname))
        dstdir = os.path.join(self.dst, dname)

        if not os.path.exists(dstdir):
            os.makedirs(dstdir)
        
        for f in files:
            fpath = os.path.join(self.src, dname, f)
            if os.path.isfile(fpath):
                dst = os.path.join(dstdir, f)
                src = os.path.join(self.src, dname, f)
                if not self.ignore_file(f):
                    print src + " -> " + dst
                    shutil.copy(src, dst)
            elif os.path.isdir(fpath):
                self.copydir(os.path.join(dname, f))

    def ignore_file(self, fname):
        if fname.endswith('.bspr'):
            return True
        elif fname.endswith('.bdspr'):
            return True
        elif fname.endswith('.res'):
            return True
        return False
        

class compiler:

    def __init__(self):
        self.gpp = "i686-w64-mingw32-g++" #C++ Compiler
        self.gpp_path = 'C:\\cygwin64\\bin' #Compiler path
        self.gcc = "i686-w64-mingw32-gcc" #C compiler
        self.includes = [] #includes directory
        self.links = [] #library to link adding -l
        self.link_args = [] #linker arguments
        self.objs_prefix = [] #compiler arguments
        self.build_num = "0" #build number
        
        self.read_settings()
        
    def read_settings(self):
        if os.path.exists(".compiler"):
            
            fp = open(".compiler", 'r')
            lines = fp.readlines()
            fp.close()
            
            for l in lines:
                if l.startswith("G++:"):
                    self.gpp = l[4:]
                elif l.startwith("PATH:"):
                    self.gpp_path = l[5:]
                elif l.startswith("GCC:"):
                    self.gcc = l[4:]

        else:
            self.write_settings()
    
    def write_settings(self):
        
        fp = open(".compiler", 'w')
        
        lines = []
        
        lines.append("G++:"+self.gpp)
        lines.append("PATH:"+self.gpp_path)
        lines.append("GCC:"+self.gcc)
        
        fp.writelines(lines)
        
        fp.close()

    def reset(self):
        self.includes = []
        self.links = []
        self.link_args = []
        self.objs_prefix = []

    def set_env(self):
        os.environ["PATH"] += os.pathsep + self.gpp_path

class object_info:
    def __init__(self, name, otype = '.cpp'):
        self.name = name
        self.otype = otype

    def get_src(self):
        return self.name + self.otype

    def get_o(self):
        return self.name + ".o"

class build_project:

    def __init__(self, projname, compiler, build = "Debug"):
        self.verbose_lvl = 5 #todo
        self.compiler = compiler
        self.projname = projname
        self.objs = []
        self.obj_dir = os.path.join("obj", build)
        self.bin_dir = os.path.join(projname, "bin", build)
        self.build = build
        self.bin_objs = []
        self.links = compiler.links
        self.output = ""
        self.objs_prefix = compiler.objs_prefix

        self.log_name = projname+"-build-"+compiler.build_num+"-"+build+"-log.html";

        if not os.path.exists('build_logs'):
            os.mkdir('build_logs')


        self.log_path = os.path.join('build_logs', self.log_name)
        
        self.log = build_log(projname, self.log_path)

        if not os.path.exists(os.path.join(projname, self.obj_dir)):
            os.makedirs(os.path.join(projname, self.obj_dir))
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

    def scan_files(self):

        files = os.listdir(self.projname)

        for f in files:
            if f.endswith('.cpp'):
                fname = f.split('.')[0]

                obj = object_info(fname)
                
                self.objs.append(obj)

                print "Adding object : " + fname
                
                self.log.add_obj(fname)
                
            elif f.endswith('.c'):
                fname = f.split('.')[0]

                obj = object_info(fname, '.c')
                
                self.objs.append(obj)

                print "Adding object : " + fname
                
                self.log.add_obj(fname)
                

    def build_objects(self):
        build_failed = False
        os.chdir(self.projname)
        for o in self.objs:
            fout = os.path.join(self.obj_dir, o.get_o())
            fcpp = os.path.join(o.get_src())
            fcpp = os.path.abspath(fcpp)

            #building args
            args = []
            if o.otype == '.cpp':
                args.append(self.compiler.gpp)
            elif o.otype == '.c':
                args.append(self.compiler.gcc)
                
            print "Building "+o.name+" with "+args[0]
            for a in self.objs_prefix:
                args.append(a)

            for i in self.compiler.includes:
                args.append("-I"+i)

            args.append("-c")
            args.append(fcpp)
            args.append("-o")
            args.append(fout)

            cmd = ""

            for a in args:
                cmd += a + " "
            print cmd
            self.log.build_obj(cmd)
            #change this to use subexec
            p = subprocess.Popen(args , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            line = p.stdout.readline()

            while len(line) > 0:
                print line
                line = p.stdout.readline()

            errtxt = ""
            line = p.stderr.readline()

            while len(line) > 0:
                errtxt += line
                line = p.stderr.readline()

            if not errtxt.find("error:") == -1:
                build_failed = True
                self.log.std_err(errtxt)

            if build_failed:
                print "Build failed ! abort..."
                print errtxt
                self.log.end_proj(False)
                os.chdir("..")
                self.log.save()
                return False
                break

            self.bin_objs.append(fout)

        os.chdir("..")
        return True

    def link(self):
        os.chdir(self.projname)
        #building args

        args = []
        args.append(self.compiler.gpp)

        for l in self.compiler.link_args:
            args.append(l)

        for o in self.bin_objs:
            args.append(o)

        args.append("-o")
        args.append(self.output)

        for l in self.compiler.links:
            args.append("-l"+l)

        cmd = ""

        for a in args:
            cmd += a + " "

        self.log.link_proj(cmd)
        print "Linking objects..."
        print cmd

        p = subprocess.Popen(args , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        line = p.stdout.readline()

        while len(line) > 0:
            print line
            line = p.stdout.readline()

        errtxt = ""

        line = p.stderr.readline()

        while len(line) > 0:
            print line
            errtxt += line
            line = p.stderr.readline()

        if not errtxt.find("error:") == -1:
            print "Linking failed , abort"
            self.log.std_err(errtxt)
            self.log.end_proj(False)
            print errtxt
            os.chdir("..")
            self.log.save()
            return False
        else:
            self.log.end_proj()
            print "Build success !"

        os.chdir("..")

        self.log.save()
        return True
            
class build_file:

    def __init__(self, path):
        self.path = path
        self.info = cpp_info()
        self.project = ""
        self.output = ""
        self.build = ""
        self.read()

    def read(self):
        fp = open(self.path, 'r')

        line = fp.readline()

        while len(line) > 0:

            self.parse_line(line)

            line = fp.readline()

        fp.close()

    def parse_line(self, line):
        if line.startswith("link:"):
            link = line[5:].strip()
            print "Linking -> " + link
            self.info.links.append(link)
        elif line.startswith("include:"):
            include = line[8:].strip()
            print "Include -> " + include
            self.info.includes.append(include)
        elif line.startswith("link_args:"):
            link_args = line[10:].strip()
            print "Link Args -> " + link_args
            self.info.link_args.append(link_args)
        elif line.startswith("obj_prefix:"):
            obj_prefix = line[11:].strip()
            print "Obj Prefix -> " + obj_prefix
            self.info.objs_prefix.append(obj_prefix)
        elif line.startswith("output:"):
            output = line[7:].strip()
            print "Output -> " + output
            self.output = output
        elif line.startswith("build:"):
            build = line[6:].strip()
            print "Build -> " + build
            self.build = build
        elif line.startswith("project:"):
            project = line[8:].strip()
            print "Project -> " + project
            self.project = project

    def get_maker(self):
        self.info.set_env()
        bp = build_project(self.project, self.info, self.build)
        bp.output = self.output
        return bp
        
