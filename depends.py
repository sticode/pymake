import pickle
import zipfile
import os
import sys

class metaversion:

    def __init__(self, major = 0, minor = 0, revision = 0, build = 0, codename = None):
        self.major = major
        self.minor = minor
        self.revision = revision
        self.build = build
        self.codename = codename


class package:

    def __init__(self):
        self.name = 'unknown'
        self.version = metaversion()

    def from_zip(self, zippath, tmp):
        man_name = 'package.manifest'
        zf = zipfile.ZipFile(zippath, 'r', zipfile.ZIP_DEFLATED)

        files = zf.namelist()

        found = False

        for f in files:
            if f == man_name:
                dest = os.path.join(tmp, f)
                zf.extract(f, dest)
                found = True
                break

        if found:
            fp = open(os.path.join(tmp, man_name))
            
            pkg = pickle.load(fp)

            fp.close()

            self.name = pkg.name
            self.version = pkg.version
        else:
            print "Manifest not found !"
        

    def build_zip(self, root, zipout, tmp):
        man_name = 'package.manifest'

        man_path = os.path.join(tmp, man_name)

        fp = open(man_path, 'w')

        pickle.dump(self, fp)

        fp.close()

        zf = zipfile.ZipFile(zipout, 'w', zipfile.ZIP_DEFLATED)

        zf.write(man_path, man_name)

        files = os.listdir(root)

        for f in files:
            fpath = os.path.join(root, f)
            if os.path.isdir(fpath):
                self.add_dir(zf, root, f)
            else:
                zf.write(fpath, f)

        zf.close()

    def add_dir(self, zf, root, reldir):

        files = os.listdir(os.path.join(root, reldir))

        for f in files:
            fpath = os.path.join(root, reldir, f)
            
            if os.path.isdir(fpath):
                self.add_dir(zf, root, os.path.join(reldir, f))
            else:
                rpath = os.path.join(reldir, f)
                zf.write(fpath, rpath)

if __name__ == '__main__':

    tmp_path = 'tmp_depends'

    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

    mode = None
    p_name = None
    p_v_major = 0
    p_v_minor = 0
    p_v_rev = 0
    p_v_build = 0
    p_out = None
    p_root = None

    ai = 0
    while ai < len(sys.argv):
        a = sys.argv[ai]
        if not ai == 0:
            if a == '-n':
                ai = ai + 1
                p_name = sys.argv[ai]
            elif a == '-v':
                ai = ai + 1
                version = sys.argv[ai]

                vs = version.split('.')
                vi = 0

                for v in vs:
                    if vi == 0:
                        p_v_major = int(v)
                    elif vi == 1:
                        p_v_minor = int(v)
                    elif vi == 2:
                        p_v_rev = int(v)
                    elif vi == 3:
                        p_v_build = int(v)

                    vi = vi + 1
            elif a == '-build':
                mode = 'build'
            elif a == '-o':
                ai = ai + 1
                p_out = sys.argv[ai]
            elif a == '-i':
                ai = ai + 1
                p_root = sys.argv[ai]
                
        ai = ai + 1

    if mode == 'build':
        print "Creating package : %s" % (p_name)

        pkg = package()

        pkg.name = p_name
        pkg.version.major = p_v_major
        pkg.version.minor = p_v_minor
        pkg.version.revision = p_v_rev
        pkg.version.build = p_v_build

        pkg.build_zip(p_root, p_out, tmp_path)
