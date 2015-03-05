# ============================================================================
# EVE main script
# ----------------------------------------------------------------------------
# default directory layout:
#   CWD/EiffelStudioXY_zzzz    location of EiffelStudio installation
#   CWD/eve                    location of EVE source checkout
#   CWD/delivery               location of generated EVE deliveries
#   CWD/merge                  location where merge is performed
# ----------------------------------------------------------------------------
# main commands:
#  //not yet implemented//- python eve.py
#      print status information and offer command selection
#  - python eve.py update
#      install or update to latest nightly build of EiffelStudio
#      checkout or update latest EVE source
#      checkout or update latest EVE scripts
#      compile EVE runtime
#      compile workbench verision of EVE bench target
#  - python eve.py delivery
#      create EVE delivery (no update performed)
#  - python eve.py merge
#      merge EiffelStudio Trunk into EVE source (uses clean repositories)
#      create EVE delivery
#  - python eve.py es
#      run EiffelStudio
# ----------------------------------------------------------------------------
# individual commands:
#  - python eve.py check
#      check installation and environment
#  - python eve.py update es
#      install or update to latest nightly build of EiffelStudio
#  - python eve.py update source
#      checkout or update latest EVE source
#  - python eve.py compile runtime
#      compile EVE runtime
#  - python eve.py compile eve
#      compile workbench version of EVE bench target
#  - python eve.py finalize eve
#      compile finalized version of EVE bench target
# ----------------------------------------------------------------------------
# dependencies:
#  - Python 2.7.x
#  - [choice] pysvn for corresponding python/svn versions (necessary for merge)
#  - [choice] SVN executable in path (if pysvn not available)
#  - [optional] colorama: http://pypi.python.org/pypi/colorama
#  - [Windows only] msc - Microsoft C compiler
#  - [Windows only] 7zip - installed at default location C:\Program Files\7-zip
# ============================================================================

# TODO
# http://www.tutorialspoint.com/python/python_gui_programming.htm

import config

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# SETUP VARIABLES
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# Base directory where EiffelStudio will be installed
# EiffelStudio will be installed in a subdirectory EiffelStudioXY_zzzzzz
v_dir_eiffelstudio_base = "."

# Set this to a string of a specific version of EiffelStudio that is already installed (i.e. "12345")
v_force_es_version = None

# Directory where EVE source will be checked out
v_dir_eve_source = "./eve"

# Directory where generated deliveries will be saved
v_dir_delivery = "./delivery"
v_dir_delivery_remote = r"\\fs.meyer.inf.ethz.ch\web\htdocs\research\eve\builds"
v_remote_base_url = r"http://se.inf.ethz.ch/research/eve/builds"

# Directory where Boogie/Z3 bundle is installed
v_dir_boogie = "./eve/Delivery/studio/tools/boogie"

# Directory where merge will be performed (checkout directory for eve)
v_dir_merge = "./merge_eve"

# Name of log file
v_log_filename = "./log.txt"

# URLs
v_url_svn_eve = "https://svn.eiffel.com/eiffelstudio/branches/eth/eve"
#v_url_svn_eve_src = "https://svn.eiffel.com/eiffelstudio/branches/eth/eve/Src"
v_url_svn_eve_src = config.v_url_svn_eve_src
#v_url_svn_trunk = "https://svn.eiffel.com/eiffelstudio/trunk"
v_url_svn_trunk = config.v_url_svn_trunk_src
v_url_eiffelstudio_download = ["ftp://ftp.eiffel.com/pub/beta/nightly", "ftp://ftp.eiffel.com/pub/beta/15.01/"]

v_svn_user = ""
v_svn_password = ""

v_email_merge_info = "" # email to merge-resposible
v_email_merge_update = "se-group@lists.inf.ethz.ch;meyer-group@googlegroups.com" # email to group

# 0: no output
# 1: error/warning/success output
# 2: info output
# 3: log output
v_verbose_level = 3

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import os
import os.path
import platform
import sys
import time
import shutil
import subprocess

try:
	import urllib.request as urllib2
except ImportError:
	import urllib2

import re
import errno
import glob

from elogger import SystemLogger
import esvn
import elocation
import eutils

# Make input a synonym of raw_input in Python 2
try:
   input = raw_input
except NameError:
   pass


# ----------------------------------------------------------------------------
# Gather system information
# ----------------------------------------------------------------------------

d_ise_platform = None
d_runtime_flag = None
d_ise_c_compiler = None
d_archive_extension = None
d_eve_exe_name = None
d_compile_runtime_script = None
d_copy_runtime_script = None

if platform.system() == 'Windows':
	if 'PROGRAMFILES(X86)' in os.environ:
		d_ise_platform = 'win64'
		d_runtime_flag = 'win64'
		d_compile_runtime_script = "compile_es/windows/compile_ec_win64.bat"
	else:
		d_ise_platform = 'windows'
		d_runtime_flag = 'win32'
		d_compile_runtime_script = "compile_es/windows/compile_ec_win32.bat"
	d_eve_exe_name = 'ec.exe'
	d_ise_c_compiler = 'msc'
	d_archive_extension = '7z'
	d_copy_runtime_script = "compile_es/windows/copy_run_time.bat"
elif platform.system() == 'Linux':
	if platform.architecture()[0] == '64bit':
		d_ise_platform = 'linux-x86-64'
		d_runtime_flag = 'linux-x86-64'
	else:
		d_ise_platform = 'linux-x86'
		d_runtime_flag = 'linux-x86'
	d_eve_exe_name = 'ec'
	d_ise_c_compiler = 'gcc'
	d_archive_extension = 'tar.bz2'
	d_compile_runtime_script = "compile_es/linux/compile_runtime.bat"
	d_copy_runtime_script = "compile_es/linux/copy_runtime.bat"
else:
	SystemLogger.error("Platform " + platform.system() + " not supported")
	sys.exit()

# ----------------------------------------------------------------------------
# helper functions: process
# ----------------------------------------------------------------------------

def execute(program, output_file = None, execution_directory = None):
	SystemLogger.debug("Executing " + ' '.join(program))
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
	SystemLogger.debug("Finished with code " + str(proc.returncode))
	return proc.returncode

# ----------------------------------------------------------------------------
# helper functions: files
# ----------------------------------------------------------------------------

def download_file(url, filename):
	SystemLogger.debug("Downloading file")
	SystemLogger.debug("URL: " + url)
	SystemLogger.debug("Path: " + filename)
	try:
		response = urllib2.urlopen(url)
		data = response.read()
		path = os.path.realpath(filename)
		with open(path, "wb") as file:
			file.write(data)
		SystemLogger.debug("Download complete")
	except URLError as e:
		path = None
		if hasattr(e, 'reason'):
			SystemLogger.error("Download of '" + url + "' failed. Reason: " + e.reason)
		elif hasattr(e, 'code'):
			SystemLogger.error("Download of '" + url + "' failed with HTTP error code " + str(e.code))
		else:
			raise e
	return path

def replace_in_file(path, search, replace):
	SystemLogger.debug("Replacing in file")
	SystemLogger.debug("Path: " + path)
	SystemLogger.debug("Search: " + search)
	SystemLogger.debug("Replace: " + replace)
	import fileinput
	for line in fileinput.FileInput(path, inplace=1):
		line = line.replace(search, replace)
		print (line),


# ----------------------------------------------------------------------------
# helper functions: email
# ----------------------------------------------------------------------------

import smtplib

try:
	from email.MIMEMultipart import MIMEMultipart
	from email.MIMEBase import MIMEBase
	from email.MIMEText import MIMEText
	from email import Encoders
except ImportError:
	from email.mime.multipart import MIMEMultipart
	from email.mime.base import MIMEBase
	from email.mime.text import MIMEText
	from email import encoders

def send_mail(to, subject, text, attach=None):
	"""Send email"""
	SystemLogger.info("Sending email '" + subject + "' to " + str(to))
	if to != None:
		email_user = "eve-noreply@se.inf.ethz.ch"
		msg = MIMEMultipart()
		msg['From'] = "EVE <" + email_user + ">"
		msg['To'] = to
		msg['Subject'] = subject
		msg.attach(MIMEText(text))
		if attach != None:
			part = MIMEBase('application', 'octet-stream')
			part.set_payload(open(attach, 'rb').read())
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attach))
			msg.attach(part)
		mailServer = smtplib.SMTP("smtp0.ethz.ch", 25, "localhost")
		mailServer.sendmail(email_user, to, msg.as_string())
		mailServer.quit()

# ----------------------------------------------------------------------------
# update EiffelStudio
# ----------------------------------------------------------------------------

def update_EiffelStudio():
	SystemLogger.info("Updating EiffelStudio")
	if v_force_es_version != None:
		SystemLogger.warning("Forcing EiffelStudio version " + v_force_es_version)
	name, filename, version, url = get_nightly_build(d_ise_platform, d_archive_extension)
	current_version, current_path = get_installed_version()
	if version > current_version or (v_force_es_version != None and current_version != v_force_es_version):
		target_file = os.path.join(v_dir_eiffelstudio_base, filename)
		download_file(url, target_file)
		eutils.extract(target_file)
		elocation.move(os.path.join(v_dir_eiffelstudio_base, name), os.path.join(v_dir_eiffelstudio_base, name + '_' + version))
		elocation.delete(target_file)
		update_environment_variables()
		current_version = version
		SystemLogger.success("EiffelStudio version " + version + " installed")
	else:
		update_environment_variables()
		SystemLogger.success("EiffelStudio is up-to-date at version " + current_version)
	return current_version

def get_nightly_build(platform, extension):
	expr = re.compile(r'.*((Eiffel_[\d.]+)_gpl_([\d]+)-([^.]+)\.([^\s]*)).*')
	name = None
	filename = None
	version = -1
	url = None
	for download_page in v_url_eiffelstudio_download:
		response = urllib2.urlopen(download_page)
		for line in response:
			m = expr.match(line)
			if m != None:
				if m.group(4) == platform and m.group(5) == extension and ((v_force_es_version == None and version < m.group(3)) or (v_force_es_version != None and v_force_es_version == m.group(3))):
					name = m.group(2)
					version = m.group(3)
					filename = m.group(1)
					url = download_page + '/' + filename
	return name, filename, version, url

def get_installed_version():
	files = os.listdir(v_dir_eiffelstudio_base)
	version = -1
	path = None
	for file in files:
		if os.path.isdir(file):
			expr = re.compile(r'Eiffel[\d.]+_([\d]+)')
			expr = re.compile(r'Eiffel_[\d.]+_([\d]+)')
			m = expr.match(file)
			if m != None and ((v_force_es_version == None and m.group(1) > version) or (v_force_es_version != None and m.group(1) == v_force_es_version)):
				version = m.group(1)
				path = os.path.realpath(os.path.join(v_dir_eiffelstudio_base, file))
	return version, path

# ----------------------------------------------------------------------------
# compile run-time
# ----------------------------------------------------------------------------

def copy_files(src_glob, dst_folder):
	SystemLogger.info("copying files from " + src_glob + " to " + dst_folder)
	for fname in glob.iglob(src_glob):
		dst_file = os.path.join(dst_folder, os.path.basename(fname))
		SystemLogger.debug ("copying file from " + fname + " to " + dst_file)
		shutil.copy(fname, dst_file)

def execute_calls(calls):
	for c in calls:
		execute(c["cmd"], SystemLogger.get_file(), os.path.expandvars(c["cwd"]))

def compile_runtime():
	global d_compile_runtime_script, d_copy_runtime_script
	SystemLogger.info("Compiling runtime\nLocation: " + os.path.join("EIFFEL_SRC", "C"))
	if platform.system() == 'Windows':
		calls = [
			{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "Configure.bat")), "clean"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "Configure.bat")), d_runtime_flag, "m"]},
		]
		execute_calls(calls)
		copy_files(
			os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "*.h")),
			os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "include")))
		copy_files(
			os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "LIB", "*.*")),
			os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "lib", "$ISE_C_COMPILER")))
		calls = [
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "net", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "wel", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "cURL", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "mysql", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "vision2", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "web_browser", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "framework", "cli_writer", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "framework", "cli_debugger", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "framework", "auto_test", "Clib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "C_library", "zlib"),
			 'cmd': ["compile_library.bat"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "C_library", "libpng"),
			 'cmd': ["compile_library.bat"]},
		]
		execute_calls(calls)
	else:
		calls = [
			{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 'cmd': ["make", "clobber"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "C"),
			 'cmd': [os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "quick_configure"))]},
		]
		execute_calls(calls)
		copy_files(
			os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "*.h")),
			os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "include")))
		copy_files(
			os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "config.sh")),
			os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "include")))
		copy_files(
			os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "*.a")),
			os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "lib")))
		copy_files(
			os.path.expandvars(os.path.join("$EIFFEL_SRC", "C", "run-time", "*.so")),
			os.path.expandvars(os.path.join("$ISE_EIFFEL", "studio", "spec", "$ISE_PLATFORM", "lib")))
		calls = [
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "net", "Clib"),
			 'cmd': ["finish_freezing", "-library"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "vision2", "implementation", "gtk", "Clib"),
			 'cmd': ["finish_freezing", "-library"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "cURL", "Clib"),
			 'cmd': ["finish_freezing", "-library"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "mysql", "Clib"),
			 'cmd': ["finish_freezing", "-library"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "library", "vision2", "Clib"),
			 'cmd': ["finish_freezing", "-library"]},
			{'cwd': os.path.join("$EIFFEL_SRC", "framework", "auto_test", "Clib"),
			 'cmd': ["finish_freezing", "-library"]},
		]
		execute_calls(calls)

def compile_eve(target):
	SystemLogger.info("Compiling EVE")
	ec_path = os.path.join(os.getenv("ISE_EIFFEL"), "studio", "spec", os.getenv("ISE_PLATFORM"), "bin", d_eve_exe_name)
	project_path = os.path.realpath(os.path.join(v_dir_eve_source, "Eiffel", "Ace"))
	ecf_path = os.path.join(project_path, "ec.ecf")
	SystemLogger.info("EiffelStudio: " + ec_path)
	SystemLogger.info("ECF: " + ecf_path)
	SystemLogger.info("Target: " + target)
	SystemLogger.info("ISE_EIFFEL: " + os.environ['ISE_EIFFEL'])
	SystemLogger.info("ISE_LIBRARY: " + os.environ['ISE_LIBRARY'])
	SystemLogger.info("EIFFEL_SRC: " + os.environ['EIFFEL_SRC'])
	if os.path.isfile(ecf_path):
		elocation.delete(os.path.join(project_path, "EIFGENs", target))
		olddir = os.getcwd()
		os.chdir(os.path.dirname(ecf_path))
		code = execute([ec_path, "-config", ecf_path, "-target", target, "-c_compile", "-batch"], SystemLogger.get_file())
		os.chdir(olddir)
		if code == 0 and is_eve_compilation_successful(target):
			SystemLogger.success("Compilation of EVE (" + target + ") successful")
		else:
			SystemLogger.error("Compilation of EVE (" + target + ") failed")
	else:
		SystemLogger.error("ECF file '" + ecf_path + "' does not exist")

def finalize_eve(target):
	SystemLogger.info("Finalizing EVE")
	ec_path = os.path.join(os.getenv("ISE_EIFFEL"), "studio", "spec", os.getenv("ISE_PLATFORM"), "bin", d_eve_exe_name)
	project_path = os.path.realpath(os.path.join(v_dir_eve_source, "Eiffel", "Ace"))
	ecf_path = os.path.join(project_path, "ec.ecf")
	SystemLogger.info("EiffelStudio: " + ec_path)
	SystemLogger.info("ECF: " + ecf_path)
	SystemLogger.info("Target: " + target)
	if os.path.isfile(ecf_path):
		elocation.delete(os.path.join(project_path, "EIFGENs"))
		olddir = os.getcwd()
		os.chdir(os.path.dirname(ecf_path))
		code = execute([ec_path, "-config", ecf_path, "-target", target, "-c_compile", "-finalize", "-batch"], SystemLogger.get_file())
		os.chdir(olddir)
		if code == 0 and is_eve_compilation_successful(target, True):
			SystemLogger.success("Finalization of EVE (" + target + ") successful")
		else:
			SystemLogger.error("Finalization of EVE (" + target + ") failed")
	else:
		SystemLogger.error("ECF file '" + ecf_path + "' does not exist")

def is_eve_compilation_successful(target, finalized = False):
	success = False
	compile_dir = "W_code"
	if finalized:
		compile_dir = "F_code"
	exe_path = os.path.realpath(os.path.join(v_dir_eve_source, "Eiffel", "Ace", "EIFGENs", target, compile_dir, d_eve_exe_name))
	if os.path.isfile(exe_path):
		if execute([exe_path, "-version"], subprocess.PIPE) == 0:
			success = True
	return success

# ----------------------------------------------------------------------------
# Delivery
# ----------------------------------------------------------------------------

def make_delivery():
	SystemLogger.info("Generating new delivery")

	eve_version = esvn.info_local_revision_number(v_dir_eve_source)
	delivery_name = 'eve_' + str(eve_version)
	delivery_path = os.path.realpath(os.path.join(v_dir_delivery, delivery_name))
	# generate finalized version
	check_environment_variables()
	compile_runtime()
	update_version_number()
	finalize_eve('bench')
	revert_version_number()
	# copy EiffelStudio to delivery destination (this copies the runtime)
	elocation.copy(os.getenv("ISE_EIFFEL"), delivery_path)
	# copy finalized eve to delivery destination
	eve_exe_source = os.path.join(v_dir_eve_source, 'Eiffel', 'Ace', 'EIFGENs', 'bench', 'F_code', d_eve_exe_name)
	eve_exe_target = os.path.join(delivery_path, 'studio', 'spec', os.getenv("ISE_PLATFORM"), 'bin', d_eve_exe_name)
	elocation.copy(eve_exe_source, eve_exe_target)
	# AutoProof: copy update to base library
	source = os.path.join(v_dir_eve_source, 'library', 'base', 'eve')
	target = os.path.join(delivery_path, 'library', 'base', 'eve')
	elocation.copy(source, target)
	source = os.path.join(v_dir_eve_source, 'library', 'base', 'base2')
	target = os.path.join(delivery_path, 'library', 'base', 'base2')
	elocation.copy(source, target)
	source = os.path.join(v_dir_eve_source, 'library', 'base', 'mml')
	target = os.path.join(delivery_path, 'library', 'base', 'mml')
	elocation.copy(source, target)
	source = os.path.join(v_dir_eve_source, 'library', 'base', 'base-eve.ecf')
	target = os.path.join(delivery_path, 'library', 'base', 'base-eve.ecf')
	elocation.copy(source, target)
	# AutoProof: copy ecf for precompile
	source = os.path.join(v_dir_eve_source, 'Delivery', 'precomp', 'spec', 'platform', 'base-eve.ecf')
	target = os.path.join(delivery_path, 'precomp', 'spec', os.getenv("ISE_PLATFORM"), 'base-eve.ecf')
	elocation.copy(source, target)
	# AutoProof: copy Boogie files
	source = os.path.join(v_dir_eve_source, 'Delivery', 'studio', 'tools', 'autoproof')
	target = os.path.join(delivery_path, 'studio', 'tools', 'autoproof')
	elocation.copy(source, target)
	# copy Boogie to delivery destination
	boogie_target = os.path.join(delivery_path, 'studio', 'tools', 'boogie')
	elocation.copy(v_dir_boogie, boogie_target)
	# copy libraries to delivery destination
	source = os.path.join(v_dir_eve_source, 'library', 'fixing')
	target = os.path.join(delivery_path, 'library', 'fixing')
	elocation.copy(source, target)
# TODO
	# copy install/run scripts to destination
	source = os.path.join(v_dir_eve_source, 'Delivery', 'run_eve.bat')
	target = os.path.join(delivery_path, 'run_eve.bat')
	elocation.copy(source, target)
	source = os.path.join(v_dir_eve_source, 'Delivery', 'run_eve.py')
	target = os.path.join(delivery_path, 'run_eve.py')
	elocation.copy(source, target)
	# generate zip archive
	archive_path = eutils.compress(delivery_path, delivery_name + "-" + d_ise_platform)
	delivery_file = os.path.join(v_dir_delivery, os.path.basename(archive_path))
	elocation.move(archive_path, delivery_file)
	# clean up
	elocation.delete(delivery_path)
	SystemLogger.success("Delivery " + delivery_name + " finished")
	# upload zip to server
	result = None
	if os.path.exists(v_dir_delivery_remote):
		remote_file = os.path.join(v_dir_delivery_remote, os.path.basename(delivery_file))
		elocation.copy(delivery_file, remote_file)
		SystemLogger.success("Delivery copied to remote location")
		result = v_remote_base_url + '/' + os.path.basename(delivery_file)
	else:
		if v_dir_delivery_remote != None:
			SystemLogger.error("Remote location (" + v_dir_delivery_remote + ") does not exist")
	return result
		
def update_version_number():
	file = os.path.join(v_dir_eve_source, 'framework', 'environment', 'interface', 'product_names.e')
	replace_in_file(file, 'EiffelStudio', 'EVE')
	file = os.path.join(v_dir_eve_source, 'Eiffel', 'API', 'constants', 'system_constants.e')
	replace_in_file(file, '0000', str(esvn.info_local_revision_number(v_dir_eve_source)))

def revert_version_number():
	file = os.path.join(v_dir_eve_source, 'framework', 'environment', 'interface', 'product_names.e')
	replace_in_file(file, 'EVE', 'EiffelStudio')
	file = os.path.join(v_dir_eve_source, 'Eiffel', 'API', 'constants', 'system_constants.e')
	replace_in_file(file, str(esvn.info_local_revision_number(v_dir_eve_source)), '0000')

# ----------------------------------------------------------------------------
# Merge
# ----------------------------------------------------------------------------

def make_merge():
	global v_dir_eve_source

	# set up parameters
	merge_path = os.path.realpath(v_dir_merge)
	v_dir_eve_source = os.path.join(merge_path, 'Src')
	os.environ['EIFFEL_SRC'] = v_dir_eve_source
	os.environ['ISE_LIBRARY'] = v_dir_eve_source

	# update dependencies
	update_EiffelStudio()

	# update repository
	try:
		elocation.delete(merge_path)
		esvn.update_repository(v_url_svn_eve, merge_path)
	except Exception as e1:
		SystemLogger.warning("Checkout failed. Trying one more time.")
		send_mail(v_email_merge_info, "[EVE] WARNING: checkout failed", "I will try again.")
		try:
			elocation.delete(merge_path)
			esvn.update_repository(v_url_svn_eve, merge_path)
		except Exception as e2:
			SystemLogger.error("Checkout failed, again...")
			send_mail(v_email_merge_info, "[EVE] ERROR: checkout failed again", "I give up...")
			sys.exit(0)

	# send email to block commits
	send_mail(v_email_merge_update, '[EVE] merge started', """Dear assistants,

The eve branch is being synchronized with the trunk.
Please do not commit to the eve branch until the synchronization is complete.

Regards,
EVE""")

	# merge
	trunk_revision = esvn.info_remote_revision_number(v_url_svn_trunk)
	last_merge_revision = esvn.last_merge_revision_number(v_url_svn_eve)
	esvn.merge(merge_path, v_url_svn_trunk, pysvn.Revision(pysvn.opt_revision_kind.number, last_merge_revision), pysvn.Revision(pysvn.opt_revision_kind.number, trunk_revision))

	# wait for conflicts to be resolved
	success = not esvn.has_conflicts(merge_path)
	first = True
	while not success:
		if first:
			first = False
			SystemLogger.error("Merge has produced conflicts")
			send_mail(v_email_merge_info, "[EVE] WAITING: merge produced conflicts", "Resolve conflicts manually and then continue script.")
		else:
			SystemLogger.error("There are still conflits!")
		print ("---")
		print ("Press enter when conflicts are resolved.")
		input()
		success = not esvn.has_conflicts(merge_path)
	SystemLogger.success("Merge successful")

	# compile
	check_environment_variables()
	compile_runtime()
	compile_eve('bench')
	
	# wait for compilation to be successful
	success = is_eve_compilation_successful('bench')
	first = True
	while not success:
		if first:
			first = False
			SystemLogger.error("EVE compilation failed")
			send_mail(v_email_merge_info, "[EVE] WAITING: EVE compilation failed", "Solve compilation problems manually and then continue script.")
		else:
			SystemLogger.error("compilation still fails!")
		print ("---")
		print ("Press enter when compilation problems are resolved.")
		input()
		if not is_eve_compilation_successful('bench'):
			compile_runtime()
			compile_eve('bench')
		success = is_eve_compilation_successful('bench')
	SystemLogger.success("Compilation successful")

	# commit
	message = "<<Merged from trunk#" + str(trunk_revision) + ".>>"
	esvn.commit(merge_path, message)
	first = True
	esvn.update (merge_path, True)
	while esvn.info_local_revision_number(merge_path) <= trunk_revision and False:
		if first:
			first = False
			SystemLogger.error("EVE commit failed")
			send_mail(v_email_merge_info, "[EVE] WAITING: commit failed", "Commit manually and then continue script.")
		else:
			SystemLogger.error("Local revision (" + str(esvn.info_local_revision_number(merge_path)) + ") still smaller than TRUNK (" + str(trunk_revision) + ")")
		print ("---")
		print ("Press enter when you have commited the repository manually.")
		print ("Commit message: " + message)
		input()
		esvn.update (merge_path, true)
	SystemLogger.success("Commit successful")
	
	# make delivery
	delivery_url = make_delivery()
	version, path = get_installed_version()

	# send email
	if delivery_url == None:
		send_mail(v_email_merge_update, "[EVE] merge completed with trunk#" + str(trunk_revision) + ".", """Dear assistants,

The eve branch is now synchronized with trunk#""" + str(trunk_revision) + """ using EiffelStudio """ + str(version) + """.
You can now update your checkout of eve and commit again.

Regards,
EVE""")
		send_mail(v_email_merge_info, "[EVE] Delivery creation failed", "See log for more information.")
	else:
		send_mail(v_email_merge_update, "[EVE] merge completed with trunk#" + str(trunk_revision) + " and new delivery available.", """Dear assistants,

The eve branch is now synchronized with trunk#""" + str(trunk_revision) + """ using EiffelStudio """ + str(version) + """.
You can now update your checkout of eve and commit again.

A """ + d_ise_platform + """ delivery of EVE has been created and is available at
  """ + delivery_url + """

Regards,
EVE""")

# ----------------------------------------------------------------------------
# Environment variables
# ----------------------------------------------------------------------------

def check_environment_variables():
	result = True
	# ISE_PLATFORM
	if not "ISE_PLATFORM" in os.environ:
		SystemLogger.error("Environment variable ISE_PLATFORM not set")
		result = False
	elif os.getenv("ISE_PLATFORM") != d_ise_platform:
		SystemLogger.error("Value of environment variable ISE_PLATFORM (" + os.getenv("ISE_PLATFORM") + ") should be '" + d_ise_platform + "'")
		result = False
	else:
		SystemLogger.debug("ISE_PLATFORM = " + os.getenv("ISE_PLATFORM"))
	# ISE_EIFFEL
	if not "ISE_EIFFEL" in os.environ:
		SystemLogger.error("Environment variable ISE_EIFFEL not set")
		result = False
	elif not os.path.isdir(os.getenv("ISE_EIFFEL")):
		SystemLogger.error("Path from environment variable ISE_EIFFEL (" + os.getenv("ISE_EIFFEL") + ") does not exist")
		result = False
	elif not os.path.isdir(os.path.join(os.getenv("ISE_EIFFEL"), "studio", "spec", os.getenv("ISE_PLATFORM"))):
		SystemLogger.error("Installed EiffelStudio version invalid (no directory found under " + os.path.join(os.getenv("ISE_EIFFEL"), "studio", "spec", os.getenv("ISE_PLATFORM")) + ")")
		result = False
	else:
		SystemLogger.debug("ISE_EIFFEL = " + os.getenv("ISE_EIFFEL"))
	# ISE_C_COMPILER
	if not "ISE_C_COMPILER" in os.environ:
		SystemLogger.error("Environment variable ISE_C_COMPILER not set")
		result = False
	elif os.getenv("ISE_C_COMPILER") != d_ise_c_compiler:
		SystemLogger.error("Value of environment variable ISE_C_COMPILER (" + os.getenv("ISE_C_COMPILER") + ") should be '" + d_ise_c_compiler + "'")
		result = False
	else:
		SystemLogger.debug("ISE_C_COMPILER = " + os.getenv("ISE_C_COMPILER"))
	# EIFFEL_SRC
	if not "EIFFEL_SRC" in os.environ:
		SystemLogger.error("Environment variable EIFFEL_SRC not set. EVE compilation not possible")
		result = False
	elif not os.path.isdir(os.getenv("EIFFEL_SRC")):
		SystemLogger.error("Path from environment variable EIFFEL_SRC (" + os.getenv("EIFFEL_SRC") + ") does not exist")
		result = False
	else:
		SystemLogger.debug("EIFFEL_SRC = " + os.getenv("EIFFEL_SRC"))
	# ISE_LIBRARY
	if not "ISE_LIBRARY" in os.environ:
		SystemLogger.error("Environment variable ISE_LIBRARY not set. EVE compilation not possible")
		result = False
	elif not os.path.isdir(os.getenv("ISE_LIBRARY")):
		SystemLogger.error("Path from environment variable ISE_LIBRARY (" + os.getenv("ISE_LIBRARY") + ") does not exist")
		result = False
	else:
		SystemLogger.debug("ISE_LIBRARY = " + os.getenv("ISE_LIBRARY"))
	# PATH: EiffelStudio, Boogie, Z3
	if not "PATH" in os.environ:
		SystemLogger.error("Environment variable PATH not set")
		result = False
	elif False: # TODO: check PATH contents
		result = False
	# final check
	if result:
		SystemLogger.success("Environment variables checked")
	return result

def update_environment_variables():
	# ISE_PLATFORM
	if not "ISE_PLATFORM" in os.environ or os.getenv("ISE_PLATFORM") != d_ise_platform:
		set_persistent_environment_variable("ISE_PLATFORM", d_ise_platform)
	# ISE_EIFFEL
	version, path = get_installed_version()
	if "ISE_EIFFEL" in os.environ and path == None:
		SystemLogger.debug ("WARNING: No nightly build available. Using ISE_EIFFEL = " + os.getenv("ISE_EIFFEL"))
	elif not "ISE_EIFFEL" in os.environ or os.getenv("ISE_EIFFEL") != path:
		set_persistent_environment_variable("ISE_EIFFEL", path)
	else:
		raise Exception ("Could not set ISE_EIFFEL environment variable.")
	# ISE_C_COMPILER
	if not "ISE_C_COMPILER" in os.environ or os.getenv("ISE_C_COMPILER") != d_ise_c_compiler:
		set_persistent_environment_variable("ISE_C_COMPILER", d_ise_c_compiler)
	# EIFFEL_SRC
	eiffel_source = os.path.realpath(v_dir_eve_source)
	if not "EIFFEL_SRC" in os.environ or os.getenv("EIFFEL_SRC") != eiffel_source:
		set_persistent_environment_variable("EIFFEL_SRC", eiffel_source)
	# ISE_LIBRARY
	eiffel_source = os.path.realpath(v_dir_eve_source)
	if not "ISE_LIBRARY" in os.environ or os.getenv("ISE_LIBRARY") != eiffel_source:
		set_persistent_environment_variable("ISE_LIBRARY", eiffel_source)
	# PATH: EiffelStudio
	# TODO: update PATH contents
	# Temporary path update for execution in same session
	os.environ['PATH'] = os.path.join(os.getenv("ISE_EIFFEL"), 'studio', 'spec', os.getenv("ISE_PLATFORM"), 'bin') + os.pathsep + os.environ['PATH']
	return

def set_persistent_environment_variable(varname, value):
	SystemLogger.debug("setting environment variable " + varname + " to " + value)
	os.environ[varname] = value
	if platform.system() == 'Windows':
		execute(['setx', varname, value], SystemLogger.get_file())
	return

# ----------------------------------------------------------------------------
# Run EiffelStudio or finalized EiffelStudio
# ----------------------------------------------------------------------------

def run_eiffel_studio():
	# Select EiffelStudio (or install if not available)
	current_version, current_path = get_installed_version()
	if current_version == -1:
		update_EiffelStudio()
		current_version, current_path = get_installed_version()
	# Update Environment variables
	update_environment_variables()
	# Run EiffelStudio
	execute(['ec', '-gui'])

def run_eve():
	# Select EiffelStudio (or install if not available)
	current_version, current_path = get_installed_version()
	if current_version == -1:
		update_EiffelStudio()
		current_version, current_path = get_installed_version()
	# Update Environment variables
	update_environment_variables()
	os.environ["ISE_PRECOMP"] = os.path.join(v_dir_eve_source, "Delivery", "precomp", "spec", "platform");
	# Run EiffelStudio
	exe_path = os.path.realpath(os.path.join(v_dir_eve_source, "Eiffel", "Ace", "EIFGENs", "bench", "F_code", d_eve_exe_name))
	if os.path.isfile(exe_path):
		execute([exe_path, '-gui'])
	else:
		SystemLogger.error("Finalized eve executable does not exist (" + exe_path + ").")

# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------

def main():
	mode = 'default'
	submode = None
	if (len(sys.argv) > 1):
		mode = sys.argv[1]
	if (len(sys.argv) > 2):
		submode = sys.argv[2]

	if mode == 'default':
		print('usage:\n'
			'  eve.py update --- Update or install EiffelStudio; update and compile EVE.\n'
			'  eve.py finalize eve --- Finalize EVE.\n'
			'  eve.py eve --- Launch finalized EVE.\n'
			'  eve.py es --- Launch EiffelStudio.\n')
	elif mode == 'es':
		run_eiffel_studio()
	elif mode == 'eve':
		run_eve()
	elif mode == 'check':
		if not check_environment_variables():
			update_environment_variables()
	elif mode == 'update' and submode == None:
		update_EiffelStudio()
		esvn.update_repository(v_url_svn_eve_src, v_dir_eve_source)
		compile_runtime()
		compile_eve('bench')
	elif mode == 'update' and (submode == 'EiffelStudio' or submode == 'es'):
		update_EiffelStudio()
	elif mode == 'update' and submode == 'source':
		esvn.update_repository(v_url_svn_eve_src, v_dir_eve_source)
	elif mode == 'compile' and submode == 'runtime':
		if not check_environment_variables():
			update_environment_variables()
		compile_runtime()
	elif mode == 'compile' and (submode == None or submode == 'eve'):
		if not check_environment_variables():
			update_environment_variables()
		compile_eve('bench')
	elif mode == 'finalize' and (submode == None or submode == 'eve'):
		if not check_environment_variables():
			update_environment_variables()
		finalize_eve('bench')
	elif mode == 'delivery':
		if not check_environment_variables():
			update_environment_variables()
		make_delivery()
	elif mode == 'merge':
		make_merge()
	else:
		if submode == None:
			SystemLogger.error("invalid option " + mode)
		else:
			SystemLogger.error("invalid option " + mode + " / " + submode)
	return

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		import traceback
		traceback.print_exc()
		input()

