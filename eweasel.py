import os
import platform
import multiprocessing
import shutil

import boolean
import elocation
import esvn
import ecompile
import eutils
from elogger import SystemLogger

d_eweasel_svn = "https://svn.eiffel.com/eiffelstudio/trunk/eweasel"

def update():
	esvn.update_repository (d_eweasel_svn, elocation.eweasel())

def install():
	assert os.environ ['ISE_EIFFEL'] != None, 'ISE_EIFFEL is not set.'
	assert os.environ ['ISE_PLATFORM'] != None, 'ISE_PLATFORM is not set.'
	assert os.environ ['ISE_LIBRARY'] != None, 'ISE_LIBRARY is no set.'
	assert os.environ ['EWEASEL'] != None, 'EWEASEL is not set.'
	
	update ()
	
	l_path = os.path.expandvars (os.path.join ("$EWEASEL", "source", "eweasel.ecf"))
	l_project = ecompile.EiffelProject (l_path, 'eweasel_mt', 'eweasel-mt')
	if l_project.finalize():
		l_target_dir = os.path.expandvars (os.path.join ("$EWEASEL", "spec", "$ISE_PLATFORM", "bin"))
		if not os.path.exists (l_target_dir):
			os.makedirs (l_target_dir)
		elocation.copy (l_project.last_result(), l_target_dir)
		l_project.clean()
		SystemLogger.success ("Eweasel installation successful.")
		SystemLogger.warning ("Make sure that $EWEASEL/spec/$ISE_PLATFORM/bin is in your PATH variable!")
	else:
		SystemLogger.error ("Installation of eweasel failed.")
	# TODO on Windows (see install_eweasel.bat): Convert a few test files to DOS format


def precompile (target):
	if target == "all" or target == None:
		precompile ("base")
		precompile ("base-safe")
		precompile ("base-mt")
		precompile ("base-scoop-safe")
	else:
		if target == "bss": # Shortcut for base-scoop-safe
			target = "base-scoop-safe"
		l_path = os.path.expandvars (os.path.join ("$ISE_EIFFEL", "precomp", "spec", "$ISE_PLATFORM", target + ".ecf"))
		l_project = ecompile.EiffelProject (l_path, target, "driver")
		if l_project.precompile():
			SystemLogger.success ("Precompilation of " + target + " successful.")
		else:
			SystemLogger.error ("Precompilation of " + target + " failed.")

def _set_eweasel_env():
	l_eweasel = os.environ ['EWEASEL']
	
	l_command = [os.path.expandvars (os.path.join (l_eweasel, "spec", "$ISE_PLATFORM", "bin", ecompile._append_exe ("eweasel-mt")))]
	l_command = l_command + ['-max_threads', str(multiprocessing.cpu_count())]
	l_command = l_command + ['-define', 'EWEASEL', l_eweasel]
	l_command = l_command + ['-define', 'INCLUDE', os.path.join (l_eweasel, 'control')]
	l_command = l_command + ['-define', 'ISE_EIFFEL', os.environ ['ISE_EIFFEL']]
	l_command = l_command + ['-define', 'ISE_PLATFORM', os.environ ['ISE_PLATFORM']]
	l_command = l_command + ['-define', 'ISE_LIBRARY', os.environ ['ISE_LIBRARY']]
	if platform.system() == 'Windows':
		l_platform = 'WINDOWS'
		if os.environ ['ISE_PLATFORM'] == 'dotnet':
			l_platform = 'DOTNET'
		
		l_command = l_command + ['-define', l_platform, '1']
		l_command = l_command + ['-define', 'PLATFORM_TYPE', l_platform]
	else:
		l_command = l_command + ['-define', 'UNIX', '1']
		l_command = l_command + ['-define', 'PLATFORM_TYPE', 'unix']
	l_command = l_command + ['-init', os.path.join (l_eweasel, 'control', 'init')]
	l_command = l_command + ['-output', elocation.eweasel_build()]
	return l_command

def _prepare_catalog (catalog):
	if catalog == None:
		catalog = os.path.join (elocation.eweasel(), "control", "catalog")
	catalog = os.path.expandvars (catalog)
	if not os.path.exists (catalog):
		catalog = os.path.join (elocation.build(), catalog + '.eweasel_catalog')

	return os.path.realpath (catalog)

def _invoke_eweasel (command, catalog, keep_all):
	if not os.path.exists (elocation.eweasel_build()):
		os.makedirs (elocation.eweasel_build())
	
	# TODO: Move this to the appropriate location.
	os.environ ['ISE_PRECOMP'] = os.path.expandvars (os.path.join ('$ISE_EIFFEL', 'precomp', 'spec', '$ISE_PLATFORM'))
	os.environ ['ISE_LANG'] = 'en_US'
	
	if keep_all:
		command = command + ['-keep', 'all']
	else:
		command = command + ['-keep', 'failed']
	command = command + ['-catalog', catalog]
	
	# On Windows we have to modify the config.eif script. 
	# TODO: This also needs to happen for precompiles...
	if platform.system() == 'Windows':
		l_path = os.path.expandvars (os.path.join ('$ISE_EIFFEL', 'studio', 'config', '$ISE_PLATFORM', 'msc'))
		l_config = os.path.join (l_path, 'config.eif')
		l_backup = os.path.join (l_path, 'config.eif.orig')
		
		shutil.copyfile (l_config, l_backup)
		
		with open (l_backup, 'r') as source:
			with open (l_config, 'w') as target:
				for line in source:
					target.write (line.replace ('-SUBSYSTEM:WINDOWS', '-SUBSYSTEM:CONSOLE'))
		
		eutils.execute_with_output (command)
		shutil.copyfile (l_backup, l_config)
	else:
		eutils.execute_with_output (command)

def generate (a_filter, name='autogen'):
	l_parser = boolean.Parser (a_filter)
	l_filter = l_parser.parse()
	l_target_path = os.path.join (elocation.build(), name + '.eweasel_catalog')
	SystemLogger.info ("Creating catalog " + l_target_path + " with filter: " + l_filter.to_string())
	with open (_prepare_catalog(None), 'r') as source:
		with open (l_target_path, 'w') as target:
			target.write ('source_path $BUGS\n')
			for line in source:
				if l_filter.evaluate (line):
					print (line.rstrip())
					target.write (line)

def run_all (keep_all=False):
	SystemLogger.info ("Running the full eweasel test suite.")
	_invoke_eweasel (_set_eweasel_env(), _prepare_catalog (None), keep_all)

def catalog (catalog, keep_all):
	if catalog == None:
		catalog = 'autogen'
	l_command = _set_eweasel_env ()
	l_catalog = _prepare_catalog (catalog)
	assert os.path.exists (l_catalog), "Catalog does not exist."
	SystemLogger.info ("Running Eweasel on catalog: " + l_catalog)
	_invoke_eweasel (l_command, l_catalog, keep_all)


import eve
import sys

# Make input a synonym of raw_input in Python 2
try:
   input = raw_input
except NameError:
   pass

def set_environment():
	if not eve.check_environment_variables():
		eve.update_environment_variables()

def main(args):
	mode = 'default'
	argument = None
	keep = False
	
	if (len(args) > 1):
		mode = args[1]
	if (len(args) > 2):
		argument = args[2]

	if mode == 'default':
		print('usage:\n'
			'  eweasel.py update                          --- Update the source code of eweasel. \n'
			'  eweasel.py install                         --- Compile the eweasel binary and set everything up.\n'
			'  eweasel.py precompile [library]            --- Precompile the specified library, or all libraries if argument omitted.\n'
			'  eweasel.py run [--keep] filter...          --- Run the tests with the specified filter. If --keep is present, also keeps passing tests.\n'
			'  eweasel.py catalog [--keep] [catalog_name] --- Run eweasel with the specified catalog..\n'
			'                                             --- If the catalog is in the BUILD directory and has the extension .eweasel_catalog,\n'
			'                                             --- the full path and file name extension can be omitted.\n'
			'                                             --- If no catalog is specified, it will default to "autogen.eweasel_catalog" in the BUILD directory.\n'
			'  eweasel.py generate catalog_name filter... --- Create a catalog with name catalog_name for the specified filter.\n'
			'                                             --- The catalog will be stored in the BUILD directory with the extension .eweasel_catalog.\n')
		
	elif mode == 'update':
		update()
	elif mode == 'install':
		set_environment()
		install()
	elif mode == 'precompile':
		set_environment()
		precompile (argument)
	elif mode == 'catalog':
		if argument == '--keep':
			keep = True
			argument = None
			if len (args) > 3:
				argument = args [3]
		set_environment()
		catalog (argument, keep)
	elif mode == 'run':
		set_environment()
		if argument == '--keep':
			keep = True
			generate (' '.join(args[3:]), 'autogen')
		else:
			generate (' '.join(args[2:]), 'autogen')
		catalog ('autogen', keep)
	elif mode == 'generate':
		assert argument != None, "Must provide argument"
		generate (' '.join(sys.argv[3:]), argument)
	else:
		SystemLogger.error("invalid option " + mode)
	return

if __name__ == "__main__":
	try:
		main(sys.argv)
	except Exception as e:
		import traceback
		traceback.print_exc()
		input()
