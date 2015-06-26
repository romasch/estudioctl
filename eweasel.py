import os
import elocation
import esvn
import ecompile
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

	