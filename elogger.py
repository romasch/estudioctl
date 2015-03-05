# ----------------------------------------------------------------------------
# Helper functions for logging and printing.
#
#For a systemwide unique logger, import the module like this:
#from logger import SystemLogger
#
# ----------------------------------------------------------------------------

import time
import traceback
import config

# Try to enable nicely colored console output.
_has_colorama = False
try:
	from colorama import init, Fore, Back, Style
	init()
	_has_colorama = True
except ImportError:
	pass

# The logger class. For exception safety this should be used inside a 'with' statement.
class Logger:

	# Initialization and teardown

	def __init__ (self, a_file, a_level):
		self._file_name = a_file
		self._verbosity = a_level
		self._log_file = None
		self._start = 0.0

	def __enter__ (self):
		open (self._file_name, 'w').close() # Clear log file.
		self._log_file = open (self._file_name, 'w') # Open log file.
		self._start = time.time() # Remember start time.
		return self

	def __exit__ (self, etype, evalue, etrace):
		if evalue != None:
			self._to_logfile ("An exception happened.\n\n" + traceback.format_exc())
		self.info("All done (duration " + self._duration() + ")", force=True)
		self._log_file.close()

	# Private implementation features.

	def _to_logfile (self, text):
		self._log_file.write(self._duration())
		self._log_file.write("  ---  ")
		self._log_file.write(text)
		self._log_file.write("\n")
		self._log_file.flush()

	def _duration (self):
		return time.strftime('%H:%M:%S', time.gmtime(time.time() - self._start))

	# Public methods

	def debug (self, text):
		if self._verbosity > 2:
				print (text)
		self._to_logfile(text)

	def info (self, text, pre='', force=False):
		if self._verbosity > 1 or force:
				print (pre + text)
		self._to_logfile(pre + text)

	def warning (self, text, pre=''):
		if self._verbosity > 0:
			if _has_colorama:
				print (pre + Back.YELLOW + Fore.YELLOW + Style.BRIGHT + text + Style.RESET_ALL)
			else:
				print (pre + text)
		self._to_logfile(pre + text)

	def error (self, text, pre=''):
		if self._verbosity > 0:
			if _has_colorama:
				print (pre + Back.RED + Fore.RED + Style.BRIGHT + text + Style.RESET_ALL)
			else:
				print (pre + text)
		self._to_logfile(pre + text)

	def success (self, text, pre=''):
		if self._verbosity > 0:
			if _has_colorama:
				print (pre + Back.GREEN + Fore.GREEN + Style.BRIGHT + text + Style.RESET_ALL)
			else:
				print (pre + text)
		self._to_logfile(pre + text)

	def get_file(self):
		return self._log_file

# A unique system-wide logger.
SystemLogger = Logger(config.v_log_filename, config.v_verbose_level)
SystemLogger.__enter__()

import atexit
import sys

def _stop (logger):
	etype, evalue, etrace = sys.exc_info()
	logger.__exit__ (etype, evalue, etrace)

atexit.register (_stop, SystemLogger)

