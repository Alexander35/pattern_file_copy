from smb.SMBConnection import SMBConnection
from log import logger_setup

class SMB_Worker:
	def __init__(self, smb_user, user_pass, client_machine_name, server_name):
		self.conn = SMBConnection(smb_user, user_pass, client_machine_name, server_name, domain='zkp28' ,use_ntlm_v2 = False, is_direct_tcp=True)
		self.logger = logger_setup(__name__)
		try: 	
			self.conn.connect(server_name, 445)
			self.logger.info('Server {} port {} connected'.format(server_name, 445, ))
		except Exception as exc:
			print('connException: {}\n'.format(Exception) )
			self.logger.error('An error occured . connException - {}'.format(exc))

	def get_file_list(self, folder_name):
		try:
			file_list = self.conn.listPath('d$', folder_name)
			self.logger.info('get_file_list from folder : {}'.format(folder_name))
			return file_list
		except Exception as exc:
			self.logger.error('get_file_list Error : {}'.format(exc))
		
	def get_attributes(self, filelist):
		try:
			attributes = [
					{
						'filename' : item.filename, 
						'size' : item.file_size, 
						'isDirectory': item.isDirectory
					}
					for item in filelist
				]
			return attributes
		except Exception as exc:
			self.logger.error('get_attributes Error : {}'.format(exc))		