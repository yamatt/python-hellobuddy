'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import gtk
import gobject
import PlatformSpecific
from FilterFrame import FilterFrame

class SettingsPage(gtk.VBox,gobject.GObject):
	__gsignals__={
		'update-account': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
			),
		'option-run-as-tray-app': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_BOOLEAN,)
		),
		'option-api-retweet': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_BOOLEAN,)
		),
		'option-ctrl-enter': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_BOOLEAN,)
		),
		'option-context-backwards': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_BOOLEAN,)
		),
		'option-no-avatars': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_BOOLEAN,)
		),
		'option-notifications':(
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_BOOLEAN,)
		),
		'option-notify-replies':(
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_BOOLEAN,)
		),
		'initial-dents': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_INT,)
		),
		'pull-time': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_INT,)
		),
		'link-color': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_STRING,)
		),
		'add-string-filter': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_STRING,)
		),
		'remove-string-filter' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				(gobject.TYPE_STRING,)
		),
		'add-user-filter': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_STRING,)
		),
		'remove-user-filter' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				(gobject.TYPE_STRING,)
		)
	}
	
	def __init__(self,has_hildon=False,has_pynotify=False):
		self.has_hildon=has_hildon
		gtk.VBox.__init__(self)
		gobject.GObject.__init__(self)
		self.set_homogeneous(False)
		self.set_border_width(5)
		#make this a scrollable thing
		vbox = gtk.VBox(False)
		scroller = PlatformSpecific.ScrollThingy()
		#put the vbox in a view port
		vport = gtk.Viewport()
		vport.set_shadow_type(gtk.SHADOW_NONE)
		vport.add(vbox)
		#add the vport to the scrollthingy
		scroller.add(vport)
		self.pack_start(scroller)
		
		#start with a table
		table = gtk.Table(4,2)
		table.attach(gtk.Label(_("Name:")),0,1,0,1,gtk.SHRINK,gtk.SHRINK)
		table.attach(gtk.Label(_("Password:")),0,1,1,2,gtk.SHRINK,gtk.SHRINK)
		table.attach(gtk.Label(_("Service:")),0,1,2,3,gtk.SHRINK,gtk.SHRINK)
		self.account_name_entry = gtk.Entry()
		self.account_password_entry = gtk.Entry()
		self.account_password_entry.set_invisible_char("*")
		self.account_password_entry.set_visibility(False)
		self.account_apiroot_entry = gtk.Entry()
		#add the entries to the table
		table.attach(self.account_name_entry,1,2,0,1,gtk.SHRINK,gtk.SHRINK)
		table.attach(self.account_password_entry,1,2,1,2,gtk.SHRINK,gtk.SHRINK)
		table.attach(self.account_apiroot_entry,1,2,2,3,gtk.SHRINK,gtk.SHRINK)
		#make a button to register "submit clicks
		enter_button = gtk.Button(_("Submit"))
		enter_button.connect('clicked', self.submit_clicked)
		#attach the button to the table
		table.attach(enter_button,1,2,3,4,gtk.SHRINK,gtk.SHRINK)
		account_frame = gtk.Frame(_("Account"))
		account_frame.add(table)
		vbox.pack_start(account_frame,False,False,0)
		#add the options settings
		options_box = gtk.VBox(False)
		if not has_hildon:
			self.run_as_tray_app = gtk.CheckButton(_("Run as tray application"))
			self.run_as_tray_app.connect('toggled', self.option_toggled,'option-run-as-tray-app')
			options_box.pack_start(self.run_as_tray_app,False,False,0)
		self.context_back_asswards = gtk.CheckButton(_("Conversation: oldest first"))
		self.context_back_asswards.connect('toggled', self.option_toggled,'option-context-backwards')
		self.disable_avatars = gtk.CheckButton(_("Disable avatar downloading"))
		self.disable_avatars.connect('toggled', self.option_toggled,'option-no-avatars')
		
		self.ctrl_enter = gtk.CheckButton(_("CTRL+Enter submits status"))
		self.ctrl_enter.connect("toggled", self.option_toggled,'option-ctrl-enter')
		
		self.api_retweet = gtk.CheckButton(_("Use retweet API instead of default redent style"))
		self.api_retweet.connect("toggled", self.option_toggled,'option-api-retweet')
		
		self.enable_notifications = gtk.CheckButton(_("Enable notifications"))
		self.enable_notifications.connect("toggled", self.option_toggled,'option-notifications')
		self.enable_notify_replies = gtk.CheckButton(_("Enable @replies notifications"))
		self.enable_notify_replies.connect('toggled', self.option_toggled,'option-notify-replies')
		
		options_box.pack_start(self.ctrl_enter,False,False,0)
		options_box.pack_start(self.context_back_asswards,False,False,0)
		options_box.pack_start(self.disable_avatars,False,False,0)
		options_box.pack_start(self.api_retweet,False,False,0)
		#does the app have notifications?
		if has_pynotify:
			options_box.pack_start(self.enable_notifications,False,False,0)
			options_box.pack_start(self.enable_notify_replies,False,False,0)
		options_frame = gtk.Frame(_("Options"))
		options_frame.add(options_box)
		vbox.pack_start(options_frame,False,False,0)
		#initial dents
		idhbox = gtk.HBox(False)
		idhbox.pack_start(gtk.Label(_("Number of dents at start-up: ")),False,False,0)
		self.initial_dents = gtk.HScale()
		self.initial_dents.connect('value-changed', self.initial_dents_changed)
		self.initial_dents.set_digits(0)
		self.initial_dents.set_range(20,100)
		self.initial_dents.set_increments(5,5)
		self.initial_dents.set_value_pos(gtk.POS_LEFT)
		#add the dpr to the options
		idhbox.pack_start(self.initial_dents)
		options_box.pack_start(idhbox,False,False,0)
		
		#pull time
		pthbox = gtk.HBox(False)
		pthbox.pack_start(gtk.Label(_("Update Interval: ")),False,False,0)
		self.pull_time = gtk.HScale()
		self.pull_time.connect('value-changed', self.pull_time_changed)
		self.pull_time.set_digits(0)
		self.pull_time.set_range(45,300)
		self.pull_time.set_increments(15,30)
		self.pull_time.set_value_pos(gtk.POS_LEFT)
		
		#add the pulltime slider+label
		pthbox.pack_start(self.pull_time)
		options_box.pack_start(pthbox,False,False,0)
		
		#how do we handle the link color?
		#don't show this on Maemo
		if not has_hildon:
			colorlabel = gtk.Label(_("Link Color: "))
			chbox = gtk.HBox(False)
			chbox.pack_start(colorlabel,False,False,0)
			self.color = gtk.Entry()
			self.color.connect('changed', self.check_color )
			self.color.set_tooltip_text(
			_("enter a hexadecimal color such as '#3333ff' or a color name such as 'yellow'"))
			chbox.pack_start(self.color,False,False,0)
			self.colorevent = gtk.EventBox()
			chbox.pack_start(self.colorevent)
			options_box.pack_start(chbox,False,False,0)
			
		#add the fucking filter stuff
		filters_frame = gtk.Frame( _("Filters") )
		filters_vbox = gtk.VBox(False)
		filters_frame.add(filters_vbox)
		#create and add a FilterFrame for users
		self.userfilterframe = FilterFrame(_("User"))
		filters_vbox.pack_start(self.userfilterframe)
		#connect the userfilterframe
		self.userfilterframe.connect('add-filter', self.add_user_filter)
		self.userfilterframe.connect('remove-filter', self.remove_user_filter)
		#create and add a FilterFrame for strings
		self.stringfilterframe = FilterFrame(_("String"))
		filters_vbox.pack_start(self.stringfilterframe)
		vbox.pack_start(filters_frame)
		#connect the stringfilterframe
		self.stringfilterframe.connect('add-filter', self.add_string_filter)
		self.stringfilterframe.connect('remove-filter', self.remove_string_filter)
		
		
	def check_color(self,widget):
		color_string = self.color.get_text()
		try:
			color = gtk.gdk.Color(color_string)
			self.set_link_color(color_string)
			self.emit('link-color', color_string)
		except:
			pass
			
	def set_link_color(self,color_name):
		if not self.has_hildon:
			self.color.set_text(color_name)
			the_color = gtk.gdk.color_parse(color_name)
			self.colorevent.modify_bg(gtk.STATE_NORMAL,the_color )
		
	def set_run_as_tray_app(self,boolean):
		if not self.has_hildon:
			self.run_as_tray_app.set_active(boolean)	
	
	def set_context_backwards(self,boolean):
		self.context_back_asswards.set_active(boolean)
		
	def set_no_avatars(self,boolean):
		self.disable_avatars.set_active(boolean)

	def set_ctrl_enter(self,boolean):
		self.ctrl_enter.set_active(boolean)

	def set_api_retweet(self,boolean):
		self.api_retweet.set_active(boolean)


	#More Code for notifications			
	def set_notifications(self,boolean):
		self.enable_notifications.set_active(boolean)

	def set_notify_replies(self,boolean):
		self.enable_notify_replies.set_active(boolean)
	
	def set_name(self,name):
		self.account_name_entry.set_text(name)

	def set_password(self,password):
		self.account_password_entry.set_text(password)

	def set_service(self,service):
		self.account_apiroot_entry.set_text(service)

	def set_initial_dents(self,initial_dents):
		#convert the dents to a number
		self.initial_dents.set_value( int(initial_dents) )
		
	def set_pull_time(self,pull_time_str):
		"""Sets the value of the self.pull_time hslider.
		If the call comes from heybuddy.py it will come from
		ConfigParser which stores things as strings. To simplify
		the code it is assumed to be a string and converted to an int
		everytime"""
		self.pull_time.set_value( int(pull_time_str) )

	def submit_clicked(self,widget):
		#get the name and password
		n=self.account_name_entry.get_text()
		p=self.account_password_entry.get_text()
		a=self.account_apiroot_entry.get_text()
		if n!="" and p!="" and a!="" :
			self.emit('update-account',n,p,a)

	def option_toggled(self,widget,signal):
		value = widget.get_active()
		self.emit(signal,value)
		
	def initial_dents_changed(self,widget):
		value = self.initial_dents.get_value()
		self.emit('initial-dents',value)
	
	def pull_time_changed(self,widget):
		"""Gets the value of the pull time slider then emits a
		signal to notify other classes of the change"""
		value = self.pull_time.get_value()
		self.emit('pull-time',value)

	def add_string_filter(self,filterframe,string):
		self.emit('add-string-filter',string)
		
	def remove_string_filter(self,filterframe,string):
		self.emit('remove-string-filter',string)

	def set_string_filters(self, filters ):
		self.stringfilterframe.set_filters(filters)

	def add_user_filter(self,filterframe,user):
		self.emit('add-user-filter',user)
		
	def remove_user_filter(self,filterframe,user):
		self.emit('remove-user-filter',user)

	def set_user_filters(self, filters ):
		self.userfilterframe.set_filters(filters)
