from elogger import SystemLogger
import os
import os.path
import platform
import shutil

def extract (a_file):
	""" Extract a_file to the current directory. """
	""" Argument a_file: Unicode string. """
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
	""" Compress the file or directory at path """
	""" Argument path: Unicode string. """
	""" Argument basename: Name of the archive to be generated. Unicode string, can be None. """
	""" Result: Path to the compressed file. Unicode string."""
	SystemLogger.debug("Compressing path")
	SystemLogger.debug("Path: " + path)
	result = None
	if basename == None:
		basename = os.path.basename(path)
	if platform.system() == 'Windows':
		output_file = os.path.join('.', basename + '.' + d_archive_extension)
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
		output_file = os.path.realpath(os.path.join('.', basename + '.' + d_archive_extension))
		workingdir, compressdir = os.path.split(path)
		if execute(['tar', '-C', workingdir, '-cjf', output_file, compressdir], SystemLogger.get_file()) == 0:
			SystemLogger.debug("Compression complete")
			result = output_file
		else:
			SystemLogger.error("Compression of '" + path + "' failed")
	return result

def move (source, target):
	""" Move the file or folder at 'source' to 'target'. Target should not exist. """
	""" Argument source: Unicode string. """
	""" Argument target: Unicode string. """
	SystemLogger.debug("Moving path")
	SystemLogger.debug("Source: " + source)
	SystemLogger.debug("Target: " + target)
	if not os.path.exists(source):
		SystemLogger.error("Cannot move '" + source + "' to '" + target + "'. Source file does not exist")
	elif os.path.exists(target):
		SystemLogger.error("Cannot move '" + source + "' to '" + target + "'. Target already exists")
	else:
		os.rename(source, target)
	return

def copy (source, target):
	""" Move the file or folder at 'source' to 'target'. Target should not exist. """
	""" Argument source: Unicode string. """
	""" Argument target: Unicode string. """
	""" Result: Boolean value. True on success."""
	SystemLogger.debug("Copying path")
	SystemLogger.debug("Source: " + source)
	SystemLogger.debug("Target: " + target)
	result = False
	if not os.path.exists(source):
		SystemLogger.error("Cannot copy '" + source + "' to '" + target + "'. Source does not exist")
	else:
		if os.path.isfile(source):
			shutil.copy(source, target)
			result = True
		elif os.path.exists(target):
			SystemLogger.error("Cannot copy directory '" + source + "' to '" + target + "'. Target already exists")
		else:
			shutil.copytree(source, target)
			result = True
	return result

def delete (path):
	""" Recursively delete the file or folder at path. """
	""" Argument path: Unicode string. """
	""" Result: Boolean value. True on success."""
	SystemLogger.debug("Deleting path")
	SystemLogger.debug("Path: " + path)
	result = False
	if os.path.isdir(path):
		shutil.rmtree(path, ignore_errors=False, onerror=_handleRemoveReadonly)
	elif os.path.isfile(path):
		os.remove(path)
	if os.path.exists(path):
		SystemLogger.error("Unable to delete '" + path + "'")
	else:
		result = True
	return result

def _handleRemoveReadonly(func, path, exc):
	import stat
	excvalue = exc[1]
	if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
		os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
		func(path)
	else:
		raise 


move ("eve", "eve2")
copy ("eve2", "eve3")
l_compressed = compress ("eve3", "blub")
