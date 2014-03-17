#builder gui
#using PyQt4
#http://hivelocity.dl.sourceforge.net/project/pyqt/PyQt4/PyQt-4.10.3/PyQt4-4.10.3-gpl-Py2.7-Qt4.8.5-x64.exe

import sys
import os
import ide_project
import make
import subprocess
from PyQt4 import QtGui, QtCore
   
        
class workspace_handler:
    
    def __init__(self, workspace):
        self.workspace = workspace
    
    def get_builds(self, project_name = None):
        for p in self.workspace.projects:
            if p.parser.project_name == project_name:
                return p.parser.builds
        
        return None
    
    def get_project(self, project_name):
        for p in self.workspace.projects:
            if p.parser.project_name == project_name:
                return p
            
        return None
    
    def is_workspace(self):
        return True

class project_handler:
    
    def __init__(self, parser):
        self.parser = parser
    
    def get_builds(self, project_name = None):
        return self.parser.builds
    
    def get_project(self, project_name):
        return self.parser
    
    def is_workspace(self):
        return False

class compiler_dialog(QtGui.QDialog):
    
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.compiler = make.compiler()
        self.init_ui()
    
    def browse_gpp(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Locate C++ Compiler', os.getcwd())
        if os.path.exists(fname):
            name = os.path.basename(str(fname))
            self.compiler.gpp = name
            self.lbl_v_gpp.setText(name)
        
    def browse_gc(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Locate C Compiler', os.getcwd())
        if os.path.exists(fname):
            name = os.path.basename(str(fname))
            self.compiler.gcc = name
            self.lbl_v_gc.setText(name)
    
    def browse_bin_path(self):
        cpath = QtGui.QFileDialog.getExistingDirectory(self, "Compiler Binary Folder", os.getcwd())
        
        if os.path.exists(cpath):
            self.compiler.gpp_path = str(cpath)
            self.lbl_v_bin_path.setText(cpath)
        
    def save_quit(self):
        self.compiler.gpp = str(self.lbl_v_gpp.text())
        self.compiler.gcc = str(self.lbl_v_gc.text())
        self.compiler.gpp_path = str(self.lbl_v_bin_path.text())
        self.compiler.write_settings()
        self.close()
        
    def init_ui(self):
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        
        self.lbl_gpp = QtGui.QLabel("C++ Compiler :")
        self.lbl_v_gpp = QtGui.QLineEdit(self)
        self.lbl_v_gpp.setText(self.compiler.gpp)
        self.btn_b_gpp = QtGui.QPushButton("...", self)
        self.btn_b_gpp.clicked.connect(self.browse_gpp)
        
        self.lbl_gc = QtGui.QLabel("C Compiler :")
        self.lbl_v_gc = QtGui.QLineEdit(self)
        self.lbl_v_gc.setText(self.compiler.gcc)
        self.btn_b_gc = QtGui.QPushButton("...", self)
        self.btn_b_gc.clicked.connect(self.browse_gc)
        
        self.lbl_bin_path = QtGui.QLabel("Compiler path :")
        self.lbl_v_bin_path = QtGui.QLineEdit(self)
        self.lbl_v_bin_path.setText(self.compiler.gpp_path)
        self.btn_b_bin_path = QtGui.QPushButton("...", self)
        self.btn_b_bin_path.clicked.connect(self.browse_bin_path)
        
        self.btn_save_quit = QtGui.QPushButton("Save and Close", self)
        self.btn_save_quit.clicked.connect(self.save_quit)
        
        self.btn_close = QtGui.QPushButton("Close", self)
        self.btn_close.clicked.connect(self.close)
        
        grid.addWidget(self.lbl_gpp, 0, 0)
        grid.addWidget(self.lbl_v_gpp, 0, 1)
        grid.addWidget(self.btn_b_gpp, 0, 2)
        
        grid.addWidget(self.lbl_gc, 1, 0)
        grid.addWidget(self.lbl_v_gc, 1, 1)
        grid.addWidget(self.btn_b_gc, 1, 2)
        
        grid.addWidget(self.lbl_bin_path, 2, 0)
        grid.addWidget(self.lbl_v_bin_path, 2, 1)
        grid.addWidget(self.btn_b_bin_path, 2, 2)
        
        grid.addWidget(self.btn_save_quit, 3, 0)
        grid.addWidget(self.btn_close, 3, 2)
        
        self.setLayout(grid)
        self.setGeometry(150, 300, 500, 200)
        self.setWindowTitle("Compiler Configuration")
        self.show()

class main_frame(QtGui.QMainWindow):
    
    def __init__(self):
        super(main_frame, self).__init__()
        
        self.init_ui()
    
    def set_lbl_type(self, itype):
        if itype == 1:
            self.lbl_project_type.setText("Executable")
        elif itype == 2:
            self.lbl_project_type.setText("Static Library")
        elif itype == 3:
            self.lbl_project_type.setText("Dynamic Library")
        
    
    def open_project_file(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open project file', os.getcwd())
        
        if os.path.exists(fname):
            if fname.endsWith('.cbp'):
                parser = ide_project.codeblock_parser(str(fname))
                parser.parse()
                
                self.handler = project_handler(parser)
                
                self.tbl_objects.clear()
                
                self.lbl_project_name.setText(parser.project_name)
                
                for o in parser.objects:
                    self.tbl_objects.addItem(o.name)
                
                self.cbox_builds.clear()
                
                self.build_changed(parser.builds[0].name)
                
                self.set_lbl_type(parser.builds[0].type)
                
                for b in parser.builds:
                    self.cbox_builds.addItem(b.name)
                

            elif fname.endsWith('.workspace'):
                print "Workspace file"
                self.grid.removeWidget(self.lbl_project_name)
                self.grid.addWidget(self.cbox_project_name, 1, 1)
                
                self.cbox_project_name.clear()
                
                workspace = ide_project.codeblock_workspace_parser(str(fname))
                workspace.parse()
                
                self.handler = workspace_handler(workspace)
                
                for p in workspace.projects:
                    self.cbox_project_name.addItem(p.name)
                    p.parser.parse()
                
                self.project_changed(workspace.projects[0].name)
                
    
    def init_menu(self):
        
        self.open_project = QtGui.QAction('Open project file...', self)
        self.open_project.triggered.connect(self.open_project_file)
        
        self.exit_action = QtGui.QAction('Exit', self)
        self.exit_action.setShortcut('Ctrl+Q')
        self.exit_action.setStatusTip('Exit application')
        self.exit_action.triggered.connect(self.close)
        
        menubar = self.menuBar()
        
        self.file_menu = menubar.addMenu('&File')
        self.file_menu.addAction(self.open_project)
        self.file_menu.addAction(self.exit_action)
    
    def init_ui(self):
        
        self.init_menu()
        
        self.main_widget = QtGui.QWidget()
        
        self.main_widget.setGeometry(0, 0, 600, 600)
        
        self.lbl_intro = QtGui.QLabel("Project Information")
        
        self.lbl_project = QtGui.QLabel('Project :')
        self.lbl_project_name = QtGui.QLabel("")
        
        self.cbox_project_name = QtGui.QComboBox()
        self.cbox_project_name.activated[str].connect(self.project_changed)
        
        self.lbl_type = QtGui.QLabel("Type :")
        self.lbl_project_type = QtGui.QLabel()
        
        self.lbl_builds = QtGui.QLabel("Build configuration :")
        self.cbox_builds = QtGui.QComboBox()
        self.cbox_builds.activated[str].connect(self.build_changed)
        
        self.lbl_compiler_incs = QtGui.QLabel("Include(s) :")
        self.tbl_compiler_incs = QtGui.QListWidget()
        
        self.lbl_lib_dirs = QtGui.QLabel("Linker dir(s) :")
        self.tbl_lib_dirs = QtGui.QListWidget()
        
        self.lbl_link_args = QtGui.QLabel("Linker argument(s) :")
        self.tbl_link_args = QtGui.QListWidget()

        self.lbl_obj_args = QtGui.QLabel("Object argument(s) :")
        self.tbl_obj_args = QtGui.QListWidget()
        
        self.lbl_objects = QtGui.QLabel('Object :')
        self.tbl_objects = QtGui.QListWidget()
        
        self.btn_compiler = QtGui.QPushButton("Compiler Configuration", self)
        self.btn_compiler.clicked.connect(self.open_compiler_dialog)
        
        self.btn_build = QtGui.QPushButton("Build", self)
        self.btn_build.clicked.connect(self.build)
        
        self.btn_close = QtGui.QPushButton("Close", self)
        self.btn_close.clicked.connect(self.close)
        
        grid = QtGui.QGridLayout()
        self.grid = grid
        grid.setSpacing(10)

        grid.addWidget(self.lbl_intro, 0, 0)
        grid.addWidget(self.btn_compiler, 0, 2)
        
        
        grid.addWidget(self.lbl_project, 1, 0)
        grid.addWidget(self.lbl_project_name, 1, 1)
        
        grid.addWidget(self.lbl_type, 1, 2)
        grid.addWidget(self.lbl_project_type, 1, 3)
        
        grid.addWidget(self.lbl_builds, 2, 0)
        grid.addWidget(self.cbox_builds, 2, 1)
        
        grid.addWidget(self.lbl_compiler_incs, 3, 0)
        grid.addWidget(self.tbl_compiler_incs, 3, 1)
        
        grid.addWidget(self.lbl_lib_dirs, 4, 0)
        grid.addWidget(self.tbl_lib_dirs, 4, 1)
        
        grid.addWidget(self.lbl_obj_args, 5, 0)
        grid.addWidget(self.tbl_obj_args, 5, 1)
        
        grid.addWidget(self.lbl_link_args, 5, 2)
        grid.addWidget(self.tbl_link_args, 5, 3)
        
        grid.addWidget(self.btn_build, 6, 1)
        grid.addWidget(self.btn_close, 6, 3)
        
        grid.addWidget(self.lbl_objects, 3, 2, 2, 1)
        grid.addWidget(self.tbl_objects, 3, 3, 2, 1)
        
        
        self.main_widget.setLayout(grid)
        
        
        self.setGeometry(150, 300, 600, 600)
        self.setWindowTitle("PyMake GUI")
        self.setCentralWidget(self.main_widget)
        self.show()

    def build(self):
        
        if self.handler.is_workspace():
            
            pfile = self.handler.workspace.wspace
            
            args = []
            args.append('build.py')
            args.append('-P:'+pfile)
            
            build_name = str(self.cbox_builds.currentText())

            args.append("-B:"+build_name)

            self.process = QtCore.QProcess(self)
            
            self.process.startDetached("python", args)

    def open_compiler_dialog(self):
        
        cframe = compiler_dialog(self)

    def project_changed(self, text):
        
        project = self.handler.get_project(str(text))
        
        self.cbox_builds.clear()
        for b in project.parser.builds:
            self.cbox_builds.addItem(b.name)
        
        self.tbl_objects.clear()
        
        for o in project.parser.objects:
            self.tbl_objects.addItem(o.name)
        
        self.build_changed(project.parser.builds[0].name)

    def build_changed(self, text):
        build_name = str(text)
        build = None
        builds = []
        if self.handler.is_workspace():
            builds = self.handler.get_builds(str(self.cbox_project_name.currentText()))
        else:
            builds = self.handler.get_builds()
        
        for b in builds:
            if b.name == build_name:
                build = b
        
        if not build == None:
            self.tbl_compiler_incs.clear()
            
            for i in build.includes:
                self.tbl_compiler_incs.addItem(i)
            
            self.tbl_lib_dirs.clear()
            
            for l in build.lib_dirs:
                self.tbl_lib_dirs.addItem(l)
            
            self.tbl_obj_args.clear()
            
            for a in build.obj_args:
                self.tbl_obj_args.addItem(a)
                
            self.tbl_link_args.clear()
            
            for a in build.link_args:
                self.tbl_link_args.addItem(a)

def main_gui():
    app = QtGui.QApplication(sys.argv)
    frame = main_frame()
    sys.exit(app.exec_())
    

if __name__ == '__main__':
    main_gui()
