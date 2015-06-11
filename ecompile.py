import glob
import os
import os.path
import platform
import shutil

import elocation
import eutils
from elogger import SystemLogger

############## Platform specifics #####################

d_target_directory = os.path.expandvars (os.path.join ("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM"))
d_target_includedir = os.path.join (d_target_directory, "include")
d_target_libdir = None
d_compile_command = None
d_platform_libs = None
d_windows_runtime_flag = None

if platform.system() == 'Windows':
	d_target_libdir = os.path.expandvars (os.path.join (d_target_directory, "lib", "$ISE_C_COMPILER"))
	d_compile_command = ["compile_library.bat"]
	d_platform_libs = [
		os.path.join("$EIFFEL_SRC", "library", "wel", "Clib"),
		os.path.join("$EIFFEL_SRC", "library", "web_browser", "Clib"),
		os.path.join("$EIFFEL_SRC", "framework", "cli_writer", "Clib"),
		os.path.join("$EIFFEL_SRC", "framework", "cli_debugger", "Clib"),
		os.path.join("$EIFFEL_SRC", "C_library", "zlib"),
		os.path.join("$EIFFEL_SRC", "C_library", "libpng")]
	if 'PROGRAMFILES(X86)' in os.environ:
		d_windows_runtime_flag = 'win64'
	else:
		d_windows_runtime_flag = 'win32'
else:
	d_target_libdir = os.path.join (d_target_directory, "lib")
	d_compile_command = ["finish_freezing", "-library"]
	d_platform_libs =  [os.path.join("$EIFFEL_SRC", "library", "vision2", "implementation", "gtk", "Clib")]

d_shared_libs = [
	os.path.join("$EIFFEL_SRC", "library", "net", "Clib"),
	os.path.join("$EIFFEL_SRC", "library", "cURL", "Clib"),
	os.path.join("$EIFFEL_SRC", "library", "vision2", "Clib")]

	# Shared Libraries used for EVE only.
d_eve_shared_libs = [
	os.path.join("$EIFFEL_SRC", "library", "mysql", "Clib"),
	os.path.join("$EIFFEL_SRC", "framework", "auto_test", "Clib")]


################# Helper functions #####################

def copy_files(src_glob, dst_folder):
	SystemLogger.info("copying files from " + src_glob + " to " + dst_folder)
	for fname in glob.iglob(src_glob):
		dst_file = os.path.join(dst_folder, os.path.basename(fname))
		SystemLogger.debug ("copying file from " + fname + " to " + dst_file)
		shutil.copy(fname, dst_file)

def run_command (command, directory):
	eutils.execute (command, SystemLogger.get_file(), os.path.expandvars (directory))

def compile_libraries (libs):
	for lib in libs:
		run_command (d_compile_command, lib)

################# Runtime compilation ##################

def compile_runtime():
	builddir = os.path.join (elocation.build(), "runtime")
	sourcedir = os.path.join (elocation.trunk_source(), "C")
	scriptdir = os.path.join (elocation.base_directory(),  "scripts")
	nightlytargetdir = os.path.expandvars (os.path.join ("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM"))
	
	copy_files (os.path.join (scriptdir, "premake4.lua"), sourcedir)
	
	if platform.system() == 'Windows':
		# Shell and Nmake based build system:
		# run_command ([os.path.join(sourcedir, "Configure.bat"), "clean"], sourcedir)
		# run_command ([os.path.join(sourcedir, "Configure.bat"), d_windows_runtime_flag, 'm'], sourcedir)
		
		# Premake based build system:

		print ("Not yet implemented")
	else:
		# Shell and make based build system:
		# TODO: This is currently broken because the libraries are generated at a wrong place.
#		run_command (["make", "clobber"], sourcedir)
#		run_command (["./quick_configure"], sourcedir)
		
		# Premake based build system:
		# TODO: Don't call the first three commands for incremental compilation.
		if os.path.exists (os.path.join (builddir, "Makefile")):
			run_command (["make", "clean"], builddir)
		run_command (["./runtime.unix.sh"], scriptdir)
		run_command (["premake4", "gmake"], sourcedir)
		run_command (["make"], builddir)

		copy_files (os.path.join (sourcedir, "config.sh"), d_target_includedir)

		# Copy public header files and all run-times.
	copy_files (os.path.expandvars (os.path.join (sourcedir, "run-time", "*.h")), d_target_includedir)
	copy_files (os.path.expandvars (os.path.join (builddir, "spec", "lib", "*.*")), d_target_libdir)
	

		# Compile the various C support libraries needed by Eiffel libraries.
	compile_libraries (d_platform_libs)
	compile_libraries (d_shared_libs)
