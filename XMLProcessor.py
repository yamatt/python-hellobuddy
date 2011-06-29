'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''

from xml.dom.minidom import parse, parseString
import datetime
import time
import locale
import re

class XMLProcessor():
	def __init__(self):
		self.re_source_sub = re.compile(r'<[^>]*?>')
		self.re_server_sub = re.compile(r'/\w+$')
		self.re_zone = re.compile(r'[+|-][0-9]{4}')
	def get_statuses(self,text,is_direct=False):
		dom = parseString(text)
		if is_direct:
			tag='direct_message'
		else:
			tag='status'
		return_data = dom.getElementsByTagName(tag)
		del dom
		return return_data

	def get_dom(self,text):
		dom = parseString(text)
		return dom
		
	def get_error_message(self,text):
		dom = parseString(text)
		message = self.get_node_text(dom, 'error')
		return message
		
	def get_user_info(self,text):
		dom = parseString(text)
		data = {}
		data['id'] = self.get_node_text(dom,'id')
		data['name'] = self.get_node_text(dom,'name')
		data['screen_name'] = self.get_node_text(dom,'screen_name')
		data['location'] = self.get_node_text(dom,'location')
		data['description'] = self.get_node_text(dom,'description')
		data['url']=self.get_node_text(dom,'url')
		data['following']=self.get_node_text(dom,'following')
		data['profile_image_url']=self.get_node_text(dom,'profile_image_url')
		return data
		
	def get_group_info(self,text):
		dom = parseString(text)
		data = {}
		data['id'] = self.get_node_text(dom,'id')
		data['fullname'] = self.get_node_text(dom,'fullname')
		data['location'] = self.get_node_text(dom,'location')
		data['description'] = self.get_node_text(dom,'description')
		data['stream_logo']=self.get_node_text(dom,'stream_logo')
		data['member']=self.get_node_text(dom,'member')
		#data['url']=self.get_node_text(dom,'url')
		data['homepage']=self.get_node_text(dom,'homepage')
		return data
	
	def get_user_is_friend(self,text):
		dom = parseString(text)
		f = self.get_node_text(dom,'friends')
		if f=="true":
			friends = True
		else:
			friends = False
		return friends
	
	def get_user_is_member(self,text):
		dom = parseString(text)
		m = self.get_node_text(dom,'is_member')
		if m=="true":
			member = True
		else:
			member = False
		return member
	
	def get_node_text(self,node,tag):
		try:
			text=node.getElementsByTagName(tag)[0].firstChild.data
		except:
			text=None
		return text

	def fix_the_fucking_date(self,date_string):
		bits = date_string.split(" ")
		#the second to last is the piece of dogshit
		dog_shit = bits[-2]
		offset_hours = int(dog_shit[0:3])
		offset_minutes = int(dog_shit[0] + dog_shit[3:5])
		ds_adjust = datetime.timedelta(hours = offset_hours, minutes = offset_minutes)
		#get rid of this crap
		del(bits[-2])
		#put the string back together
		date_string = " ".join(bits)
		''' Wed May 26 01:27:08 +0000 2010 '''
		#get the current locale time formatting
		lctime = locale.getlocale(locale.LC_TIME)
		#set the locale to the generic C
		locale.setlocale(locale.LC_TIME,"C")
		pdate = datetime.datetime.strptime(date_string,'%a %b %d %H:%M:%S %Y')
		#wipe the shit off your shoe
		pdate -= ds_adjust

		#reset to the current locale
		try:
			locale.setlocale(locale.LC_ALL,lctime)
		except:
			pass # this was an issue on the N810
		t = time.mktime( pdate.timetuple() )
		t-= ( time.timezone )
		localtime = time.localtime(t)
		#are we in shitty DST?
		if localtime.tm_isdst > 0:
			#add an hour to that shit!
			t+=3600
			localtime = time.localtime(t)
		return localtime

	def xmlentities(self,data):
		data = data.replace("&", "&amp;")
		data = data.replace("<", "&lt;")
		data = data.replace("\"", "&quot;")
		data = data.replace(">", "&gt;")
		return data

	def get_dent_data(self,status):
		#make dict to hold the data
		dict={}
		dict['status_id'] = int(self.get_node_text(status,"id") )
		dict['name'] = self.get_node_text(status,"name")
		dict['screen_name']=self.get_node_text(status,"screen_name")
		dict['text']=self.get_node_text(status,"text")
		dict['in_reply_to_screen_name']=self.get_node_text(status,"in_reply_to_screen_name")
		dict['profile_image_url']=self.get_node_text(status,"profile_image_url")
		dict['source']=self.get_node_text(status,"source")
		dict['favorited']=self.get_node_text(status,"favorited")
		#what server is this shit from?
		profile_url = self.get_node_text(status,"statusnet:profile_url")
		dict['profile_url'] = profile_url
		# we should clean the source ( if there is one )
		if dict['source']!=None:
			dict['source']=self.re_source_sub.sub( '', dict['source'])
		created=self.get_node_text(status,'created_at')
		#strip the zone because this is fucking bullshit
		lt = self.fix_the_fucking_date(created)
		#what about DST?#fuck DST move to relative time
		#format the time		
		dict['time']=time.asctime(lt)
		#is this in reply to some shit?
		in_reply_to_id_str=self.get_node_text(status,'in_reply_to_status_id')
		#this may be a retweet
		retweet_nodes = status.getElementsByTagName('retweeted_status')
		if len(retweet_nodes) > 0 :
			in_reply_to_id_str = self.get_node_text( retweet_nodes[0], 'id')

		if in_reply_to_id_str!=None:
				 in_reply_to_id=int(in_reply_to_id_str)
		else:
				 in_reply_to_id=None
		dict['in_reply_to_id']=in_reply_to_id
		return dict
		
	def get_server_config(self, text):
		return_dict = {}
		dom = parseString(text)
		site = dom.getElementsByTagName('site')[0]
		return_dict['textlimit'] = self.get_node_text( site, 'textlimit' )
		return_dict['timezone'] = self.get_node_text( site, 'timezone' )
		return return_dict
