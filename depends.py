import pickle
import zipfile
import os
import sys
import xml.etree.ElementTree as ET
import urllib2

class metaversion:

    def __init__(self, major = 0, minor = 0, revision = 0, build = 0, codename = ''):
        self.major = major
        self.minor = minor
        self.revision = revision
        self.build = build
        self.codename = codename
        
    def get_dict(self):
        dict = { 'major': str(self.major), 'minor': str(self.minor), 'revision': str(self.revision), 'build': str(self.build), 'codename': self.codename }

        return dict
    
    def from_dict(self, dict):
        for k in dict:
            if k == 'major':
                self.major = int(dict[k])
            elif k == 'minor':
                self.minor = int(dict[k])
            elif k == 'revision':
                self.revision = int(dict[k])
            elif k == 'build':
                self.build = int(dict[k])
            elif k == 'codename':
                self.codename = dict[k]
                
    def to_string(self):
        return "%d.%d.%d.%d-%s" % (self.major, self.minor, self.revision, self.build, self.codename)
    
    def from_string(self, text):
        vars = text.split('.')
        
        i = 0
        
        for v in vars:
            
            if i == 0:
                self.major = int(v)
            elif i == 1:
                self.minor = int(v)
            elif i == 2:
                if '-' in v:
                    le = v.split('-', 2)
                    self.revision = int(le[0])
                    
                    if len(le) > 1:
                        self.codename = le[1]
                        
                    break
                else:
                    self.revision = int(v)
            elif i == 3:
                if '-' in v:
                    le = v.split('-', 2)
                    if len(le) == 1:
                        self.build = int(le[0])
                    else:
                        self.build = int(le[0])
                        self.codename = le[1]
            
            i = i + 1

class metapackage:
    
    def __init__(self, name = '', author = '', website = ''):
        self.name = name
        self.author = author
        self.website = website
        self.versions = []
        
    def generate_xml(self, output = 'info.xml'):
        root = ET.Element('metapackage')
        
        name = ET.SubElement(root, 'name')
        name.text = self.name
        
        author = ET.SubElement(root, 'author')
        author.text = self.author
        
        website = ET.SubElement(root, 'website')
        website.text = self.website
        
        tree = ET.ElementTree(root)
        tree.write(output)
    
    def read_xml(self, input = 'info.xml'):
        
        tree = ET.parse(input)
        root = tree.getroot()
        
        for c in root:
            if c.tag == 'name':
                self.name = c.text
            elif c.tag == 'author':
                self.author = c.text
            elif c.tag == 'website':
                self.website = c.text
                
    def pack(self, root, pkg):
        
        apath = os.path.join(root, pkg + '.zip')
        rpath = os.path.join(root, pkg)
        
        zf = zipfile.ZipFile(apath, 'w', zipfile.ZIP_DEFLATED)
    
        files = os.listdir(rpath)
    
        for f in files:
            fpath = os.path.join(rpath, f)
            
            if os.path.isdir(fpath):
                self.pack_dir(zf, rpath, f)
            else:
                zf.write(fpath, f)
                
        zf.close()
        
    def pack_dir(self, zf, root, rel):
        
        fpath = os.path.join(root, rel)
        
        files = os.listdir(fpath)
            
        for f in files:
            rpath = os.path.join(fpath, f)
            
            if os.path.isdir(rpath):
                self.pack_dir(zf, root, os.path.join(rel, f))
            else:
                apath = os.path.join(rel, f)
                zf.write(rpath, apath)
                
            
class repo_index:
    
    #repos will be structured as /index.xml
    #                            /package-name/version.zip
    #                    ex. :   /stipersist/0.0.0.1-codename.zip
    # project must have meta info
    #                    ex. :   /stipersist/info.xml
    
    def __init__(self, name = 'default'):
        self.name = name
        self.email = ''
        self.website = ''
        
        self.packages = []
    
    def build_index(self, root):
        
        if os.path.exists(os.path.join(root, 'index.xml')):
            self.read_xml(os.path.join(root, 'index.xml'))
            self.packages = []
        
        files = os.listdir(root)
        
        for f in files:
            fpath =  os.path.join(root, f)
            
            if os.path.isdir(fpath):
                self.scan_pkg(fpath)
        
        self.generate_xml(os.path.join(root, 'index.xml'))
    
    def scan_pkg(self, ppath):
        
        pkgname = os.path.basename(ppath)
        
        info = os.path.join(ppath, 'info.xml')
        
        if os.path.exists(info):
            pkg = metapackage()
            pkg.read_xml(info)
            
            #scanning version
            
            files = os.listdir(ppath)
            
            for f in files:
                if f.endswith('.zip'):
                    pversion = f[0:-4]
                    mversion = metaversion()
                    mversion.from_string(pversion)
                    
                    pkg.versions.append(mversion)
            self.packages.append(pkg)
    
    def generate_xml(self, output = 'index.xml'):
        
        root = ET.Element('repos')
        
        header = ET.SubElement(root, 'header')
        
        name = ET.SubElement(header, 'name')
        name.text = self.name
        
        email = ET.SubElement(header, 'email')
        email.text = self.email
        
        website = ET.SubElement(header, 'website')
        website.text = self.website
        
        packages = ET.SubElement(root, 'packages')
        
        for p in self.packages:
            
            proot = ET.SubElement(packages, 'pkg')
            
            pname = ET.SubElement(proot, 'name')
            pname.text = p.name
            
            pauthor = ET.SubElement(proot, 'author')
            pauthor.text = p.author
            
            pwebsite = ET.SubElement(proot, 'website')
            pwebsite.text = p.website
            
            pversion = ET.SubElement(proot, 'versions')
            
            for v in p.versions:
                pv = ET.SubElement(pversion, 'version')
                pv.text = v.to_string()
            
        
        tree = ET.ElementTree(root)
        tree.write(output)


    def read_xml(self, input = 'index.xml'):
        
        tree = ET.parse(input)
        root = tree.getroot()
        
        for c in root:
            #repo header
            if c.tag == 'header':
                self.parse_header(c)
            if c.tag == 'packages':
                for p in c:
                    self.parse_package(p)

    
    def parse_package(self, package):
        
        pkg = metapackage()
        
        for c in package:
            if c.tag == 'name':
                pkg.name = c.text
            elif c.tag == 'author':
                pkg.author = c.text
            elif c.tag == 'website':
                pkg.website = c.text
            elif c.tag == 'versions':
                for v in c:
                    self.parse_version(pkg, v)

        self.packages.append(pkg)

    def parse_version(self, pkg, version):
        
        vstr = version.text
        v = metaversion()
        v.from_string(vstr)
        pkg.versions.append(v)
        
        
    def parse_header(self, header):
        
        for c in header:
            if c.tag == 'name':
                self.name = c.text
            elif c.tag == 'email':
                self.email = c.text
            elif c.tag == 'website':
                self.website = c.text

def download(remote, destination):
    print "Retrieving file : %s" % (remote)
    
    req = urllib2.Request(remote)
    
    resp = urllib2.urlopen(req)
    
    fp = open(destination, 'wb')
    
    bufsize = 16384
    length = resp.info().getheaders('Content-Length')[0]
    length = int(length)
    current = 0
    chunk = resp.read(bufsize)
    last_prc = None
    i = 0
    
    while len(chunk) == bufsize:
        
        current = current + len(chunk)
        prc = (current*100) / length
        
        if not prc == last_prc:
            prefix = ""
            nb = i / 5
            for x in range(nb):
                prefix = prefix + "="
            i = i + 1
            
            print prefix + "> " + str(prc) + "%"
            last_prc = prc
        
        fp.write(chunk)
        
        chunk = resp.read(bufsize)
        
    fp.write(chunk)
    fp.close()
    
    print "Download complete !"
    

class remote_repo(repo_index):
    
    def __init__(self, url):
        self.url = url
        repo_index.__init__(self)
        self.index_url = ""
        if self.url.endswith('/'):
            self.index_url = url + "index.xml"
        else:
            self.index_url = url + "/index.xml"
            
        download(self.index_url, 'repo.xml')
        
        self.read_xml('repo.xml')

if __name__ == '__main__':

    #arguments parsing
    
    argc = len(sys.argv)
    ai = 0
    
    script_path = sys.argv[ai]
    
    mode = None
    root = 'root'
    pname = None
    pauthor = None
    pwebsite = None
    pversion = None
    
    rurl = None
    
    while ai < argc:
        if not ai == 0:
            arg = sys.argv[ai]
            
            if arg == '-root':
                #root folder
                ai = ai + 1
                root = sys.argv[ai]
            elif arg == '-newpkg':
                #new project
                #-new [name],[author],[website]
                mode ='newpkg'
                ai = ai + 1
                param = sys.argv[ai]
                data = param.split(',')
                
                i = 0
                
                for d in data:
                    if i == 0:
                        pname = d
                    elif i == 1:
                        pauthor = d
                    elif i == 2:
                        pwebsite = d
                    
                    i = i + 1
            elif arg == '-packversion':
                #pack version
                #-packversion project 0.0.0.0-codename
                mode = 'packversion'
                ai = ai + 1
                pname = sys.argv[ai]
                ai = ai + 1
                pversion = sys.argv[ai]
            elif arg == '-buildindex':
                mode = 'buildindex'
            elif arg == '-scanrepo':
                mode = 'scanrepo'
                ai = ai + 1
                rurl = sys.argv[ai]
                
        ai = ai + 1
        
    
    if not os.path.exists(root):
        os.makedirs(root)
        
    if mode == 'newpkg':
        print "Creating new package in repository"
        ppath = os.path.join(root, pname)
        
        if not os.path.exists(ppath):
            os.makedirs(ppath)
        
        pkg = metapackage(pname, pauthor, pwebsite)
        
        xpath = os.path.join(ppath, 'info.xml')
        
        pkg.generate_xml(xpath)
        
        print "Package head created !"
        
    elif mode == 'packversion':
        print "Packing version : %s " % pversion
    
        proot = os.path.join(root, pname)
        
        pkg = metapackage()
        
        if not os.path.exists(proot):
            print "Package not existing !"
        else:
            pkg.pack(proot, pversion)
            print "%s - %s packed !" % (pname, pversion)
    elif mode == 'buildindex':
        repo = repo_index()
        repo.build_index(root)
    elif mode == 'scanrepo':
        
        rrepo = remote_repo(rurl)
        
        print "Repo : %s" % rrepo.name
        
        for p in rrepo.packages:
            print "Package : %s" % p.name
            
            for v in p.versions:
                print "\t Version : %s" % v.to_string()