import os
import errno
import zipfile
from log import logger_setup

class OS_Suit:
	""" creates folder, listen file attributes etc"""
	def __init__(self, output_folder, input_folder, temp_folder):
		self.logger = logger_setup(__name__)
		self.output_folder = output_folder
		self.temp_folder = temp_folder
		self.input_folder = input_folder
		try:
			os.makedirs(self.output_folder)
			os.makedirs(self.temp_folder)
		except Exception as exc:
			self.logger.error('initialize global folders error : {}'.format(exc))	

	def create_local_folder(self, folder_name):
		try:
		    os.makedirs(self.output_folder + '/' + folder_name)
		    self.logger.info('folder created : {}'.format(folder_name))
		except OSError as exc:
			self.logger.warning('create_local_folder warn : {}'.format(exc))
			if exc.errno != errno.EEXIST:
				raise

	def unzip_to_temp(self, target_file):
		try:
			zip_ref = zipfile.ZipFile(self.input_folder + '/' + target_file, 'r')
			zip_ref.extractall(self.temp_folder + '/' + target_file)
			zip_ref.close()
			self.logger.info('zip file has been extracted : {}'.format(self.input_folder + '/' + target_file))
			return self.temp_folder + '/' + target_file		
		except Exception as exc:
			self.logger.error('unzip_to_temp error : {}'.format(exc))

	def get_filelist_with_attributes(self, path):
		try:	
			attributes = [
					{
						'filename' : item.name,
						'info' : os.stat(item),
						'isfile' : os.path.isfile(item)
					}
					for item in os.scandir(path)
				]	
			return attributes
		except Exception as exc:
			self.logger.error('get_filelist_with_attributes error : {}'.format(exc)) 		

	def erase_temp(self):
		pass				