import logger
from logger import SystemLogger

def test_logger ():
	with logger.Logger("test_logger.txt", 3) as log:
		log.debug ("debug")
		log.info ("info")
		log.warning ("warning")
		log.success ("success")
		log.error ("error")


def main ():
	SystemLogger.success ("Hello World")
	test_logger()

if __name__ == "__main__":
	with logger.Logger("log.txt", 2) as log:
		SystemLogger = log
		main()
