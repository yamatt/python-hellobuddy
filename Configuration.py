'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import ConfigParser
import os
import pickle
from base64 import b64encode, b64decode
class Configuration:
	def __init__(self,app_name):
		self._name = ""
		self._password = ""
		self._service = "identi.ca" #default to identi.ca FUCK YEA!
		self._textlimit=140
		self.config = ConfigParser.RawConfigParser()
		config_file = ".%s" % (app_name)
		self.file = os.path.join( os.path.expanduser("~"),config_file )
		if os.path.exists( self.file ):
			try:
				self.config.read(self.file)
				self._name = self.config.get('access','name')
				self._password = self.get('access','password', enc=True, default="")
				self._service = self.config.get('access','service')
				self._textlimit = self.config.get('access','textlimit')
			except:
				self.set('access', 'name', self._name)
				self.set('access', 'password', self._password)
				self.set('access', 'service', self._service)
				self.set('access', 'textlimit', self._textlimit)
				pass #bummer
				
	def save(self):
		f = open(self.file,"w")
		self.config.write(f)
		f.close()
		#set the perms
		os.chmod(self.file, 0600)
	
	def name(self,value=None):
		if value!=None:
			self._name = value
			self.set('access', 'name', self._name)
		return self._name
		
	def password(self,value=None):
		if value!=None:
			self._password = value
			self.set('access', 'password', self._password,enc=True)
			
		return self._password
	
	def service(self,value=None):
		if value!=None:
			self._service = value
			self.set('access', 'service', self._service)
		return self._service
	
	def textlimit(self,value=None):
		if value!=None:
			self._textlimit = value
			self.set('access', 'textlimit', self._textlimit)
		return self._textlimit
	
	def set(self,section,key,value,pickled = False,enc=False):
		if not self.config.has_section(section) :
			self.config.add_section(section)
		if pickled:
			value = pickle.dumps(value)
		elif enc:
			value = b64encode( value )
		self.config.set(section,key,value)	
		
	def get(self,section,key,pickled=False,default=False,enc=False):
		try:
			if pickled:
				val = pickle.loads( self.config.get(section,key) )
			elif enc:
				val = b64decode(self.config.get(section,key) )
			else:
				val = self.config.get(section,key)	
		except :
			print "key exceptions %s : %s" % (section,key)
			val = default
		return val
	
	def get_bool(self,section, option):
		try:
			val = self.config.get(section,option)
		except:
			val=False
		if val == 'True':
			val=True
		else:
			val=False
		return val
		
	def get_bool_option(self,option):
		return self.get_bool('options',option)
