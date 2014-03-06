import os
import subprocess
import sys
import shutil
import datetime
import zipfile

#Python building script
#Author : Jord Sti (jord52@gmail.com)

class packer:

    def __init__(self, packdir, output):
        self.packdir = packdir
        self.output = output

    def pack(self):
        self.zf = zipfile.ZipFile(self.output, 'w', zipfile.ZIP_DEFLATED)

        files = os.listdir(self.packdir)

        for f in files:

            if os.path.isdir(os.path.join(self.packdir, f)):
                self.pack_dir(f)
            elif os.path.isfile(os.path.join(self.packdir, f)):
                src = os.path.join(self.packdir, f)
                arcname = f
                print "Packing : " + f
                self.zf.write(src, arcname)

        self.zf.close()

    def pack_dir(self, zdir):
        pdir = os.path.join(self.packdir, zdir)

        files = os.listdir(pdir)

        for f in files:

            if os.path.isdir(os.path.join(pdir, f)):
                self.pack_dir(os.path.join(zdir, f))
            elif os.path.isfile(os.path.join(pdir, f)):
                src = os.path.join(pdir, f)
                arcname = os.path.join(zdir, f)
                print "Packing : " + arcname
                self.zf.write(src, arcname)

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
        self.lib_dirs = []
        
        self.read_settings()
        
    def read_settings(self):
        if os.path.exists(".compiler"):
            
            fp = open(".compiler", 'r')
            lines = fp.readlines()
            fp.close()
            
            for l in lines:
                if l.startswith("G++:"):
                    self.gpp = l[4:].strip()
                elif l.startswith("PATH:"):
                    self.gpp_path = l[5:].strip()
                elif l.startswith("GCC:"):
                    self.gcc = l[4:].strip()

        else:
            self.write_settings()
    
    def write_settings(self):
        
        fp = open(".compiler", 'w')
        
        lines = []
        
        lines.append("G++:"+self.gpp+"\n")
        lines.append("PATH:"+self.gpp_path+"\n")
        lines.append("GCC:"+self.gcc+"\n")
        
        fp.writelines(lines)
        
        fp.close()

    def reset(self):
        self.includes = []
        self.links = []
        self.link_args = []
        self.objs_prefix = []
        self.lib_dirs = []

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
        self.verbose_lvl = 1 #todo
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

    def do_clean(self):
        print "Cleaning for " + self.projname
        clean_dir = os.path.join(self.projname, self.obj_dir)
        
        files = os.listdir(clean_dir)
        
        for f in files:
            
            fpath = os.path.join(clean_dir, f)
            
            if self.verbose_lvl >= 3:   
                print "Deleting : " + f
                
            os.remove(fpath)
        
        clean_dir = self.bin_dir
        
        files = os.listdir(clean_dir)
        
        for f in files:
            
            fpath = os.path.join(clean_dir, f)
            
            if self.verbose_lvl >= 3:
                print "Deleting : " + f
                
            os.remove(fpath)

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
            
            if not fcpp.find(' ') == -1:
                fcpp = "\"" + fcpp +  "\""


            args.append("-o")
            args.append(fout)
            
            args.append(fcpp)
            
            cmd = ""

            for a in args:
                cmd += a + " " 
            
            if self.verbose_lvl > 2:
                print cmd
 
            self.log.build_obj(cmd)
            #change this to use subexec
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True)

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
                print errtxt
                print "---------------------------------------------"
                print "Build failed ! abort..."
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


        for o in self.bin_objs:
            args.append(o)

        for l in self.compiler.lib_dirs:
            lib = os.path.abspath(l)
            if not lib.find(' ') == -1 :
                args.append("\"-L"+lib+"\"")
            else:
                args.append("-L"+lib)

        for l in self.compiler.link_args:
            args.append(l)


        args.append("-o")
        args.append(os.path.join(self.output))

        for l in self.compiler.links:
            args.append("-l"+l)

        cmd = ""

        for a in args:
            cmd += a + " "

        self.log.link_proj(cmd)
        print "Linking objects..."
        
        if self.verbose_lvl > 2:
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
            self.log.std_err(errtxt)
            self.log.end_proj(False)
            print errtxt
            print "------------------------------------------"
            print "Linking failed , abort"
            os.chdir("..")
            self.log.save()
            return False
        else:
            self.log.end_proj()
            print "Build success !"

        os.chdir("..")

        self.log.save()
        return True


class script:
    
    def __init__(self, spath):
        self.path = spath
        self.working_dir = None
        self.args = []
        
    def run(self):
        
        return None


class pymake_file:
    
    def __init__(self, fpath):
        self.path = fpath
        self.posts = []
        self.pres = []
        self.verbose_lvl = 0


    def read(self):
        
        fp = open(self.path, 'r')
        
        lines = fp.readlines()
        
        fp.close()
        
        for l in lines:
            l = l.strip()
            
            if l.startswith('post:'):
                args = l[5:]
                args = args.split(',')
                i = 0
                ps = script(args[0])
                
                for a in args:
                    if i == 1:
                        #working_dir
                        ps.working_dir = a
                    elif not i == 0:
                        ps.args.append(a)
                    i = i + 1
                    
                self.posts.append(ps)
            elif l.startswith("pre:"):
                args = l[4:]
                args = args.split(',')
                i = 0
                ps = script(args[0])
                
                for a in args:
                    if i == 1:
                        ps.working_dir = a
                    elif not i == 0:
                        ps.args.append(a)
                        
                    i = i + 1
                    
                self.pres.append(ps)

    def run_script(self, s):
        args = []
        args.append("python")
        args.append(s.path)
            
        for a in s.args:
            args.append(a)
            
        if self.verbose_lvl >= 2:
            cmd = ""
            for a in args:
                cmd = cmd + a + " "
            print cmd
            
        sub = subexec(args)
        sub.run()
            
            
        if self.verbose_lvl >= 1:
            print sub.stdout

    def do_post_build(self):
        
        if not len(self.posts) == 0:    
            print "Running post build..."
        
        for s in self.posts:
            self.run_script(s)
        
    
    def do_pre_build(self):
        
        if not len(self.pres) == 0:
            print "Running pre build..."
        
        for s in self.pres:
            self.run_script(s)
        
        return None
    

class build_file:

    def __init__(self, path):
        self.path = path
        self.info = compiler()
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
        
