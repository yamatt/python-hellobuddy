#!/usr/bin/env python
'''
copyright 2010 jezra lickter http://www.jezra.net

heybuddy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

heybuddy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with heybuddy.	If not, see <http://www.gnu.org/licenses/>.
'''
import gc
gc.enable()
import gtk,gobject
import sys, os
import gettext
import webbrowser
locale_dir = os.path.join(
	os.path.dirname( os.path.realpath(__file__) ),
	'locales')

gettext.bindtextdomain('heybuddy', locale_dir)
gettext.textdomain('heybuddy')
gettext.install('heybuddy', locale_dir)
_ = gettext.gettext
from xml.dom.minidom import parse, parseString
import re
import time
import subprocess
#this might be on Maemo
from PlatformSpecific import has_hildon,links_unavailable
#what are the custom classes that I need?
from Communicator import Communicator
from Configuration import Configuration
from XMLProcessor import XMLProcessor
from ImageCache import ImageCache
from StatusIcon import StatusIcon
from GroupPage import GroupPage
from About import About
from SettingsPage import SettingsPage
import MainWindow
#from FilterPage import *
from DentScroller import DentScroller
from UserPage import UserPage
from ScrollPage import ScrollPage
from Dent import Dent
from ContextPage import ContextPage
#for notifications
from Notify import Notify, has_pynotify, notifier_reads_markup
#this might be on Maemo
try:
	import hildon
	has_hildon = True
except:
	has_hildon = False
	
global app_name
global version
global branch
app_name = 'heybuddy'
version = '0.2.3'
branch="testing: 295"

#make a fake enumeration
DENT,MENTION,DIRECT,CONTEXT,USER,GROUP,ACCOUNT,ABOUT = range(8)
#keep track of high ids
highest_id={ "dent":0,
	"dent_previous":0,
	"mention":0,
	"mention_previous":0,
	"direct":0,
	"direct_previous":0
}

class application :
	def __init__(self):
		#init threading
		gobject.threads_init()
		#keep track of the window size
		self.window_height=0
		self.window_width=0
		self.window_is_hidden = False
		self.has_status_icon = False
		#keep track of the initial conversation id so that conversations don't colide
		self.conversation_id="0"
		#keep track of the filters
		self.filters ={'users':[],'strings':[]}
		self.options={'run_as_tray_app':False,'context_backwards':False,'no_avatars':False,'notifications':True,'notify_replies':False}
		#keep track of the direct_message requests
		self.last_direct_message_time=0
		#something something direct message
		self.is_direct_message_mode=False
		self.direct_message_to=None
		self.waiting_requests=0
		self.is_first_dents = True
		#keep track of the respond to id
		self.respond_to_id=0
		self.pre_group_page=None
		self.pre_user_page=None
		#keep track of the last time statuses where pulled
		self.last_get_statuses = 0
		#what are the assets?
		asset_dir = 'assets'
		heybuddy_dir = os.path.dirname( os.path.realpath( __file__ ) )
		self.readme_file = os.path.join(heybuddy_dir,'README.txt')
		self.standard_icon_path = os.path.join(heybuddy_dir,asset_dir,'icon.png')
		self.direct_icon_path = os.path.join(heybuddy_dir,asset_dir,'direct_icon.png')
		self.networking_icon_path = os.path.join(heybuddy_dir,asset_dir,'icon1.png')
		self.throbber_icon_path = os.path.join(heybuddy_dir,asset_dir,'throbber.gif')
		self.default_icon_path = self.standard_icon_path
		self.conf = Configuration(app_name)
		#has the account info been authenticated?
		self.credentials_verified = self.conf.get_bool('access', 'credentials_verified')
		self.xmlprocessor = XMLProcessor()
		#create a regex to replace parts of a dent
		self.regex_tag = re.compile("(^| )#([\w-]+)", re.UNICODE)
		self.regex_group = re.compile("(^| )!([\w-]+)")
		self.regex_user=re.compile("(^|[^A-z0-9])@(\w+)")
		self.regex_url=re.compile("(http[s]?://.*?)(\.$|\. |\s|$)",re.IGNORECASE)
		#get the initial dents
		self.initial_dents = self.conf.get('settings','initial_dents',default='20' )
		self.dent_limit = int(self.initial_dents)*2
		#get the pull time
		self.pull_time = self.conf.get('settings','pull_time',default='60')
		self.pull_time_changed_bool = False
		self.pull_time_mentions = False
		#build the gui
		self.build_gui()
		
		#where is the certs file?
		ca_certs_files = [
			"/etc/ssl/certs/ca-certificates.crt",
			"/etc/ssl/certs/ca-bundle.crt",
			]
		#what if there isn't a cert_file
		cert_file=None
		#determine the certs_file
		for f in ca_certs_files:
			if os.path.exists(f):
				cert_file=f
				break	
		
		#create the communicator
		self.comm = Communicator(app_name, cert_file)
		self.comm.connect('statusesXML',self.process_statusesXML,self.dentspage)
		self.comm.connect('mentionsXML',self.process_statusesXML,self.mentionspage)
		self.comm.connect('favoritesXML', self.process_statusesXML,self.favoritespage)
		self.comm.connect('group-statusesXML',self.process_statusesXML,self.grouppage)
		self.comm.connect('user-statusesXML',self.process_statusesXML,self.userpage)
		self.comm.connect('direct_messagesXML',self.process_statusesXML,self.directspage,True)
		self.comm.connect('conversationXML',self.process_conversationXML)
		self.comm.connect('userXML',self.process_userXML)
		self.comm.connect('groupXML',self.process_groupXML)
		self.comm.connect('new-statusXML',self.process_new_statusXML)
		self.comm.connect('redent-statusXML',self.process_new_statusXML)
		self.comm.connect('user_is_friendXML',self.process_user_is_friendXML)
		self.comm.connect('user_is_memberXML',self.process_user_is_memberXML)
		self.comm.connect('friendshipXML',self.process_friendshipXML)
		self.comm.connect('exception-caught',self.process_communication_exception)
		self.comm.connect('widget-image',self.process_widget_image)
		self.comm.connect('direct-messageXML',self.process_new_directXML)
		self.comm.connect('verify_credentialsXML',self.process_verifycredentialsXML)
		self.comm.connect('configXML',self.process_configXML)
		#create an image cacher thingy
		self.imagecache = ImageCache()
		self.imagecache.set_disabled( self.conf.get_bool_option('no_avatars') )
		self.imagecache.connect('get-widget-image', self.get_widget_image)
	
		#Create notify-er if has pynotify
		if has_pynotify:
			self.notify = Notify()

		#align the window
		self.align_window()
		# do we need to create the status icon
		if self.conf.get_bool_option('run_as_tray_app'):
			self.create_status_icon()
		
	def build_gui(self):
		#build the GUI 
		self.mainwindow=MainWindow.MainWindow(app_name,version,branch)
		try:
			self.mainwindow.set_icon_from_file(self.default_icon_path)
		except:
			pass
		self.mainwindow.set_textlimit( self.conf.textlimit() )	
		self.mainwindow.set_ctrl_enter( self.conf.get_bool_option('ctrl_enter') )
		self.mainwindow.connect('quit', self.quit_triggered )
		self.mainwindow.connect('window-to-tray', self.window_to_tray )
		self.mainwindow.connect('update-status',self.update_status)
		self.mainwindow.connect('get-conversation',self.get_conversation)
		self.mainwindow.connect('show-user',self.get_user_info)
		self.mainwindow.connect('show-group',self.get_group_info)
		self.mainwindow.connect('notebook-page-change',self.page_change)
		self.mainwindow.connect('follow-user',self.follow_user)
		self.mainwindow.connect('join-group',self.join_group)
		self.mainwindow.connect('clear-respond-to-id',self.clear_respond_to_id)
		#keep track of the window size
		self.mainwindow.connect('size-allocate', self.window_size_allocate)
		#self.mainwindow.connect('window-state-event', self.mainwindow_state_event)
		self.mainwindow.connect('delete-event', self.mainwindow_delete_event)
		
		# local function to create a closeable tab label for closeable tabs
		def closeable_tab_label(caption, tab):
			tablabel = gtk.HBox(False,2)
			tablabel.pack_start(gtk.Label(caption),False,False,0)
			closebutton = gtk.Button()
			closeicon = gtk.Image()
			closeicon.set_from_stock(gtk.STOCK_CLOSE,gtk.ICON_SIZE_MENU)
			closebutton.set_image(closeicon)
			closebutton.set_relief(gtk.RELIEF_NONE)
			tinybutton_style = gtk.RcStyle()
			tinybutton_style.xthickness = 0
			tinybutton_style.ythickness = 0
			closebutton.modify_style(tinybutton_style)
			if tab != None:	# if this isn't a mock-add
				closebutton.connect('clicked',tab.close)
			#don't show a tooltip on maemo
			if not has_hildon:
				closebutton.set_tooltip_text(_("Close"))
			tablabel.pack_start(closebutton,False,False,0)
			tablabel.show_all()
			return tablabel

		# do a mock add of dentspage, with a close label, so as to determine height needed for uncloseable tabs' labels, then break it all down again
		# this is ridiculously hacky, but it works, and doesn't leave anything behind
		self.dentspage = ScrollPage()
		self.mock_label = closeable_tab_label(_("Dents"),None)
		self.mainwindow.notebook.append_page(self.dentspage,self.mock_label)
		self.mainwindow.show_all() # we have to do this so the tab gets actualised, and thus gets a height
		min_tab_height = self.mock_label.allocation.height
		self.mainwindow.hide_all()
		self.mainwindow.notebook.remove_page(-1)
		del self.mock_label
		
		# local function to create a label the same height as the closeable tabs' labels
		def uncloseable_tab_label(caption):
			tablabel = gtk.Label(caption)
			tablabel.set_size_request(-1,min_tab_height)
			tablabel.show()
			return tablabel
		
		# create and add all of the pages
		self.dentspage = ScrollPage()
		self.mainwindow.notebook.append_page(self.dentspage,uncloseable_tab_label(_("Dents") ) )
		
		self.mentionspage = ScrollPage()
		self.mainwindow.notebook.append_page(self.mentionspage,uncloseable_tab_label(_("Mentions")) )

		self.favoritespage = ScrollPage()
		self.mainwindow.notebook.append_page(self.favoritespage,uncloseable_tab_label(_("Favorites")) )
		
		self.directspage = ScrollPage()
		self.mainwindow.notebook.append_page(self.directspage,uncloseable_tab_label(_("Directs")) )
		
		#make the conversation page
		self.contextpage=ContextPage()
		self.contextpage.connect('context-page-hide',self.hide_contextpage)
		#add the contextpage
		context_label = closeable_tab_label(_("Context"), self.contextpage)
		self.mainwindow.notebook.append_page(self.contextpage, context_label)
		
		#create a user page
		self.userpage=UserPage()
		self.userpage.connect('user-page-hide',self.hide_userpage)
		self.userpage.connect('follow-user',self.follow_user)
		self.userpage.connect('direct-clicked',self.direct_clicked)
		self.userpage.connect('open-link',self.open_link)
		self.userpage.connect('block-create',self.block_create)
		self.userpage.connect('block-destroy',self.block_destroy)
		
		#add the userpage
		user_label = closeable_tab_label(_("User"),self.userpage ) 
		self.mainwindow.notebook.append_page(self.userpage, user_label)
		
		#create a Group page
		self.grouppage=GroupPage()
		self.grouppage.connect('group-page-hide',self.hide_grouppage)
		self.grouppage.connect('join-group',self.join_group)
		self.grouppage.connect('open-link',self.open_link)

		#add the Grouppage
		group_label = closeable_tab_label(_("Group"),self.grouppage ) 
		self.mainwindow.notebook.append_page(self.grouppage, group_label)
		
		#create and add the account page
		self.settingspage = SettingsPage(has_hildon,has_pynotify)
		self.settingspage.set_initial_dents( self.initial_dents )
		self.settingspage.set_pull_time(self.pull_time)
		#update the configuration of the settings
		self.settingspage.connect('update-account',self.update_account)
		self.options['ctrl_enter'] = self.conf.get_bool_option('ctrl_enter')
		self.settingspage.set_ctrl_enter( self.options['ctrl_enter']	)
		self.options['run_as_tray_app'] = self.conf.get_bool_option('run_as_tray_app')
		self.settingspage.set_run_as_tray_app( self.options['run_as_tray_app']	)
		self.options['context_backwards']	= self.conf.get_bool_option('context_backwards')
		self.settingspage.set_context_backwards( self.options['context_backwards'] )
		self.options['no_avatar']= self.conf.get_bool_option('no_avatars')
		self.settingspage.set_no_avatars( self.options['no_avatar'] )
		self.options['api_retweet'] = self.conf.get_bool_option('api_retweet')
		self.settingspage.set_api_retweet( self.options['api_retweet']	)
		self.options['notifications']= self.conf.get_bool_option('notifications')
		self.settingspage.set_notifications( self.options['notifications'] )
		self.options['notify_replies']= self.conf.get_bool_option('notify_replies')
		self.settingspage.set_notify_replies( self.options['notify_replies'] )
		link_color = self.conf.get('settings','link_color',default='blue')
		self.settingspage.set_link_color( link_color )
		self.theme_link_color(link_color)
		#connect the setting signals
		self.settingspage.connect('option-run-as-tray-app', self.option_changed, 'run_as_tray_app')
		self.settingspage.connect('option-ctrl-enter', self.option_changed, 'ctrl_enter')
		self.settingspage.connect('option-context-backwards',self.option_changed, 'context_backwards')
		self.settingspage.connect('option-no-avatars',self.option_changed, 'no_avatars')
		self.settingspage.connect('option-api-retweet', self.option_changed, 'api_retweet')
		self.settingspage.connect('option-notifications',self.option_changed, 'notifications')
		self.settingspage.connect('option-notify-replies',self.option_changed, 'notify_replies')
		self.settingspage.connect('initial-dents',self.set_initial_dents)
		self.settingspage.connect('pull-time',self.set_pull_time)
		self.settingspage.connect('link-color',self.set_link_color)
		self.settingspage.connect('add-string-filter', self.add_string_filter )
		self.settingspage.connect('remove-string-filter', self.remove_string_filter )
		self.settingspage.connect('add-user-filter', self.add_user_filter )
		self.settingspage.connect('remove-user-filter', self.remove_user_filter )
		#add the settings to the mainwindow
		self.mainwindow.add_notebook_page(self.settingspage,uncloseable_tab_label(_("Settings") ) )
		#create and add the about page
		about = About(version,branch,self.standard_icon_path,self.readme_file)
		about.connect('open-link',self.open_link)
		self.mainwindow.add_notebook_page( about, uncloseable_tab_label(_("About") ) )
		self.mainwindow.show_some()
		#hide some stuff
		self.grouppage.hide_all()
		self.userpage.hide_all()
		self.contextpage.hide_all()
		
	def align_window(self):
		#try to set the mainwindows size based on conf info
		try:
			w = int( self.conf.get('window_info','width') )
			h = int( self.conf.get('window_info','height') )
			self.mainwindow.resize(w,h)
		except:
			pass
		try:
			x = int( self.conf.get('window_info','x') )
			y = int( self.conf.get('window_info','y') )
			self.mainwindow.move(x,y)
		except:
			pass
		
		#get the filters
		try: 
			#read the filters
			filters = self.conf.get('settings','filters',True)
			#the filters should be an array
			if len(filters):
				#self.filters = filters
				self.filters['users']	= filters['users']
				self.filters['strings']	= filters['strings']
				#set the filters
				self.settingspage.set_string_filters( self.filters['strings'] )
				self.settingspage.set_user_filters( self.filters['users'] )
		except:
			pass
	
	def create_status_icon(self):
		if not self.has_status_icon:
			#create the statusicon
			self.statusicon = StatusIcon()
			self.statusicon.connect('activate', self.status_clicked )
			self.statusicon.connect('quit-selected',self.quit_app)
			self.statusicon.set_icon( self.standard_icon_path )
		self.statusicon.set_property("visible",True)
		self.has_status_icon=True
	
	def destroy_status_icon(self):
		self.statusicon.set_property("visible",False)
		self.has_status_icon=False
		
	def update_account(self, widget, n, p, s):
		#check if these are valid
		self.mainwindow.set_message(_("Authenticating account..."))
		self.increment_requests()
		self.comm.verify_credentials(n, p, s)
			
	def increment_requests(self):
		self.waiting_requests+=1
		if self.waiting_requests==1:
			try:
				self.mainwindow.set_icon_from_file(self.networking_icon_path)
			except:
				pass
			try:
				self.mainwindow.set_throbber(self.throbber_icon_path)
			except:
				pass
			if self.has_status_icon:
				self.statusicon.set_icon( self.networking_icon_path)
				
	def decrement_requests(self):
		self.waiting_requests-=1
		if self.waiting_requests==0:
			try:
				self.mainwindow.set_icon_from_file(self.default_icon_path)
			except:
				pass
			try:
				self.mainwindow.set_throbber(self.default_icon_path)
			except:
				pass
			if self.has_status_icon:
				self.statusicon.set_icon( self.default_icon_path )
		if self.waiting_requests<0:
			self.waiting_requests=0
	
	def valid_account_info(self, n, p, s):
		self.conf.name( n )
		self.conf.password( p )
		self.conf.service( s )
		self.conf.save()
		#update the comm
		self.comm.set_name_and_password( n,p )
		self.comm.set_service( s )
		
	def get_statuses(self,count="20"):
		if self.credentials_verified:
			#do some time handling for the good doctor
			now = time.time()
			if now - self.last_get_statuses > 2*self.pull_time:
				count = self.initial_dents
			self.last_get_statuses = now
			self.increment_requests()
			self.comm.get_statuses(count=count, since=highest_id['dent_previous'])
			#clean up the garbage
			gc.collect()
	
	def get_mentions(self,count="20"):
		if self.credentials_verified:
			self.increment_requests()
			self.comm.get_mentions(count=count,since=highest_id['mention_previous'])

	def get_favorites(self):
		if self.credentials_verified:
			self.increment_requests()
			self.comm.get_favorites()
	
	def get_direct_messages(self):
		if self.credentials_verified:
			now = time.time()
			#NOTE this could be changed to 3 minutes just setting it 
			#this way for now
			#has it been 3 times the pull time?
			if now - (3 * int(self.pull_time) ) > self.last_direct_message_time:
				self.increment_requests()
				self.comm.get_direct_messages(highest_id['direct_previous'])	
				self.last_direct_message_time=now
	
	def run(self, enable_logging=False):
		self.logging = enable_logging
		#start the communicator
		self.comm.start()
		self.main_loop = gobject.MainLoop()
		
		#we have to temporarily show the various pages or nothing works
		''' why the fuck do I need to do this? '''
		self.mainwindow.set_notebook_page(DIRECT)
		self.mainwindow.set_notebook_page(MENTION)
		self.mainwindow.set_notebook_page(DENT)
		#send the service to the settings page
		self.settingspage.set_service(self.conf.service() )
		#did the conf read a name and password?
		if( self.conf.name() !="" and self.conf.password()!=""):
			if self.credentials_verified:
				self.comm.set_name_and_password( self.conf.name(),self.conf.password() )
				self.comm.set_service( self.conf.service() )
				#fill the Account tab name/pw fields to show the user that they're logged in
				self.settingspage.set_name(self.conf.name())
				self.settingspage.set_password(self.conf.password())
				#add a function to the main loop
				gobject.timeout_add(int(self.pull_time)*1000, self.update_statuses )
				gobject.timeout_add(int(self.pull_time)*1500, self.update_mentions )
				#add a timout to get dents
				gobject.timeout_add(500,self.get_statuses,self.initial_dents )
				gobject.timeout_add(600,self.get_mentions,self.initial_dents )
			#gobject.timeout_add(1000,self.get_direct_messages )
		else:
			#set the focus on the account page; the last page
			self.mainwindow.set_notebook_page(ACCOUNT)
		
		self.mainwindow.run()
		self.main_loop.run()
		#if we ever get here, we should quit

	def update_statuses(self):
		self.get_statuses()
		if(self.pull_time_changed_bool):
			self.pull_time_changed_bool= False
			gobject.timeout_add(int(self.pull_time)*1000, self.update_statuses)
			return False
		return True
	
	def update_mentions(self):
		self.get_mentions()
		if(self.pull_time_mentions):
			self.pull_time_mentions=False
			gobject.timeout_add(int(self.pull_time)*1500, self.update_mentions)
			return False
		return True
	
	def update_direct_messages(self):
		self.get_direct_messages()
		return True
	
	def update_status(self,widget,text):
		self.increment_requests()
		#remove newlines from text
		text=text.replace("\n","")
		#is this direct message mode?
		if self.is_direct_message_mode:
			self.comm.send_direct_message(text,self.direct_message_to)
			self.set_is_direct_message_mode(False)
		else:
			self.comm.send_update_status(text,self.respond_to_id)
		self.clear_respond_to_id()
		
	def quit_app(self,widget=None):
		#quit the communicator loop
		self.comm.quit()
		#quit the main loop
		self.main_loop.quit()
		
	def get_widget_image(self,imagecache,image):
		self.comm.get_widget_image(image)
	
	def get_conversation(self,id,conversation_id):
		if self.credentials_verified:
			self.increment_requests()
			self.comm.get_conversation(id,conversation_id)
	
	def parse_profile(self, profile=None, name=None ):
		#is this a remote user?
		remote_user = True
		service = ''
		#did we get a name?
		if profile!=None:
			bits = profile.rsplit("/")
			service = bits[2]
			if name==None:
				name = bits[3]
				#if there is no name, use the first subdomain as a name
				if name==None:
					dot_split = service.split(".")
					name = dot_split[0]
			if service==self.conf.service():
				remote_user = False
		else:
			remote_user = False
		return {'service':service, 'remote':remote_user,'name':name}
	
	def get_user_info(self, profile=None, name=None):
		#parse the info
		result = self.parse_profile( profile, name )
		#is this a remote user?
		remote_user = result['remote']
		name = result['name']
		service = result['service']
		
		#is this not a remote user?
		if not remote_user:
			if self.credentials_verified:
				self.increment_requests()
				self.comm.get_user_info(name)
				self.increment_requests()
				self.comm.get_user_statuses(name)
			return
	
		self.increment_requests()
		self.comm.get_remote_user_info(service,name)
		self.increment_requests()
		self.comm.get_remote_user_statuses(service,name)
		
	
	def get_group_info(self,name):
		if self.credentials_verified:
			self.increment_requests()
			self.comm.get_group_info(name)
	
	def follow_user(self,widget,name,bool):
		if self.credentials_verified:
			if bool:
				self.comm.friendship_create(name)
			else:
				self.comm.friendship_destroy(name)
	
	def join_group(self,widget,name,bool):
		if self.credentials_verified:
			if bool:
				self.comm.group_join(name)
			else:
				self.comm.group_leave(name)
	
	def process_friendshipXML(self,widget,text):
		pass
	
	def page_change(self,widget,old_id,new_id):
		if new_id==MainWindow.DIRECT:
			self.get_direct_messages()
		else:
			if self.is_direct_message_mode:
				self.set_is_direct_message_mode(False)
		#should we clear any warning message?
		self.mainwindow.clear_message()
	
	def process_userXML(self,comm,text):
		self.decrement_requests()
		data = self.xmlprocessor.get_user_info(text)
		if data['profile_image_url']!=None:
			self.imagecache.add_image_to_widget(data['profile_image_url'],self.userpage)
		self.userpage.set_user_data(data)
	
	def process_groupXML(self,comm,text):
		self.decrement_requests()
		data = self.xmlprocessor.get_group_info(text)
		if data['stream_logo']!=None:
			self.imagecache.add_image_to_widget(data['stream_logo'],self.grouppage)
		'''#is this user a member of this group
		self.increment_requests()
		self.comm.get_user_is_member(data['id'])'''
		self.increment_requests()
		self.comm.get_group_statuses(data['id'])
		self.grouppage.set_group_data(data)
	
	def process_user_is_friendXML(self,comm,text):
		self.decrement_requests()
		is_friend = self.xmlprocessor.get_user_is_friend(text)
		self.mainwindow.display_user_is_friend( is_friend )
	
	def process_user_is_memberXML(self,comm,text):
		self.decrement_requests()
		is_member = self.xmlprocessor.get_user_is_member(text)
		self.mainwindow.display_user_is_member( is_member )
	
	def process_new_directXML(self,comm,text):
		#a update status was sent
		self.decrement_requests()
		#clear the textview thing
		self.mainwindow.emit_update_textview_responsed()
	
	def process_new_statusXML(self,comm,text):
		#a update status was sent
		self.decrement_requests()
		#clear the textview thing
		self.mainwindow.emit_update_textview_responsed()
		#there is one status and it is the DOM
		status = self.xmlprocessor.get_dom(text)
		data = self.xmlprocessor.get_dent_data(status)
		data['markup'] = self.markup_dent_text(data['text'])
		#add the dent
		dent = self.connect_dent(data,self.dentspage)

	def process_verifycredentialsXML(self, object, text, data):
		#actually, if we are here, the authorization worked!
		self.conf.set('access', 'credentials_verified', True)
		self.credentials_verified = True
		self.mainwindow.message_label.hide()
		(n, p, s) = data
		self.valid_account_info(n, p, s)
		#get the config
		self.comm.get_config()
		#switch to the dents page
		self.mainwindow.set_notebook_page(DENT) 
		self.get_statuses()
		self.get_mentions()

	def process_conversationXML(self,object,text,conversation_id):
		self.decrement_requests()
		#is this the current conversation Id? if not, then do nothing
		#convert to int because there is a problem with string comparison
		'''is one of the strings unicode?'''
		if int(self.conversation_id)==int(conversation_id):
			#get the status
			status = self.xmlprocessor.get_dom(text)
			data = self.xmlprocessor.get_dent_data(status)
			data['markup']=self.markup_dent_text(data['text'])
			#since this is a conversation, we can get rid of the in_reply_to_screen_name
			data['in_reply_to_screen_name']=None
			#tell the mainWindow to add the dent
			dent = self.connect_dent(data,self.contextpage,True, self.options['context_backwards'] )
			if data['in_reply_to_id']!=None:
				#recursively get in_reply_to_ids
				self.get_conversation(id=data['in_reply_to_id'],conversation_id=conversation_id)

	def process_configXML(self, object, text):
		self.decrement_requests()
		server = self.xmlprocessor.get_server_config(text)
		print server
		self.conf.textlimit( server['textlimit'] )
		self.conf.save()
		self.mainwindow.set_textlimit( server['textlimit'] )

	def connect_dent(self,data,target_page,is_conv=False,conv_backwards=False,is_direct_dent=False):
		#make the dent
		dent = Dent(data,is_direct=is_direct_dent)
		if target_page.dentScroller.add_dent( dent, is_conv, conv_backwards ):
			dent.connect('group-clicked', self.view_group)
			dent.connect('reply-clicked', self.reply_clicked)
			dent.connect('direct-clicked', self.direct_clicked)
			dent.connect('view-conversation-clicked', self.view_conversation)
			dent.connect('user-clicked', self.view_user_name)
			dent.connect('profile-clicked', self.view_user_profile)
			dent.connect('id-clicked', self.view_id)
			dent.connect('text-label-clicked',self.dent_text_clicked)
			dent.connect('redent-clicked',self.redent_clicked)
			dent.connect('favorite-clicked',self.favorite_clicked)
			dent.connect('unfavorite-clicked',self.unfavorite_clicked)
			dent.connect('open-link',self.open_link)
			if target_page!=self.userpage:
				#get the image for this dent
				self.imagecache.add_image_to_widget(data['profile_image_url'],dent)
			return True
		else:
			dent.destroy()
			del dent
			return False
			
	def reply_clicked(self,dent,name):
		#set the text buffer
		self.mainwindow.update_textbuffer.set_text("@%s " % (name) )
		self.mainwindow.update_textview.grab_focus()
		#set the respond_to_id
		self.respond_to_id=dent.id

	
	def favorite_clicked(self,dent):
		id=dent.id
		self.comm.favorite(id)
	
	def unfavorite_clicked(self,dent):
		id=dent.id
		self.comm.unfavorite(id)
	
	def direct_clicked(self,widget,name):
		self.direct_message_to = name
		if type(widget).__name__=="Dent":
			self.respond_to_id=widget.id
		else:
			self.respond_to_id=None
		self.set_is_direct_message_mode(True,name)
		#we should be on the directs page
		self.mainwindow.set_notebook_page(DIRECT)
		#set the text buffer
		self.mainwindow.update_textbuffer.set_text("")
		self.mainwindow.update_textview.grab_focus()
	
	def view_conversation(self,dent,id):
		self.conversation_id=id
		self.pre_context_page=self.mainwindow.notebook_current_page
		self.contextpage.dentScroller.clear()
		self.contextpage.show_all()
		#get conversation starting with id
		self.get_conversation(id,id)
		self.mainwindow.notebook.set_current_page(CONTEXT)
		
	def view_user_profile(self, widget, profile_url, screen_name):
		self.get_user_info(profile=profile_url, name=screen_name)
		#self.get_user_info(screen_name)
		self.pre_user_page=self.mainwindow.notebook_current_page
		#make the user page checkbox insensitive
		self.userpage.disable()
		#show the page 
		self.userpage.show_all()
		#rehide its collapsed widgetbox, that doesn't need to be visible yet
		self.userpage.widgetbox_collapsed.hide()
		#clear the userpage stuff
		self.userpage.clear()
		#change to the user page
		self.mainwindow.set_notebook_page(USER)
			
	def view_id(self, widget, id):
		url = 'http://%s/notice/%s' % (self.conf.service(), id)
		self.open_link(None, url)
		
	def view_user_name(self, widget, screen_name):
		#TODO: merge this function with view_user_profile
		self.get_user_info(name=screen_name)
		#self.get_user_info(screen_name)
		self.pre_user_page=self.mainwindow.notebook_current_page
		#make the user page checkbox insensitive
		self.userpage.disable()
		#show the page 
		self.userpage.show_all()
		#rehide its collapsed widgetbox, that doesn't need to be visible yet
		self.userpage.widgetbox_collapsed.hide()
		#clear the userpage stuff
		self.userpage.clear()
		#change to the user page
		self.mainwindow.set_notebook_page(USER)	
			
	#does this function even get called? get rid of it
	def get_dent_time(self,text):
		#print text
		pass
		
	def markup_dent_text(self,text,is_notification=False):
		#process the text to markup
		#xmlencode the string
		text = self.xmlprocessor.xmlentities(text)
		#regex find the highlights
		markup = self.regex_tag.sub(r'\1#<b>\2</b>',text)
		#regex find users
		if has_hildon or links_unavailable or is_notification:
			markup = self.regex_group.sub(r'\1!<b>\2</b>',markup)
			markup = self.regex_user.sub(r'\1@<b>\2</b>',markup)
		else:
			#find urls
			markup = self.regex_url.sub(r'<a href="\1">\1</a>\2',markup)
			markup = self.regex_user.sub(r'\1@<a href="@\2">\2</a>',markup)
			markup = self.regex_group.sub(r'\1!<a href="!\2">\2</a>',markup)
		return markup
	
	def process_statusesXML(self,object,text,target_page,is_direct=False):
		#based on the target, what is the counting thingy?
		count_ref=None
		if target_page==self.dentspage:
			count_ref = "dent"
		elif target_page==self.mentionspage:
			count_ref = "mention"
		elif target_page==self.directspage:
			count_ref = "direct"
		self.decrement_requests()
		#set the "previous" count ref, do this now and get data twice
		if count_ref!=None:
			highest_id[count_ref+"_previous"] = highest_id[count_ref]
		#get a list of the statuses
		statuses = self.xmlprocessor.get_statuses(text,is_direct)
		#if there aren't any statuses, return
		if len(statuses)==0:
			return
		#reverse the statuses list
		statuses.reverse()
		dent_count=0
		reply_count=0
		#what is the highest id of the target index?	
		for status in statuses:
			filtered_status = False
			data = self.xmlprocessor.get_dent_data(status)

			if target_page==self.dentspage:
				#we should check for filtration
				filtered = self.check_filtered( data )
				filtered_status=filtered[0]
			if not filtered_status:
				#get the markup
				data['markup'] = self.markup_dent_text(data['text'])
				#did this dent connect
				if not self.connect_dent(data,target_page,is_direct_dent=is_direct):
					continue

				#if the target_page = 0 and not first_dents and not is_conf
				if target_page==self.dentspage and not self.is_first_dents:
					if "@"+self.conf.name() in data['markup']:					
						dent=self.connect_dent(data, self.mentionspage )
						reply_count+=1
						if self.options['notify_replies'] and has_pynotify:
							user = data['screen_name']
							#the message shouldn't be marked up if the server doesn't understand markup
							if notifier_reads_markup:
								message = self.markup_dent_text(data['text'],True)
							else:
								message = data['text']
							avatar = self.imagecache.get_image_path(data['profile_image_url'])
							self.notify.notify_reply(user,message,avatar)
					else:
						dent_count+=1
			else:
				self.log("filter #%s %s" %(data['status_id'], filtered[1] ) )
		
		#keep track of the last status_id			
		if count_ref!=None and data!=None:
				highest_id[count_ref]=data['status_id']
				
		self.is_first_dents=False
		#get the related images
		self.imagecache.get_images()
		#do we notify?
		if (dent_count!=0 or reply_count!=0) and has_pynotify and target_page==self.dentspage:
			if self.options['notifications']:
				if not self.options['notify_replies']:
					self.notify.notify_updates_replies(dent_count,reply_count,self.standard_icon_path)
				else:
					if dent_count!=0:
						self.notify.notify_updates(dent_count,self.standard_icon_path)
		#prune off the extra dents
		target_page.dentScroller.prune(self.dent_limit)
		
	def process_widget_image(self,comm,data,name):
		self.imagecache.widget_image_add(data,name)	
		
	def process_communication_exception(self,communicator,code,data,signal=None):
		if self.logging:
			self.log("code:%s, signal:%s" % (code,signal) )
		self.decrement_requests()
		#is there an error message?
		try:
			error_message = self.xmlprocessor.get_error_message(data)
		except:
			error_message = False
		if error_message and not code:
			self.mainwindow.set_message( error_message, MainWindow.ERROR_MESSAGE)
		elif code=='401': 
			#bad authorization
			self.mainwindow.set_notebook_page(MainWindow.ACCOUNT)
			error_message = _("Invalid Authorization: Your name or password is incorrect")
		elif code == '404':
			error_message = _("Service Not Found")
		elif code == '503':
			error_message = _("Service Unavailable")
		elif code == 'unknown error':
			error_message = _("Unknown Error")
		else:
			error_message = code
		#send the error message
		self.mainwindow.set_message(error_message, MainWindow.ERROR_MESSAGE)
		
		#a signal may have been passed from the comm
		if signal == "new-statusXML":
			#a dent was sent but it failed
			self.mainwindow.emit_update_textview_responsed(error=True)
	
	#functions to handle the filtration system
	def add_string_filter(self,winder,string):
		if not string in self.filters['strings']:
			self.filters['strings'].append(string)
			self.filters['strings'].sort()
			self.settingspage.set_string_filters( self.filters['strings'] )
		
	def remove_string_filter(self,winder,string):
		if string in self.filters['strings']:
			self.filters['strings'].remove(string)
			self.settingspage.set_string_filters( self.filters['strings'] )
			
	def add_user_filter(self,winder,user):
		if not user in self.filters['users']:
			self.filters['users'].append(user)
			self.filters['users'].sort()
			self.settingspage.set_user_filters( self.filters['users'] )
		
	def remove_user_filter(self,winder,user):
		if user in self.filters['users']:
			self.filters['users'].remove(user)
			self.settingspage.set_user_filters( self.filters['users'] )
	
	def check_filtered(self,data):
		if len(self.filters['users'])!=0 :
			#filter against the user
			for user in self.filters['users']:
				if data['screen_name'].lower()==user.lower():
					return (True, "user: %s" % data['screen_name'] )
		
		if len(self.filters['strings'])!=0:
			#filter against the strings
			#get the dent text
			text = data['text']
			#loop through the filter strings
			for string in self.filters['strings']:
				if re.search(string,text, flags=re.IGNORECASE):
					return (True, "string: %s" % string )
		#if we get this far, just return
		return (False, None)		
	
	def status_clicked(self,widget):
		if self.window_is_hidden==True:
			self.window_is_hidden=False
			self.mainwindow.show()
			self.align_window()
			self.mainwindow.present()
		else:
			self.window_to_tray(widget)

	def window_size_allocate(self,widget,size):
		self.window_width = size[2]
		self.window_height = size[3]
			
	def save_app_info(self):
		#save the filters
		self.conf.set('settings','filters', self.filters ,True)
		#save the window info
		self.conf.set('window_info','width', self.window_width )
		self.conf.set('window_info','height', self.window_height )
		try:
			#some themes don't pass root origin?
			origin = self.mainwindow.window.get_root_origin()
			self.window_x = origin[0]
			self.window_y = origin[1]
			self.conf.set('window_info','x', self.window_x )
			self.conf.set('window_info','y', self.window_y )
		except:
			pass
		self.conf.save()
		
	def mainwindow_delete_event(self,window,event=None):
		self.save_app_info()
		#are we in tray mode?
		if self.conf.get_bool_option('run_as_tray_app') or self.has_status_icon:
			#is the status icon embedded?
			if self.statusicon.is_embedded():
				self.window_is_hidden=True
				self.mainwindow.hide_on_delete()
				#do not propogate the signal
				return True
		else:
			#we need to quit
			self.quit_app()
			
	def quit_triggered(self,widget):
		self.save_app_info()
		self.quit_app()
	
	def option_changed(self,widget,value,option):
		#save the option change in the configuration
		self.conf.set('options',option,value)
		self.options[option]=value
		self.conf.save()
		#is this the run_tray_app:
		if option=='run_as_tray_app':
			if value:
				self.create_status_icon()
			else:
				self.destroy_status_icon()
		elif option=='no_avatars':
			self.imagecache.set_disabled(value)
		elif option=='ctrl_enter':
			self.mainwindow.set_ctrl_enter(value)
		 
	def redent_clicked(self,dent,name,text):
		if self.options['api_retweet']:
			self.comm.send_redent(dent.id)
		else:
			self.respond_to_id=dent.id
			#formatted_text= u'\u267A @%s: %s' % (name,text)
			formatted_text= u'\u267A @%s: %s' % (name,text)
			self.mainwindow.update_textbuffer.set_text(formatted_text )
			self.mainwindow.update_textview.grab_focus()
	 
	def view_group(self,widget,group_name):
		#where were we?
		self.pre_group_page=self.mainwindow.notebook_current_page
		#make some flags
		self.grouppage.joined_checkbutton.set_sensitive(False)
		#make the grouppage visible
		self.grouppage.show_all()
		#rehide its collapsed widgetbox, that doesn't need to be visible yet
		self.grouppage.widgetbox_collapsed.hide()
		#clear the grouppage
		self.grouppage.clear()
		#switch to the group page
		self.mainwindow.set_notebook_page(GROUP)
		#get the group info
		self.get_group_info(group_name)

	def hide_contextpage(self,widget):
		#end any conversation in progress
		self.conversation_id="0"
		self.mainwindow.set_notebook_page( self.pre_context_page )
		self.contextpage.hide()

	def hide_grouppage(self,widget):
		self.mainwindow.set_notebook_page( self.pre_group_page )
		self.grouppage.hide()

	def hide_userpage(self,widget):
		self.mainwindow.set_notebook_page( self.pre_user_page )
		self.userpage.hide()

	def dent_text_clicked(self,dent,text_label):
		self.mainwindow.last_clicked_label = text_label

	def clear_respond_to_id(self,widget=None):
		self.respond_to_id=0
		
	def set_initial_dents(self,widget,value):
		self.initial_dents=value
		self.dent_limit = int(self.initial_dents)*2
		self.conf.set('settings','initial_dents',value)
		
		
	def set_pull_time(self, widget,value):
		"""A method for setting the time between pulls. obvious comment
		is obvious. Very possible everything will die now that I've added
		this. 
		--Muel Kiel (aka samsnotunix)"""
		self.pull_time=value
		self.conf.set('settings','pull_time',value)
		self.pull_time_changed_bool = True
		self.pull_time_mentions = True
	
	def set_link_color(self,widget,string):
		self.conf.set('settings','link_color',string)
		self.theme_link_color(string)
		
	def theme_link_color(self,color):
		style='''
		style "label" {
			GtkLabel::link-color="%s"
		}
		widget_class "*GtkLabel" style "label"
		''' % (color)
		gtk.rc_parse_string(style)
		#fuck you GTK for not make this work, more than once!
	
	#functions for blocking/unblocking
	def block_create(self,widget,user_id):
		self.comm.block_create(user_id)
		
	def block_destroy(self,widget,user_id):
		self.comm.block_destroy(user_id)
		
		
	def set_is_direct_message_mode(self,mode,user=None):
		self.is_direct_message_mode=mode
		self.mainwindow.set_is_direct_message_mode(mode,user)
		if mode:
			self.default_icon_path=self.direct_icon_path
		else:
			self.default_icon_path=self.standard_icon_path
		#if we aren't waiting on any requests, swap the graphic
		if self.waiting_requests==0:
			try:
				self.mainwindow.set_icon_from_file(self.default_icon_path)
			except:
				pass
			try:
				self.mainwindow.set_throbber(self.default_icon_path)
			except:
				pass
			
	def simple_decrement(self,text=None,data=None):
		self.decrement_requests()

	'''
	function window_to_tray
	sets the run_as_tray_app to true and minimizes the app
	'''
	def window_to_tray(self,window):
		if self.options['run_as_tray_app']:
			self.mainwindow_delete_event(window)
			
			
	def open_link(self, widget, uri):
		webbrowser.open(uri)
		return True
		'''
		command = "xdg-open '%s'" % ( uri )
		#print command
		subprocess.Popen(command,shell=True)
		return True
		'''

	def log(self,string):
		if self.logging:
			now = time.strftime("%H:%M:%S")
			file = os.path.join( os.path.expanduser("~"),"heybuddy.log")
			f = open(file,'a')
			f.write("%s %s\n" % (now,string) )
			f.close() 

if(__name__=="__main__"):
	try:
		enable_logging = (sys.argv[1]=='--enable-logging')
	except:
		enable_logging = False
	a = application()
	a.run(enable_logging)
