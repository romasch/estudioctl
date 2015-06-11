import config
import os
import os.path
import shutil

from elogger import SystemLogger


def base_directory ():
	"""The root directory to which all files are relative to."""
	if config.v_base_directory_override != None:
		return os.path.realpath (v_estuidoctl_base_default)
	elif (config.v_base_directory_environment_variable != None and config.v_base_directory_environment_variable in os.environ):
		return os.path.realpath (os.path.expandvars (os.environ ["ESTUDIOCTL"]))
	else:
		return os.path.realpath ("../")


def trunk_source ():
	""" The directory containing the source code of trunk."""
	return os.path.join (base_directory(), config.v_dir_trunk_source)


def eve_source ():
	""" The directory containing the source code of EVE."""
	return os.path.join (base_directory(), config.v_dir_eve_source)

def eweasel():
	""" The directory containing eweasel test cases."""
	return os.path.join (base_directory(), config.v_dir_eweasel)

def nightly():
	return os.path.join (base_directory(), config.v_dir_nightly)

def build():
	return os.path.join (base_directory(), config.v_dir_build)

def eweasel_build():
	return os.path.join (base_directory(), config.v_dir_build_eweasel)

def move (source, target):
	""" 
	Move the file or folder at 'source' to 'target'. Target should not exist.
	Argument source: Unicode string.
	Argument target: Unicode string.
	"""
	SystemLogger.debug("Moving file(s) from " + source + " to " + target)
	if not os.path.exists(source):
		SystemLogger.error("Cannot move '" + source + "' to '" + target + "'. Source file does not exist")
	elif os.path.exists(target):
		SystemLogger.error("Cannot move '" + source + "' to '" + target + "'. Target already exists")
	else:
		os.rename(source, target)
	return

def copy (source, target):
	""" 
	Move the file or folder at 'source' to 'target'. Target should not exist.
	Argument source: Unicode string.
	Argument target: Unicode string.
	Result: Boolean value. True on success.
	"""
	SystemLogger.debug("Copying file(s) from " + source + " to " + target)
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
	SystemLogger.debug("Deleting location at path: " + path)
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
