"""
Uitlity functions.

"""

from elogger import SystemLogger
import config

import os
import os.path
import platform
import subprocess
import sys
v_encoding = sys.stdout.encoding

def execute(program, output_file = None, execution_directory = None):
	"""
		Execute 'program'.
	"""
	SystemLogger.info("Executing " + ' '.join(program))
	if isinstance(output_file, str):
		pipe = open(output_file, 'a')
	else:
		pipe = output_file
	if execution_directory is None:
		proc = subprocess.Popen(program, stdin=pipe, stdout=pipe, stderr=pipe)
	else:
		proc = subprocess.Popen(program, cwd=execution_directory, stdin=pipe, stdout=pipe, stderr=pipe)
	proc.communicate()
	if isinstance(output_file, str):
		pipe.close()
	SystemLogger.info("Finished with code " + str(proc.returncode))
	return proc.returncode

def execute_with_output (program, execution_directory = None):
	SystemLogger.info ("Executing " + ' '.join (program))
	if execution_directory is None:
		proc = subprocess.Popen(program, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for line in proc.stdout:
			SystemLogger.info (line.decode (v_encoding).rstrip())
	SystemLogger.info("Finished with code " + str(proc.returncode))
	return proc.returncode

def extract (a_file):
	""" 
		Extract a_file to the current directory.
		Argument a_file: Unicode string.
	"""
	SystemLogger.debug("Extracting file")
	SystemLogger.debug("Path: " + a_file)
	if platform.system() == 'Windows':
		# TODO: get path from registry
		executable = os.path.join('C:\\', 'Program Files', '7-zip', '7z.exe')
		if os.path.isfile(executable):
			if execute([executable, 'x', a_file], SystemLogger.get_file()) == 0:
				SystemLogger.debug("Extraction complete")
			else:
				SystemLogger.error("Extraction of '" + a_file + "' failed")
		else:
			SystemLogger.error("Extraction of '" + a_file + "' failed. 7zip executable not found at " + executable)
	else:
		if execute(['tar', '-xjf', a_file], SystemLogger.get_file()) == 0:
			SystemLogger.debug("Extraction complete")
		else:
			SystemLogger.error("Extraction of '" + a_file + "' failed")

def compress (path, basename=None):
	""" 
		Compress the file or directory at path 
		Argument path: Unicode string. 
		Argument basename: Name of the archive to be generated. Unicode string, can be None.
		Result: Path to the compressed file. Unicode string.
	"""
	SystemLogger.debug("Compressing path")
	SystemLogger.debug("Path: " + path)
	result = None
	if basename == None:
		basename = os.path.basename(path)
	if platform.system() == 'Windows':
		output_file = os.path.join('.', basename + '.' + config.d_archive_extension)
		SystemLogger.debug("Destination: " + output_file)
		# TODO: get path from registry
		executable = os.path.join('C:\\', 'Program Files', '7-zip', '7z.exe')
		if os.path.isfile(executable):
			if execute([executable, 'a', output_file, path], SystemLogger.get_file()) == 0:
				SystemLogger.debug("Compression complete")
				result = output_file
			else:
				SystemLogger.error("Compression of '" + path + "' failed")
		else:
			SystemLogger.error("Comperssion of '" + path + "' failed. 7zip executable not found at " + executable)
	else:
		output_file = os.path.realpath(os.path.join('.', basename + '.' + config.d_archive_extension))
		workingdir, compressdir = os.path.split(path)
		if execute(['tar', '-C', workingdir, '-cjf', output_file, compressdir], SystemLogger.get_file()) == 0:
			SystemLogger.debug("Compression complete")
			result = output_file
		else:
			SystemLogger.error("Compression of '" + path + "' failed")
	return result
