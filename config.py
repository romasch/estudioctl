
# Base path for the main setup.
# The order of precedence is as follows:
# 1. v_estudioctl_base_override
# 2. The environment variable with the given name.
# 3. The parent directory, if none of the above are defined.
v_base_directory_override = None
v_base_directory_environment_variable = "ESTUDIOCTL"


# Directory where the trunk repository will be checked out.
v_dir_trunk_source = "source"

# Directory where the EVE repository will be checked out.
v_dir_eve_source = "src_eve"

# Directory where eweasel will be checked out.
v_dir_eweasel = "eweasel"

# Directory where the nightly builds will be installed.
v_dir_nightly = "nightly"

# Build directories and subdirectories.
v_dir_build = "build"
v_dir_build_eweasel = "build/eweasel"

v_url_svn_trunk_src = "https://svn.eiffel.com/eiffelstudio/trunk/Src"
v_url_svn_eve_src = "https://svn.eiffel.com/eiffelstudio/branches/eth/eve/Src"

# Name of log file
v_log_filename = "./log.txt"

# 0: no output
# 1: error/warning/success output
# 2: info output
# 3: log output
v_verbose_level = 2


# ----------------------------------------------------------------------------
# Gather system information
# ----------------------------------------------------------------------------

import platform
import os

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
