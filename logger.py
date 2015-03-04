# ----------------------------------------------------------------------------
# helper functions: printing
# ----------------------------------------------------------------------------

import config
import time

_has_colorama = False
try:
	from colorama import init, Fore, Back, Style
	init()
	_has_colorama = True
except ImportError:
	pass

_log_file = None
_script_start = None

def start():
	global _script_start, _log_file
	# clear log file
	open(config.v_log_filename, 'w').close()
	# open log file
	_log_file = open(config.v_log_filename, 'w')
	# start timer
	_script_start = time.time()

def stop():
	as_info("All done (duration " + time.strftime('%H:%M:%S', time.gmtime(time.time()-_script_start)) + ")", force=True)
	_log_file.close

def _to_logfile(text):
	if _log_file != None and _script_start != None:
		_log_file.write(time.strftime('%H:%M:%S', time.gmtime(time.time() - _script_start)))
		_log_file.write("  ---  ")
		_log_file.write(text)
		_log_file.write("\n")
		_log_file.flush()
	else:
		print ("Error: Could not log: " + text)


def to_log(text):
	if config.v_verbose_level > 2:
		print (text)
	_to_logfile(text)

def as_info(text, pre='', force=False):
	if config.v_verbose_level > 1 or force:
		print (pre + text)
	_to_logfile(pre + text)

def as_warning(text, pre=''):
	if config.v_verbose_level > 0:
		if _has_colorama:
			print (pre + Back.YELLOW + Fore.YELLOW + Style.BRIGHT + text + Style.RESET_ALL)
		else:
			print (pre + text)
	_to_logfile(pre + text)

def as_error(text, pre=''):
	if config.v_verbose_level > 0:
		if _has_colorama:
			print (pre + Back.RED + Fore.RED + Style.BRIGHT + text + Style.RESET_ALL)
		else:
			print (pre + text)
	_to_logfile(pre + text)

def as_success(text, pre=''):
	if config.v_verbose_level > 0:
		if _has_colorama:
			print (pre + Back.GREEN + Fore.GREEN + Style.BRIGHT + text + Style.RESET_ALL)
		else:
			print (pre + text)
	_to_logfile(pre + text) 




to_log ("Hello")
start_logger()
to_log ("world")
as_error ("blub")
as_warning ("asdf")
stop_logger()