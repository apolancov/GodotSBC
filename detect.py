import os
import sys
import platform

def get_name():
    return 'sbc'

def can_build():
    if os.name != "posix":
        return False
    
    # Check for SDL2 development libraries
    if os.system("pkg-config --exists sdl2") != 0:
        print("SDL2 development libraries not found. Please install libsdl2-dev or equivalent.")
        return False
    
    return True

def get_opts():
    from SCons.Variables import BoolVariable, EnumVariable
    
    return [
        BoolVariable("use_sdl2_audio", "Use SDL2 audio driver", False),
        BoolVariable("use_sdl2_video", "Use SDL2 video driver", False),
        #EnumVariable("sdl2_gl_driver", "SDL2 GL driver", "desktop", ("desktop", "es", "es2")),
        EnumVariable("linker", "Linker program", "default", ("default", "bfd", "gold", "lld", "mold")),
        #BoolVariable("gles3", "Enable OpenGL ES 3 rasterizer", False),
        
        BoolVariable("use_llvm", "Use the LLVM compiler", False),
        BoolVariable("use_static_cpp", "Link libgcc and libstdc++ statically for better portability", True),
        BoolVariable("use_coverage", "Test Godot coverage", False),
        BoolVariable("use_ubsan", "Use LLVM/GCC compiler undefined behavior sanitizer (UBSAN)", False),
        BoolVariable("use_asan", "Use LLVM/GCC compiler address sanitizer (ASAN)", False),
        BoolVariable("use_lsan", "Use LLVM/GCC compiler leak sanitizer (LSAN)", False),
        BoolVariable("use_tsan", "Use LLVM/GCC compiler thread sanitizer (TSAN)", False),
        BoolVariable("use_msan", "Use LLVM compiler memory sanitizer (MSAN)", False),
        BoolVariable("use_sowrap", "Dynamically load system libraries", False),
        BoolVariable("alsa", "Use ALSA", False),
        BoolVariable("pulseaudio", "Use PulseAudio", False),
        BoolVariable("dbus", "Use D-Bus to handle screensaver and portal desktop settings", False),
        BoolVariable("speechd", "Use Speech Dispatcher for Text-to-Speech support", False),
        BoolVariable("fontconfig", "Use fontconfig for system fonts support", False),
        BoolVariable("udev", "Use udev for gamepad connection callbacks", False),
        BoolVariable("x11", "Enable X11 display", False),
        BoolVariable("wayland", "Enable Wayland display", False),
        BoolVariable("libdecor", "Enable libdecor support", False),
        BoolVariable("touch", "Enable touch events", False),
        BoolVariable("execinfo", "Use libexecinfo on systems where glibc is not available", False),
        ]

def get_flags():
    return [
       
    ]

def configure(env):
    # Base flags
    env.Prepend(CPPPATH=["#platform/sbc"])

    env.Append(CPPDEFINES=["PLATFORM_SBC"])
    env.Append(CPPDEFINES=["UNIX_ENABLED"])
    env.Append(CPPDEFINES=["LINUX_ENABLED"])

    env.Append(CPPFLAGS=['-DUNIX_ENABLED'])
    env.Append(CPPDEFINES=[('_FILE_OFFSET_BITS', 64)])
    env.Append(CXXFLAGS=["-std=c++17"])

    # SDL2 flags and libraries
    env.ParseConfig("pkg-config --cflags --libs sdl2")
   # env.Append(LIBS=['SDL2'])
    
    # System libraries
    env.Append(LIBS=["pthread"])
    env.Append(LIBS=["dl"])
    env.Append(LIBS=["z"])
  #  env.Append(LIBS=['GL'])
       
    # Vulkan support
    if env["vulkan"]:
        env.Append(CPPDEFINES=["VULKAN_ENABLED", "RD_ENABLED"])
        #env.Append(CPPDEFINES=["VULKAN_ENABLED"])
        # if not env["use_volk"]:
        #     env.Append(LIBS=["vulkan"])
        if not env["builtin_glslang"]:
            # No pkgconfig file so far, hardcode expected lib name.
            env.Append(LIBS=["glslang", "SPIRV"])
    
    # OpenGL ES 3 support
    if env["opengl3"]:
        #env.Prepend(CPPPATH=["#thirdparty/glad"])
        env.Append(CPPDEFINES=["GLES3_ENABLED"])
        #env.Append(CPPDEFINES=["GLES_API_ENABLED"])
        #env.Append(CPPDEFINES=["EGL_ENABLED"])
        #env.Append(CPPDEFINES=["GLAD_ENABLED"])

    
    if env['CXX'] == 'clang++':
        env['CC'] = 'clang'
        env['LD'] = 'clang++'
    
    if env['use_static_cpp']:
        env.Append(LINKFLAGS=['-static-libgcc', '-static-libstdc++'])
    
    # CPU architecture flags.
    if env["arch"] == "rv64":
        # G = General-purpose extensions, C = Compression extension (very common).
        env.Append(CCFLAGS=["-march=rv64gc"])

    ## Compiler configuration

    if "CXX" in env and "clang" in os.path.basename(env["CXX"]):
        # Convenience check to enforce the use_llvm overrides when CXX is clang(++)
        env["use_llvm"] = True

    if env["use_llvm"]:
        if "clang++" not in os.path.basename(env["CXX"]):
            env["CC"] = "clang"
            env["CXX"] = "clang++"
        env.extra_suffix = ".llvm" + env.extra_suffix
