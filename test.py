import elogger
from elogger import SystemLogger

import esvn
import elocation
import eutils
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

def test_location():
	elocation.move ("eve", "eve2")
	elocation.copy ("eve2", "eve3")
	elocation.delete ("eve3")
	elocation.move ("eve2", "eve")
	print (elocation.base_directory())
	print (elocation.trunk_source())
	print (elocation.eve_source())
	print (elocation.eweasel())
	print (elocation.nightly())
	print (elocation.build())
	print (elocation.eweasel_build())
	
def test_compress():
	name = eutils.compress ("./compress")
	eutils.extract ("./decompress.tar.bz2")

def main ():
	SystemLogger.success ("Starting tests.")
	#test_svn()
	test_location()
	test_compress()

if __name__ == "__main__":
	main()
