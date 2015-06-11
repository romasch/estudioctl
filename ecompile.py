import glob
import os
import os.path
import platform
import shutil

import elocation
import eutils
from elogger import SystemLogger

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
	
	copy_files (os.path.join (scriptdir, "premake4.lua"), sourcedir)
	
	if platform.system() == 'Windows':
		print ("Not yet implemented")
	else:
		init_calls = [
			{'cwd': scriptdir,
			 'cmd': ["./runtime.unix.sh"]},
			{'cwd': sourcedir,
			 'cmd': ["premake4", "gmake"]}]
		execute_calls (init_calls)
		
		calls = [
			{'cwd': builddir,
			 'cmd': ["make"]}]
	
		execute_calls (calls)



#def compile_runtime():
	#global d_compile_runtime_script, d_copy_runtime_script
	#SystemLogger.info("Compiling runtime\nLocation: " + os.path.join("EIFFEL_SRC", "C"))
	#if platform.system() == 'Windows':
		#calls = [
			#{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 #'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "Configure.bat")), "clean"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 #'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "Configure.bat")), d_runtime_flag, "m"]},
		#]
		#execute_calls(calls)
		#copy_files(
			#os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "*.h")),
			#os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "include")))
		#copy_files(
			#os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "LIB", "*.*")),
			#os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "lib", "$ISE_C_COMPILER")))
		#calls = [
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "net", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "wel", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "cURL", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "mysql", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "vision2", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "web_browser", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "framework", "cli_writer", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "framework", "cli_debugger", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "framework", "auto_test", "Clib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "C_library", "zlib"),
			 #'cmd': ["compile_library.bat"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "C_library", "libpng"),
			 #'cmd': ["compile_library.bat"]},
		#]
		#execute_calls(calls)
	#else:
		#calls = [
			#{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 #'cmd': ["make", "clobber"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 #'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "quick_configure"))]},
		#]
		#execute_calls(calls)
		#copy_files(
			#os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "*.h")),
			#os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "include")))
		#copy_files(
			#os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "config.sh")),
			#os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "include")))
		#copy_files(
			#os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "*.a")),
			#os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "lib")))
		#copy_files(
			#os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "*.so")),
			#os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "lib")))
		#calls = [
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "net", "Clib"),
			 #'cmd': ["finish_freezing", "-library"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "vision2", "implementation", "gtk", "Clib"),
			 #'cmd': ["finish_freezing", "-library"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "cURL", "Clib"),
			 #'cmd': ["finish_freezing", "-library"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "mysql", "Clib"),
			 #'cmd': ["finish_freezing", "-library"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "library", "vision2", "Clib"),
			 #'cmd': ["finish_freezing", "-library"]},
			#{'cwd': os.path.join("$EIFFEL_SRC", "framework", "auto_test", "Clib"),
			 #'cmd': ["finish_freezing", "-library"]},
		#]
		#execute_calls(calls) 
