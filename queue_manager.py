from csv_worker import CSV_Worker
from log import logger_setup
from smb_worker import SMB_Worker
from os_suit import OS_Suit
import re
import shutil
import configparser
from time import gmtime, strftime

class Queue_Manager:
	def __init__(self, data_queue):
		self.data_queue = data_queue
		self.logger = logger_setup(__name__)
		self.control_logger = logger_setup('ControlLog.log')
		# get smb connection
		config = configparser.ConfigParser()
		config.sections = []
		config.read('smb.ini')
		self.SMBW = SMB_Worker(config['SMB']['USER'],config['SMB']['PASS'],config['SMB']['CLIENT_MACHINE'],config['SMB']['SERVER'])
		self.OSS = OS_Suit('C:/OUTPUT_FOLDER', 'C:/MDRtoGKN', 'C:/TEMP_FOLDER')
		self.file_counter = 0

	"""get current folder name , get obj name and zip file name"""
	def item_devide(self, item):
		self.logger.info('current item {} '.format(item))
		self.current_item = item 

		try:
			# replace '/' to '_' in foldernames
			self.current_folder_name = re.split(r'-[0-9]+$',item['OBJ_NUMBER'])[0].replace('/','_')
			self.current_item['OBJ_NUMBER'] = self.current_item['OBJ_NUMBER'].replace('/','_')
			self.logger.info('current folder name {} '.format(self.current_folder_name))
		except Exception as exc:
			self.logger.error('Error {}'.format(Exception))

	def queue_traverse(self):
		[ self.perform_item(item) for item in self.data_queue]

	def perform_item(self, item):
		# find the folder name
		self.item_devide(item)
		curr_remote_folder = '/ais/Docs/request/' + self.current_folder_name +'/' + self.current_item['OBJ_NUMBER']
		filelist = self.SMBW.get_file_list(curr_remote_folder)
		attributes = self.SMBW.get_attributes(filelist)
		
		# create folder tree
		try:
			self.current_path = self.current_folder_name + '/' + self.current_item['OBJ_NUMBER']

			[ self.OSS.create_local_folder(self.current_path + '/' +item['filename']) for item in attributes if item['isDirectory'] ]
		except Exception as exc:
			self.logger.error('attributes list error : {}'.format(exc))

		# unzip to temp
		try:
			res = re.search(r'req.+zip',self.current_item['FILE_NAME_ZIP'])
			tmp_zip = self.OSS.unzip_to_temp(res.group(0))
		except Exception as exc:
			self.logger.error('pattern for zip file name missmatch : {}'.format(exc))

		# get attributes from tmp files
		try:
			self.attributes_tmp = [
					at 
					for at in self.OSS.get_filelist_with_attributes(tmp_zip) 
					if (at['filename'] != '.' and at['filename'] != '..')
				]
			try: 	
				internal_folder =[
						file
						for file in self.attributes_tmp
						if file['isfile'] == False 
					]

				[
					self.final_copy_files( tmp_zip+'/'+internal_folder[0]['filename']+'/'+at['filename'], tmp_zip+'/'+at['filename'])
					for at in self.OSS.get_filelist_with_attributes(tmp_zip + '/' + internal_folder[0]['filename'] ) 
					if (at['filename'] != '.' and at['filename'] != '..')
					and internal_folder != []
				]

				self.attributes_tmp = [
					at 
					for at in self.OSS.get_filelist_with_attributes(tmp_zip) 
					if (at['filename'] != '.' and at['filename'] != '..')
				]

				self.logger.info('internal folder extracted : {}'.format(tmp_zip+'/'+internal_folder['filename']))
			except Exception as exc:
				self.logger.error('internal folder {} : {}'. format(tmp_zip+'/'+internal_folder['filename']), exc )

		except Exception as exc:
			self.logger.error('attributes for ext files : {}'.format(exc))

		try: 
			remote_sub_folder = [
					self.compare_sizes(item['filename'],self.SMBW.get_file_list(curr_remote_folder + '/' + item['filename']),tmp_zip)
					for item in attributes 
					if (item['filename'] != '.' and item['filename'] != '..') 
				]
		except Exception as exc:
			self.logger.error('remote_sub_folder listing {}'.format(exc))

	def compare_sizes(self, rfolder_name, rfile_list, ltmp_folder):
		try:
			# get attr from remote files
			rattr = self.SMBW.get_attributes(rfile_list)
			# self.attributes_tmp
			[
				self.final_copy_files(
					ltmp_folder+'/'+ att['filename'],
					'C:/OUTPUT_FOLDER/'+self.current_path+'/'+rfolder_name+'/'+rattr.filename
					)
				for att in self.attributes_tmp  
				for rattr in rfile_list
				if abs(att['info'].st_size - rattr.file_size) < 5000
				and att['filename'][-3:] == rattr.filename[-3:]
			]

		except Exception as exc:
			self.logger.error('compare_sizes : {}'.format(exc))
			self.control_logger.error('compare_sizes : {}'.format(exc))

	def final_copy_files(self, src, dst):
		shutil.copyfile(src, dst)
		self.file_counter += 1 
		self.control_logger.info(
			'[ file# {} ] {}'.format(
				self.file_counter,
				dst
				)
			)
	
def main():
	CSVW = CSV_Worker('C:/MDRtoGKN/ИНФО/temp.csv')
	data = CSVW.read_file()
	QM = Queue_Manager(data)
	QM.queue_traverse()

if __name__ == '__main__':
	main()