import make
import os
import shutil
import packer
import sys

def exit_clean(build_config = "Release"):
    shutil.rmtree(os.path.join("stigame", "bin", build_config), True)
    shutil.rmtree(os.path.join("stigame", "obj", build_config), True)
    shutil.rmtree(os.path.join("stiuniverse", "bin", build_config), True)
    shutil.rmtree(os.path.join("stiuniverse", "obj", build_config), True)
    shutil.rmtree(os.path.join("assettools", "bin", build_config), True)
    shutil.rmtree(os.path.join("assettools", "obj", build_config), True)
    shutil.rmtree("deploy", True)
    exit()

def show_help():
    print "use this script like this : "
    print "build.py [args]value"
    print "--------------------------------"
    print "-B : Build Name"
    print "-CPP : C++ Compiler name"
    print "-CPATH : C++ Compiler Path"
    print "-DEBUG : Compile with debug symbol"
    print "-CC : C Compiler name"
    print ""
    exit()

if __name__ == '__main__':
    print "------------------------------"
    print "Python make Script"
    print "------------------------------"
    print "JordSti : jord52@gmail.com"
    print "------------------------------"
    
    info = make.compiler_info()
    build_name = "Release"
    build_num = "0"
    output_zip =  'stiuniverse.zip'
    debug = False

    index = 0
    for args in sys.argv:
        if index == 0:
            index = index + 1
            continue

        if args.startswith('-B'):
            build_num = args[2:]
            print "Setting Build Name : " + build_num
        elif args.startswith('-CPP'):
            cpp_bin = args[4:]
            print "Setting C++ Compiler : " + cpp_bin
            info.gpp = cpp_bin
        elif args.startswith('-CPATH'):
            cpp_path = args[6:]
            print "Setting C++ Compiler Path : " + cpp_path
            info.gpp_path = cpp_path
        elif args.endswith('-CC'):
            cc_bin = args[3:]
            print "Setting C Compiler : " + cc_bin
            info.gcc = cc_bin
        elif args.startswith('-DEBUG'):
            build_name = "Debug"
            debug = True
            print "Setting Debug mode compilation"
        elif args.startswith("-HELP"):
            show_help()

        index = index + 1


    if debug:
        output_zip =  'stiuniverse-'+build_num+'-debug.zip'
    else:
        output_zip =  'stiuniverse-'+build_num+'.zip'
        
    info.set_env()

    #g++ exec test
    se = make.subexec([info.gpp, '--version'])
    se.run()
    print se.stdout

    if not os.path.exists("deploy"):
        os.mkdir("deploy")

    #building stigame
    info.includes.append("..\\include\\SDL2")
    info.build_num = build_num
    info.links.append("SDL2main")
    info.links.append("SDL2")
    info.links.append("SDL2_image")
    info.links.append("SDL2_ttf")
    info.links.append("SDL2_gfx")
    info.link_args.append("-shared")
    
    if debug:      
        info.link_args.append("-Wl,--output-def=bin\Debug\libStiGame.def")
        info.link_args.append("-Wl,--out-implib=bin\Debug\libStiGame.a")
    else:
        info.link_args.append("-Wl,--output-def=bin\Release\libStiGame.def")
        info.link_args.append("-Wl,--out-implib=bin\Release\libStiGame.a")
        
    info.link_args.append("-Wl,--dll")
    info.link_args.append("-L..\\lib\\")
    info.objs_prefix.append("-std=c++11")
    info.objs_prefix.append("-Wall")
    info.link_args.append("-s")
    
    if debug:
        info.objs_prefix.append("-g")
        info.objs_prefix.append("-DDEBUG")
    else:
        info.objs_prefix.append("-O2")
        info.objs_prefix.append("-DRELEASE")


    bp = make.build_project("stigame", info, build_name)
    bp.output = "..\\deploy\\StiGame.dll"
    bp.scan_files()
    
    if not bp.build_objects():
        print "Error building stigame, aborting..."
        exit_clean(build_name)
        
    if not bp.link():
        print "Error building stigame, aborting..."
        exit_clean(build_name)


    #building assettools
    info.reset()
    info.build_num = build_num
    info.includes.append("..\\include\\SDL2")
    info.includes.append("..\\stigame")
    info.links.append("mingw32")
    info.links.append("SDL2main")
    info.links.append("SDL2")
    info.links.append("SDL2_image")
    info.links.append("SDL2_ttf")
    info.links.append("SDL2_gfx")
    info.links.append("StiGame")
    info.link_args.append("-L..\\lib\\")
    info.link_args.append("-s")
    
    if debug:
        info.link_args.append("-L..\\stigame\\bin\\Debug\\")
    else:
        info.link_args.append("-L..\\stigame\\bin\\Release\\")

    info.objs_prefix.append("-std=c++11")
    info.objs_prefix.append("-Wall")

    if debug:
        info.objs_prefix.append("-g")
        info.objs_prefix.append("-DDEBUG")
    else:    
        info.objs_prefix.append("-O2")
        info.objs_prefix.append("-DRELEASE")


    bp = make.build_project("assettools", info, build_name)
    bp.output = "..\\deploy\\assettools.exe"
    bp.scan_files()
    if not bp.build_objects():
        print "Error building assettools, aborting..."
        exit_clean(build_name)
        
    if not bp.link():
        print "Error building assettools, aborting..."
        exit_clean(build_name)

    #building stiuniverse
    info.reset()
    info.build_num = build_num
    info.includes.append("..\\include\\SDL2")
    info.includes.append("..\\stigame")
    info.links.append("mingw32")
    info.links.append("SDL2main")
    info.links.append("SDL2")
    info.links.append("SDL2_image")
    info.links.append("SDL2_ttf")
    info.links.append("SDL2_gfx")
    info.links.append("StiGame")
    #info.link_args.append("-shared")
    #info.link_args.append("-Wl,--output-def=bin\Debug\libStiGame.def")
    #info.link_args.append("-Wl,--out-implib=bin\Debug\libStiGame.a")
    #info.link_args.append("-Wl,--dll")
    info.link_args.append("-L..\\lib\\")
    info.link_args.append("-s")
    
    if debug:
        info.link_args.append("-L..\\stigame\\bin\\Debug\\")
    else:
        info.link_args.append("-L..\\stigame\\bin\\Release\\")
        
    info.objs_prefix.append("-std=c++11")
    info.objs_prefix.append("-Wall")

    if debug:
        info.objs_prefix.append("-g")
        info.objs_prefix.append("-DDEBUG")
    else:
        info.objs_prefix.append("-O2")
        info.objs_prefix.append("-DRELEASE")

    bp = make.build_project("stiuniverse", info, build_name)
    bp.output = "..\\deploy\\StiUniverse.exe"
    bp.scan_files()
    if not bp.build_objects():
        print "Error building stiuniverse, aborting..."
        exit_clean(build_name)
        
    if not bp.link():
        print "Error building stiuniverse, aborting..."
        exit_clean(build_name)

    #dlls dependency
    dc = make.dll_copy()
    dc.copy()

    #assets copying
    ac = make.assets_copy( 'assets', os.path.join('deploy', 'assets') )
    ac.copy()

    #assets building
    sprites = ['a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'd0', 'd1']
    dsprites = ['vessel0']

    os.chdir('deploy')

    for s in sprites:
        cmd = ['assettools', 'sprite', s]
        se = make.subexec(cmd)
        se.run()
        print se.stdout
        
        shutil.rmtree(os.path.join("assets","sprites", s))
        os.remove(os.path.join("assets", "sprites", s + ".spr"))
        
    for ds in dsprites:
        cmd = ['assettools', 'dsprite', ds]
        se = make.subexec(cmd)
        se.run()
        print se.stdout

        shutil.rmtree(os.path.join("assets","sprites", ds))
        os.remove(os.path.join("assets", "sprites", ds + ".dspr"))

    os.chdir('..')

    #cleaning folder

    shutil.rmtree(os.path.join("stigame", "bin", build_name))
    shutil.rmtree(os.path.join("stigame", "obj", build_name))
    shutil.rmtree(os.path.join("stiuniverse", "bin", build_name))
    shutil.rmtree(os.path.join("stiuniverse", "obj", build_name))
    shutil.rmtree(os.path.join("assettools", "bin", build_name))
    shutil.rmtree(os.path.join("assettools", "obj", build_name))

    pack = packer.packer('deploy', output_zip)
    pack.pack()

    shutil.rmtree("deploy")

    if os.path.exists("deploy"):
        #still exists
        print "Forcing delete : deploy"
        os.remove("deploy")

    print "Build endend !"
    


