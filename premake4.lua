require "config"

solution "EiffelRunTime"
	configurations { "debug", "release" }

	location "../../build/runtime"
	targetdir "../../build/runtime/spec/lib"
	language "C"
	includedirs {".", "run-time", "run-time/include", "idrs", "ipc/app", "ipc/shared"}
	
	buildoptions (warning_level)

	configuration "Windows"
		includedirs {"console"}
		buildoptions {"-W4 -wd4055 -wd4054 -wd4100 -wd4702 -wd4706 -wd4510 -wd4512 -wd4610",
			"-nologo -MT -D_WIN32_WINNT=0x0500 -DWINVER=0x0500" }
		defines {"_CRT_SECURE_NO_DEPRECATE", "_CRT_NONSTDC_NO_DEPRECATE"}
		links {"kernel32", "user32", "gdi32", "winspool", "comdlg32", "advapi32", "shell32", "ole32", "oleaut32", "uuid", "wsock32"}

	-- All of these settings will appear in the Debug configuration
-- 	filter "configurations:Debug"
	configuration "debug"
		defines { "ISE_USE_ASSERT" }
		flags { "Symbols" }

	-- All of these settings will appear in the Release configuration
-- 	filter "configurations:Release"
	configuration "release"
		buildoptions (optimize)

local rt_base = {
	"run-time/malloc.c",
	"run-time/garcol.c",
	"run-time/local.c",
	"run-time/store.c",
	"run-time/retrieve.c",
	"run-time/hash.c",
	"run-time/traverse.c",
	"run-time/hashin.c",
	"run-time/tools.c",
	"run-time/internal.c",
	"run-time/plug.c",
	"run-time/copy.c",
	"run-time/equal.c",
	"run-time/lmalloc.c",
	"run-time/out.c",
	"run-time/timer.c",
	"run-time/urgent.c",
	"run-time/sig.c",
	"run-time/hector.c",
	"run-time/cecil.c",
	"run-time/file.c",
	"run-time/dir.c",
	"run-time/misc.c",
	"run-time/error.c",
	"run-time/umain.c",
	"run-time/memory.c",
	"run-time/memory_analyzer.c",
	"run-time/argv.c",
	"run-time/boolstr.c",
	"run-time/search.c",
	"run-time/run_idr.c",
	"run-time/path_name.c",
	"run-time/object_id.c",
	"run-time/eif_threads.c",
	"run-time/eif_project.c",
	"run-time/posix_threads.c",
	"run-time/gen_conf.c",
	"run-time/eif_type_id.c",
	"run-time/rout_obj.c",
	"run-time/option.c",
	"run-time/compress.c",
	"run-time/console.c",
	"run-time/offset.c",
	"run-time/main.c",
	"run-time/except.c",

	"idrs/idrs.c"
}

local rt_workbench = {
	"run-time/debug.c",
	"run-time/interp.c",
	"run-time/update.c",
	"run-time/wbench.c",

	"ipc/shared/com.c",
	"ipc/shared/identify.c",
	"ipc/shared/logfile.c",
	"ipc/shared/network.c",
	"ipc/shared/select.c",
	"ipc/shared/shword.c",
	"ipc/shared/stack.c",
	"ipc/shared/stream.c",
	"ipc/shared/system.c",
	"ipc/shared/transfer.c",
	"ipc/shared/rqst_idrs.c",
	
	"ipc/shared/uu.c",

	"ipc/app/app_listen.c",
	"ipc/app/app_proto.c",
	"ipc/app/app_server.c",
	"ipc/app/app_transfer.c"
}

local rt_multithreaded = {"run-time/scoop/*.c"}

local rt_console = {"console/argcargv.c", "console/econsole.c"}

project "x2c"
	kind "ConsoleApp"
	targetdir "../../build/runtime/spec/bin"
	buildoptions (ccflags)
	linkoptions (ldccflags)
	files {"run-time/x2c.c", "run-time/offset.c"}

project "wkbench_static"
	kind "StaticLib"
	targetname "wkbench"
	defines "WORKBENCH"
	buildoptions (ccflags)
	linkoptions (ldflags)
	files (rt_base)
	files (rt_workbench)
	configuration "Windows"
		files (rt_console)

project "wkbench_shared"
	kind "SharedLib"
	targetname "wkbench"
	defines "WORKBENCH"
	buildoptions (ccflags)
	linkoptions (ldsharedflags)
	files (rt_base)
	files (rt_workbench)
	configuration "Windows"
		files (rt_console)

project "mtwkbench_static"
	kind "StaticLib"
	targetname "mtwkbench"
	defines {"WORKBENCH"}
	buildoptions (mtccflags)
	linkoptions (mtldflags)
	files (rt_base)
	files (rt_workbench)
	files (rt_multithreaded)
	configuration "Windows"
		files (rt_console)

project "mtwkbench_shared"
	kind "SharedLib"
	targetname "mtwkbench"
	defines {"WORKBENCH"}
	buildoptions (mtccflags)
	linkoptions (mtldsharedflags)
	files (rt_base)
	files (rt_workbench)
	files (rt_multithreaded)
	configuration "Windows"
		files (rt_console)

project "finalized_static"
	kind "StaticLib"
	targetname "finalized"
	buildoptions (ccflags)
	linkoptions (ldflags)
	files (rt_base)
	configuration "Windows"
		files (rt_console)

project "finalized_shared"
	kind "SharedLib"
	targetname "finalized"
	buildoptions (ccflags)
	linkoptions (ldsharedflags)
	files (rt_base)
	configuration "Windows"
		files (rt_console)

project "mtfinalized_static"
	kind "StaticLib"
	targetname "mtfinalized"
	buildoptions (mtccflags)
	linkoptions (mtldflags)
	files (rt_base)
	files (rt_multithreaded)
	configuration "Windows"
		files (rt_console)

project "mtfinalized_shared"
	kind "SharedLib"
	targetname "mtfinalized"
	buildoptions (mtccflags)
	linkoptions (mtldsharedflags)
	files (rt_base)
	files (rt_multithreaded)
	configuration "Windows"
		files (rt_console)

project "platform"
	kind "StaticLib"
	buildoptions (ccflags)
	linkoptions (ldflags)
	files {"platform/*.c"}
		-- The platform library location is hardcoded in some other scripts...
	targetdir "platform"
	
project "compiler"
	kind "StaticLib"
	buildoptions (ccflags)
	linkoptions (ldflags)
	files {"bench/*.c"}
		-- The compiler library location is hardcoded in some other scripts...
	targetdir "bench"

project "wcompiler"
	kind "StaticLib"
	buildoptions (ccflags)
	linkoptions (ldflags)
	defines {"WORKBENCH"}
	files {"bench/*.c"}
		-- The compiler library location is hardcoded in some other scripts...
	targetdir "bench"

project "mtcompiler"
	kind "StaticLib"
	buildoptions (mtccflags)
	linkoptions (mtldflags)
	files {"bench/*.c"}
		-- The compiler library location is hardcoded in some other scripts...
	targetdir "bench"

project "mtwcompiler"
	kind "StaticLib"
	buildoptions (mtccflags)
	linkoptions (mtldflags)
	defines {"WORKBENCH"}
	files {"bench/*.c"}
		-- The compiler library location is hardcoded in some other scripts...
	targetdir "bench"
