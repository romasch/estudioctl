import glob
import os
import os.path
import platform
import shutil

import elocation
import eutils
from elogger import SystemLogger

# Hide some platform specific issues.
d_target_directory = os.path.expandvars (os.path.join ("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM"))
d_target_includedir = os.path.join (d_target_directory, "include")
d_target_libdir = None
d_compile_command = None
d_platform_libs = None


if platform.system() == 'Windows':
	d_target_libdir = os.path.expandvars (os.path.join (d_target_directory, "lib", "$ISE_C_COMPILER"))
	d_compile_command = ["compile_library.bat"]
	d_platform_libs = [
		{'cwd': os.path.join("$EIFFEL_SRC", "library", "wel", "Clib"),
			'cmd': d_compile_command},
		{'cwd': os.path.join("$EIFFEL_SRC", "library", "web_browser", "Clib"),
			'cmd': d_compile_command},
		{'cwd': os.path.join("$EIFFEL_SRC", "framework", "cli_writer", "Clib"),
			'cmd': d_compile_command},
		{'cwd': os.path.join("$EIFFEL_SRC", "framework", "cli_debugger", "Clib"),
			'cmd': d_compile_command},
		{'cwd': os.path.join("$EIFFEL_SRC", "C_library", "zlib"),
			'cmd': d_compile_command},
		{'cwd': os.path.join("$EIFFEL_SRC", "C_library", "libpng"),
			'cmd': d_compile_command}]
else:
	d_target_libdir = os.path.join (d_target_directory, "lib")
	d_compile_command = ["finish_freezing", "-library"]
	d_platform_libs =  [
		{'cwd': os.path.join("$EIFFEL_SRC", "library", "vision2", "implementation", "gtk", "Clib"),
		 'cmd': d_compile_command}]

d_shared_libs = [
	{'cwd': os.path.join("$EIFFEL_SRC", "library", "net", "Clib"),
	 'cmd': d_compile_command},
	{'cwd': os.path.join("$EIFFEL_SRC", "library", "cURL", "Clib"),
	 'cmd': d_compile_command},
#	{'cwd': os.path.join("$EIFFEL_SRC", "library", "mysql", "Clib"),
#	 'cmd': d_compile_command},
#	{'cwd': os.path.join("$EIFFEL_SRC", "framework", "auto_test", "Clib"),
#	 'cmd': d_compile_command},
	{'cwd': os.path.join("$EIFFEL_SRC", "library", "vision2", "Clib"),
	 'cmd': d_compile_command}]


def copy_files(src_glob, dst_folder):
	SystemLogger.info("copying files from " + src_glob + " to " + dst_folder)
	for fname in glob.iglob(src_glob):
		dst_file = os.path.join(dst_folder, os.path.basename(fname))
		SystemLogger.debug ("copying file from " + fname + " to " + dst_file)
		shutil.copy(fname, dst_file)

def execute_calls(calls):
	for c in calls:
		eutils.execute(c["cmd"], SystemLogger.get_file(), os.path.expandvars(c["cwd"]))

def compile_runtime():
	builddir = os.path.join (elocation.build(), "runtime")
	sourcedir = os.path.join (elocation.trunk_source(), "C")
	scriptdir = os.path.join (elocation.base_directory(),  "scripts")
	nightlytargetdir = os.path.expandvars (os.path.join ("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM"))
	
	copy_files (os.path.join (scriptdir, "premake4.lua"), sourcedir)
	
	if platform.system() == 'Windows':
		# Shell and Nmake based build system:
		#calls = [
			#{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 #'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "Configure.bat")), "clean"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 #'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "Configure.bat")), d_runtime_flag, "m"]},
		#]
		#execute_calls(calls)
		
		# Premake based build system:
		print ("Not yet implemented")
	else:
		# Shell and make based build system:
		# TODO: This is currently broken because the libraries are generated at a wrong place.
		#build_calls = [
			#{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 #'cmd': ["make", "clobber"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 #'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "quick_configure"))]},
		#]
		
		# Premake based build system:
		# TODO: Don't call init_calls for incremental compilation.
		# TODO: Maybe add a "make clean" call in the build directory, if it exists.
		init_calls = [
			{'cwd': scriptdir,
			 'cmd': ["./runtime.unix.sh"]},
			{'cwd': sourcedir,
			 'cmd': ["premake4", "gmake"]}]
		execute_calls (init_calls)
		
		build_calls = [
			{'cwd': builddir,
			 'cmd': ["make"]}]
			 
		execute_calls (build_calls)
		copy_files (os.path.join (sourcedir, "config.sh"), d_target_includedir)

		# Copy public header files and all run-times.
	copy_files (os.path.expandvars (os.path.join (sourcedir, "run-time", "*.h")), d_target_includedir)
	copy_files (os.path.expandvars (os.path.join (builddir, "spec", "lib", "*.*")), d_target_libdir)
	

		# Compile the various C support libraries needed by Eiffel libraries.
	execute_calls (d_platform_libs)
	execute_calls (d_shared_libs)
