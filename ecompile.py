import glob
import os
import os.path
import platform
import shutil

import elocation
import eutils
from elogger import SystemLogger

############## Platform specifics #####################

d_target_directory_raw = os.path.expandvars (os.path.join ("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM"))
d_target_includedir_raw = os.path.join (d_target_directory_raw, "include")
d_target_libdir_raw = None
d_compile_command = None
d_platform_libs = None
d_windows_runtime_flag = None

if platform.system() == 'Windows':
	d_target_libdir_raw = os.path.expandvars (os.path.join (d_target_directory_raw, "lib", "$ISE_C_COMPILER"))
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
	d_target_libdir_raw = os.path.join (d_target_directory_raw, "lib")
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

def copy_files(src_glob_raw, destination_folder_raw):
	SystemLogger.info("copying files from " + src_glob_raw + " to " + destination_folder_raw)
	expanded_folder = os.path.expandvars (destination_folder_raw)
	for fname in glob.iglob(os.path.expandvars (src_glob_raw)):
		dst_file = os.path.join(expanded_folder, os.path.basename(fname))
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

		copy_files (os.path.join (sourcedir, "config.sh"), d_target_includedir_raw)

		# Copy public header files and all run-times.
	copy_files (os.path.join (sourcedir, "run-time", "*.h"), d_target_includedir_raw)
	copy_files (os.path.join (builddir, "spec", "lib", "*.*"), d_target_libdir_raw)
	

		# Compile the various C support libraries needed by Eiffel libraries.
	compile_libraries (d_platform_libs)
	compile_libraries (d_shared_libs)


def to_platform_exe (name):
	if platform.system() == 'Windows':
		name = name + '.exe'
	return name

def compile_eiffel (ecf_path, target, binary_name, finalize=False):
	result = False
	SystemLogger.info("Compiling Eiffel program")
	ec_path = os.path.expandvars (os.path.join ("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "bin", to_platform_exe('ec')))
	ecf_path = os.path.expandvars (ecf_path)
	project_path = os.path.dirname (ecf_path)
	
	SystemLogger.info("EiffelStudio: " + ec_path)
	SystemLogger.info("ECF: " + ecf_path)
	SystemLogger.info("Target: " + target)
	SystemLogger.info("ISE_EIFFEL: " + os.environ['ISE_EIFFEL'])
	SystemLogger.info("ISE_LIBRARY: " + os.environ['ISE_LIBRARY'])
	SystemLogger.info("EIFFEL_SRC: " + os.environ['EIFFEL_SRC'])
	SystemLogger.info("Finalize: " + str(finalize))
	
	if os.path.isfile (ecf_path):
		elocation.delete(os.path.join (project_path, "EIFGENs", target))
		command = [ec_path, '-config', ecf_path, '-target', target, '-batch', '-c_compile']
		if finalize:
			command = command + ['-finalize']
		
		code = eutils.execute (command, SystemLogger.get_file(), project_path)
		
		code_folder = 'W_code'
		if finalize:
			code_folder = 'F_code'
		generated_binary = os.path.join (project_path, 'EIFGENs', target, code_folder, to_platform_exe (binary_name))
		
		if code == 0 and os.path.isfile (generated_binary):
			SystemLogger.success ("Compilation of Eiffel project " + ecf_path + " (" + target + ") successful.")
			result = True
		else:
			SystemLogger.error ("Compilation of Eiffel project " + ecf_path + " (" + target + ") failed.")
	else:
		SystemLogger.error("ECF file '" + ecf_path + "' does not exist")
	return result
