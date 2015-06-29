import os
import platform
import multiprocessing


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


def precompile (target = "all"):
	if target == "all":
		precompile ("base")
		precompile ("base-safe")
		precompile ("base-mt")
		precompile ("base-scoop-safe")
	else:
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

def _prepare_catalog (catalog=None):
	if catalog == None:
		catalog = os.path.join ("$EWEASEL", "control", "catalog")
	catalog = os.path.realpath (os.path.expandvars (catalog))
	return catalog

def _invoke_eweasel (command, catalog, keep_all):
	if not os.path.exists (elocation.eweasel_build()):
		os.makedirs (elocation.eweasel_build())
	
	# TODO: Move this to the appropriate location.
	os.environ ['ISE_PRECOMP'] = os.path.expandvars (os.path.join ('$ISE_EIFFEL', 'precomp', 'spec', '$ISE_PLATFORM'))
	
	# TODO: On Windows we have to modify the config.eif script.

	if keep_all:
		command = command + ['-keep', 'all']
	else:
		command = command + ['-keep', 'failed']
	command = command + ['-catalog', catalog]
	eutils.execute_with_output (command)


def catalog (catalog=None, keep_all=False):
	l_command = _set_eweasel_env ()
	l_catalog = _prepare_catalog (catalog)
	SystemLogger.info ("Running Eweasel on catalog: " + l_catalog)
	_invoke_eweasel (l_command, l_catalog, keep_all)
	

def only (test):
	l_command = _set_eweasel_env()
	l_command = l_command + ['-filter', 'dir ' + test]
	_invoke_eweasel (l_command, _prepare_catalog (None), True)
	
	
