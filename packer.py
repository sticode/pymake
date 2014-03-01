import os
import zipfile
import sys

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
