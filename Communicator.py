'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
from base64 import b64encode
from urllib import urlencode
import urllib2
import gobject
from threading import Thread
from CertificateValidatingHTTPSHandler import *

#import thread
from time import sleep
class Communicator(gobject.GObject,Thread):
	__gsignals__ = {
		'statusesXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'configXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'mentionsXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'group-statusesXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'user-statusesXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'verify_credentialsXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
			),
		'conversationXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,gobject.TYPE_STRING)
			),
		'new-statusXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'userXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'groupXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'join-groupXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'leave-groupXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'direct_messagesXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'user_is_friendXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'user_is_memberXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'memberXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'friendshipXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'exception-caught': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,gobject.TYPE_STRING,gobject.TYPE_STRING )
			),
		'widget-image': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_PYOBJECT,gobject.TYPE_STRING)
			),
		'direct-messageXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'redent-statusXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'block-createXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'block-destroyXML': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
	}
	
	def __init__(self, app_name=None, cert_file=None, apiroot="http://identi.ca/api"):
		gobject.GObject.__init__(self)
		Thread.__init__(self)
		self.daemon = True
		self.queue = []
		#self.name = name
		#self.password = password
		self.agent = app_name
		self.apiroot = apiroot
		self.cert_file = cert_file
		self.sapiroot = self.apiroot[:4] + "s" + self.apiroot[4:]
		
		#TODO: check for the certs and notify the user that shit could get fucked
		if has_ssl_module:
			handler = VerifiedHTTPSHandler(ca_certs=self.cert_file)
		else:
			try:
				handler = urllib2.HTTPSHandler()
			except:
				handler = urllib2.HTTPHandler()
		self.opener = urllib2.build_opener(handler)
		
	def set_name_and_password(self, name, password):
		self.name=name
		self.password = password
		self.authheader =	self.get_auth_string(name, password)
	
	def set_service(self,service):
		self.apiroot, self.sapiroot = self.get_apiroot_for_service( service )
		
	def get_apiroot_for_service(self,service):
		apiroot = service + "/api"
		if apiroot[:7] != "http://":
			apiroot = "http://" + apiroot
		sapiroot = apiroot[:4] + "s" + apiroot[4:]
		return (apiroot, sapiroot)
	
	def get_auth_string(self, name, password):
		authstring = '%s:%s' % (name, password)
		enc = b64encode(authstring)
		return "Basic %s" % enc
			
	def get_statuses(self,count="20",since="0"):
		url = "%s/statuses/friends_timeline/%s.xml?count=%s&since_id=%s" % (self.apiroot,self.name,count,since)
		print url
		self.process_httprequest(url,'statusesXML')
	
	def verify_credentials(self, name, password, service):
		(api,sapi) = self.get_apiroot_for_service(service)
		url = "%s/account/verify_credentials.xml" % (sapi)
		authheader = self.get_auth_string(name, password)
		request = urllib2.Request(url)
		request.add_header("Authorization", authheader)
		data = (name, password, service)
		self.process_httprequest(request,'verify_credentialsXML', data)
		
	def get_config(self):
		url = "%s/statusnet/config.xml" % (self.apiroot)
		request = urllib2.Request(url)
		self.process_httprequest(request,'configXML')
		
	def get_widget_image(self,image):
		self.get_image(image,'widget-image')
	
	def get_image(self,image,signal):	
		url=image
		print url
		self.process_httprequest(url,signal,image)
		
	def get_conversation(self,id,conversation_id):
		url="%s/statuses/show/%d.xml" % (self.sapiroot,id)
		print url
		request = urllib2.Request(url)
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'conversationXML',conversation_id)
		
	def get_mentions(self,count="20",since="0"):
		url = "%s/statuses/mentions/%s.xml?count=%s&since_id=%s" % (self.apiroot,self.name,count,since)
		print url
		self.process_httprequest(url,'mentionsXML') 
	
	def	get_user_info(self,name):
		url="%s/users/show.xml?screen_name=%s" % (self.sapiroot,name)
		print url
		request = urllib2.Request(url)
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'userXML') 
	
	def get_user_statuses(self,name):
		url="%s/statuses/user_timeline.xml?screen_name=%s" % (self.sapiroot,name)
		print url
		request = urllib2.Request(url)
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'user-statusesXML')
	
	def	get_remote_user_info(self, service, name):
		url="http://%s/api/users/show.xml?screen_name=%s" % (service,name)
		print url
		self.process_httprequest(url,'userXML') 
	
	def get_remote_user_statuses(self, service, name):
		url="http://%s/api/statuses/user_timeline.xml?screen_name=%s" % (service,name)
		print url
		self.process_httprequest(url,'user-statusesXML')
	
	
	def get_user_is_friend(self,name):
		#is the user a friend?
		url="%s/friendships/exists.xml?user_a=%s&user_b=%s" % (self.apiroot,self.name,name)
		print url
		self.process_httprequest(url,'user_is_friendXML') 
	
	def favorite(self,id):
		#favorite this thing
		url="%s/favorites/create/%s.xml" % (self.sapiroot,id)
		print url
		request = urllib2.Request(url,"")
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,None)
		
	def unfavorite(self,id):
		#favorite this thing
		url="%s/favorites/destroy/%s.xml" % (self.sapiroot,id)
		print url
		request = urllib2.Request(url,"")
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,None)
	
	def	get_group_info(self,name):
		url="%s/statusnet/groups/show/%s.xml" % (self.sapiroot,name)
		print url
		request = urllib2.Request(url,"")
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'groupXML') 
	
	def	get_group_statuses(self,name):
		url="%s/statusnet/groups/timeline/%s.xml" % (self.apiroot,name)
		print url
		request = urllib2.Request(url,"")
		self.process_httprequest(request,'group-statusesXML') 
	
		
	def get_user_is_member(self,group_name):
		#is the user a friend?
		url="%s/statusnet/groups/is_member.xml?screen_name=%s&group_id=%s" % (self.apiroot,self.name,group_name)
		print url
		#request = urllib2.Request(url)
		self.process_httprequest(url,'user_is_memberXML') 
	
	def get_direct_messages(self,id):
		url="%s/direct_messages.xml?since_id=%d" % (self.sapiroot,id)
		print url
		request = urllib2.Request(url,"")
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'direct_messagesXML')
	
	def friendship_create(self,name):
		url="%s/friendships/create/%s.xml" % (self.sapiroot,name)
		print url
		request = urllib2.Request(url,"")
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'friendshipXML')
	
	def friendship_destroy(self,name):
		url="%s/friendships/destroy.xml?screen_name=%s" % (self.sapiroot,name)
		print url
		request = urllib2.Request(url,"")
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'friendshipXML')
		
	def group_join(self,group_id):
		url="%s/statusnet/groups/join.xml" % (self.sapiroot)
		print url
		request = urllib2.Request(url,"id=%s" % (group_id) )
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'join-groupXML')
	
	def group_leave(self,group_id):
		url="%s/statusnet/groups/leave.xml" % (self.sapiroot)
		print url, group_id
		request = urllib2.Request(url,"id=%s" % (group_id) )
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'leave-groupXML')
		
	def send_update_status(self,text,respond_to_id=0):
		data={"status":text,"source":self.agent} 
		if(respond_to_id>0):
			data["in_reply_to_status_id"]=respond_to_id
		encoded_data =urlencode(data)
		url="%s/statuses/update.xml" % (self.sapiroot)
		print url
		request = urllib2.Request(url,encoded_data)
		request.add_header("Authorization", self.authheader)
		#add this request to the front of the communication queue
		self.queue.append( (request,'new-statusXML',None) )

	def send_redent(self,status_id):
		url="%s/statuses/retweet.xml" % (self.sapiroot)
		data={"id":status_id}
		encoded_data =urlencode(data)
		print url
		request = urllib2.Request(url, encoded_data)
		request.add_header("Authorization", self.authheader)
		self.queue.append( (request,'redent-statusXML',None) )
	
	def block_create(self,user_id):
		url="%s/blocks/create.xml?user_id=%s" % (self.sapiroot,user_id)
		request = urllib2.Request(url,'')
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'block-createXML')
		
	def block_destroy(self,user_id):
		url="%s/blocks/destroy.xml?user_id=%s" % (self.sapiroot,user_id)
		print url
		request = urllib2.Request(url,'')
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'block-destroyXML')
		
	def send_direct_message( self, text, screen_name):
		data={"text":text,"screen_name":screen_name,"source":self.agent}
		encoded_data=urlencode(data)
		url="%s/direct_messages/new.xml" % (self.sapiroot)
		print url
		request = urllib2.Request(url,encoded_data)
		request.add_header("Authorization", self.authheader)
		self.process_httprequest(request,'direct-messageXML')
		
	def quit(self):
		self.looping = False
	
	def run(self):
		self.looping = True
		while self.looping:
			#are there any requests in the queue?
			if len(self.queue)>0:
				#pop the first item
				(request,signal,data) = self.queue[0]
				del self.queue[0]
				#run the request
				self.threaded_request(request,signal,data)
			#take a nap
			sleep(1)	
			

	def process_httprequest(self,request,signal=None,data=None):
		self.queue.append( (request,signal,data) )

	def threaded_request(self,request,signal,data):
		text = ''
		try:
			f=self.opener.open( request )
			#read the data
			text = f.read()
			#pass the data as a signal
			if signal!=None:
				#print "emitting %s signal" % (signal)
				if data!=None:
					#pack the data 
					gobject.idle_add(self.emit,signal,text,data)
				else:
					gobject.idle_add(self.emit,signal,text)
				
		except urllib2.HTTPError, e :
			text = e.read()
			gobject.idle_add(self.emit,"exception-caught",e.code,text,signal)
		except InvalidCertificateException, ice:
			gobject.idle_add(self.emit,"exception-caught",ice,text,signal)
		except Exception,error:
			gobject.idle_add(self.emit,"exception-caught","unknown error",text,signal)

