
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

v_url_svn_trunk_src = "https://svn.eiffel.com/eiffelstudio/trunk/Src/C/run-time/scoop"
v_url_svn_eve_src = "https://svn.eiffel.com/eiffelstudio/branches/eth/eve/Src/C/run-time/scoop"

# Name of log file
v_log_filename = "./log.txt"

# 0: no output
# 1: error/warning/success output
# 2: info output
# 3: log output
v_verbose_level = 3