import logging
from time import gmtime, strftime

def logger_setup( logger_name):	
	logfile_name = logger_name 
	logfile_name = '{}{}'.format('log/', logfile_name)
	current_time = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
	logfile_name = '{0}-{1}'.format(logfile_name, current_time)
	
	l = logging.getLogger(logger_name)
	formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
	fileHandler = logging.FileHandler(logfile_name, mode='w')
	fileHandler.setFormatter(formatter)
	l.setLevel(logging.DEBUG)
	l.addHandler(fileHandler)

	return logging.getLogger(logger_name)	