# ----------------------------------------------------------------------------
# helper functions: svn
# ----------------------------------------------------------------------------

_has_pysvn = False
_has_cmdsvn = False

import subprocess
import os
import os.path
import re

from logger import SystemLogger



# Import pysvn if available.
try:
	import pysvn
	_has_pysvn = True
except ImportError:
	try:
		if subprocess.call(['svn', 'help'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
			_has_cmdsvn = True
		else:
			SystemLogger.error("pysvn module is not available. SVN command line not available. All SVN operations are disabled.")
	except OSError:
		SystemLogger.error("pysvn module is not available. SVN command line not available. All SVN operations are disabled.")


def svn_get_login(realm, username, may_save):
	return True, v_svn_user, v_svn_password, False

def svn_ssl_server_trust_prompt(trust_dict):
	"""Helper function to ignore any SSL trust errors"""
	return True, trust_dict['failures'], True

svn_helper_revision = -1
def svn_notify(arg):
	global svn_helper_revision
	if arg['action'] == pysvn.wc_notify_action.update_completed:
		svn_helper_revision = arg['revision'].number

_svn = None
if _has_pysvn:
	svn = pysvn.Client()
	svn.callback_get_login = svn_get_login
	svn.callback_ssl_server_trust_prompt = svn_ssl_server_trust_prompt
	svn.callback_notify = svn_notify

def svn_info_remote_url(path):
	"""Remote URL of the repository at local path"""
	global svn, _has_pysvn
	if _has_pysvn:
		info = svn.info2(path, revision=pysvn.Revision(pysvn.opt_revision_kind.working), recurse=False)
		return info[0][1]["URL"]
	else:
		output = subprocess.check_output(['svn', 'info', path])
		expr = re.compile(r'^URL:\s(.*)$', re.M)
		return expr.search(output).group(1).strip()

def svn_info_local_revision_number(path):
	"""Revision number of the repository at local path"""
	global svn, _has_pysvn
	if _has_pysvn:
		info = svn.info2(path, revision=pysvn.Revision(pysvn.opt_revision_kind.working), recurse=False)
		return info[0][1]["rev"].number
	else:
		output = subprocess.check_output(['svn', 'info', path])
		expr = re.compile(r'^Revision:\s(.*)$', re.M)
		return expr.search(output).group(1)

def svn_info_remote_revision_number(url):
	"""Revision number of the repository at remote URL"""
	global svn, _has_pysvn
	if _has_pysvn:
		info = svn.info2(url, revision=pysvn.Revision(pysvn.opt_revision_kind.head), recurse=False)
		return info[0][1]["rev"].number
	else:
		output = subprocess.check_output(['svn', 'info', url])
		expr = re.compile(r'^Revision:\s(.*)$', re.M)
		return expr.search(output).group(1)

def svn_is_up_to_date(path):
	"""Is repository at local path up to date?"""
	remote_url = svn_info_remote_url(path)
	remote_revision = svn_info_remote_revision_number(remote_url)
	local_revision = svn_info_local_revision_number(path)
	return local_revision == remote_revision

def svn_has_conflicts(path):
	"""Does repository at path have any conflicts?"""
	global svn
	changed = svn.status(path, ignore_externals=True)
	for f in changed:
		if f.text_status == pysvn.wc_status_kind.conflicted:
			return True
	return False

def svn_update(path, force=False):
	"""Update repository at local path"""
	global svn, _has_pysvn
	SystemLogger.debug("SVN: updating repository at " + path)
	if _has_pysvn:
		if not svn_is_up_to_date(path) or force:
			revision = svn.update(path)[0].number
		else:
			revision = svn_info_local_revision_number(path)
	else:
		output = subprocess.check_output(['svn', 'update', path])
		expr = re.compile(r'.*revision\s([\d]+).*')
		revision = expr.search(output).group(1)
	SystemLogger.debug("SVN: revision " + str(revision))
	return revision

def svn_checkout(url, path):
	"""Checkout HEAD revision from url to path"""
	global svn, svn_helper_revision, _has_pysvn
	SystemLogger.debug("SVN: checkout from " + url + " to " + path)
	if _has_pysvn:
		svn.checkout(url, path)
		revision = svn_helper_revision
	else:
		output = subprocess.check_output(['svn', 'checkout', url, path])
		expr = re.compile(r'.*Checked out revision\s([\d]+).*')
		revision = expr.search(output).group(1)
	SystemLogger.debug("SVN: revision " + str(revision))
	return revision

def svn_last_merge_revision_number(url):
	"""Get revision number of last merge of repository at url"""
	global svn
	head_revision = svn_info_remote_revision_number(url)
	bottom_revision = head_revision
	found_revision = -1
	while True:
		bottom_revision = bottom_revision - 20
		log = svn.log(url, pysvn.Revision(pysvn.opt_revision_kind.number, bottom_revision), pysvn.Revision(pysvn.opt_revision_kind.number, head_revision))
		for entry in log:
			match = re.search("<<Merged from trunk#(\d+)", entry['message'])
			if match != None:
				found_revision = int(match.group(1))
		if found_revision > 0:
			return found_revision
		if bottom_revision < 0:
			return -1

def svn_merge(path, url, rev_start, rev_end):
	"""Merge repository at path with repository at url"""
	source_path = os.path.realpath(path)
	SystemLogger.debug("SVN merge")
	SystemLogger.debug("Path: " + source_path)
	SystemLogger.debug("URL: " + url)
	SystemLogger.debug("Revision from: " + str(rev_start))
	SystemLogger.debug("Revision to: " + str(rev_end))
	svn.merge_peg(url, rev_start, rev_end, rev_end, source_path)

def svn_commit(path, message):
	"""Commit repository at path using the commit message"""
	SystemLogger.debug("SVN commit")
	SystemLogger.debug("Path: " + path)
	SystemLogger.debug("Message: " + message)
	svn.checkin(path, message)

def update_repository(url, path):
	"""Update repository at given path. If no checkout exists, do a new checkout from given url."""
	revision = -1
	if os.path.exists(path):
		SystemLogger.info("Updating repository")
		SystemLogger.info("Path: " + path)
		remote_url = svn_info_remote_url(path)
		if url == remote_url:
			revision = svn_info_local_revision_number(path)
			remote_revision = svn_info_remote_revision_number(url)
			SystemLogger.debug("Local revision: " + str(revision))
			SystemLogger.debug("Remote revision: " + str(remote_revision))
			if revision == remote_revision:
				SystemLogger.success("Repository '" + path + "' is up-to-date at revision " + str(revision))
			else:
				revision = svn_update(path)
				SystemLogger.success("Repository '" + path + "' is updated to revision " + str(revision))
		else:
			SystemLogger.error("Repository URL of existing directory '" + path + "'  does not match expected remote url")
			SystemLogger.error("Existing URL: " + remote_url)
			SystemLogger.error("Expected URL: " + url)
	else:
		SystemLogger.info("Checking out repository")
		SystemLogger.info("URL: " + url)
		SystemLogger.info("Location: " + path)
		revision = svn_checkout(url, path)
		SystemLogger.success("Checkout of revision " + str(revision) + " complete")
	return revision 

