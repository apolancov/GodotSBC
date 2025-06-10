# GodotSBC
## Godot SDL 2 Implementation

## required library
```
sudo apt-get install build-essential scons pkg-config \
  clang llvm lld libsdl2-dev libgles2-mesa-dev
```

this don't work out of the box, you need to modify the Godot source code for make it's work.

first, add a compiler flag condition on rasterizerGLES3 on constructor method
/godot/drivers/gles3/rasterizer_gles3.cpp 

RasterizerGLES3::RasterizerGLES3()

you need to find the line 243 (this may can be different in godot 4.2, 4.3)

```
#endif // EGL_ENABLED

	if (gles_over_gl) {
		if (!glad_loaded && gladLoaderLoadGL()) {
			glad_loaded = true;
		}
	} else {
		if (!glad_loaded && gladLoaderLoadGLES2()) {
			glad_loaded = true;
		}
	}

	// FIXME this is an early return from a constructor.  Any other code using this instance will crash or the finalizer will crash, because none of
	// the members of this instance are initialized, so this just makes debugging harder.  It should either crash here intentionally,
	// or we need to actually test for this situation before constructing this.
	ERR_FAIL_COND_MSG(!glad_loaded, "Error initializing GLAD.");
```
and replace with this, put #include in include section

```
// put include in include section
#include "platform/sbc/display_server_sdl.h"

...

#endif // EGL_ENABLED

	if (gles_over_gl) {
		if (!glad_loaded && gladLoaderLoadGL()) {
			glad_loaded = true;
		}
	} else {
#ifdef PLATFORM_SBC
		if (!glad_loaded && gladLoadGLES2((GLADloadfunc)&get_gl_proc_address)) {
			glad_loaded = true;
		}
#else
		if (!glad_loaded && gladLoaderLoadGLES2()) {
			print_line("GLAD loaded GLES2");
			glad_loaded = true;
		}
#endif
```

## scons command for compile
scons platform=sbc target=template_release use_lto=no use_llvm=yes -j$(nproc) arch=arm64 tools=no		
