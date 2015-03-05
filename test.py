import elogger
from elogger import SystemLogger

import esvn
import config

def test_logger ():
	with elogger.Logger("test_logger.txt", 3) as log:
		log.debug ("debug")
		log.info ("info")
		log.warning ("warning")
		log.success ("success")
		log.error ("error")

def test_svn():
	esvn.update_repository(config.v_url_svn_trunk_src, "./test")


def main ():
	SystemLogger.success ("Starting tests.")
	test_svn()

if __name__ == "__main__":
	main()
