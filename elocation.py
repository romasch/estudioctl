import config
import os
import os.path


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


print (base_directory())
print (trunk_source())
print (eve_source())
print (eweasel())
print (nightly())
print (build())
print (eweasel_build())