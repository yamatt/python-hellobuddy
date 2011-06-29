'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''

import gtk
import gobject
import PlatformSpecific
from DentButton import DentButton
class Dent(gtk.EventBox, gobject.GObject):
	__gsignals__ = {
		'reply-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'direct-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'view-conversation-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_INT,)
			),
		'favorite-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 ()
			),
		'unfavorite-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 ()
			),
		'user-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
			'profile-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING, gobject.TYPE_STRING,)
			),
			'id-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'group-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'text-label-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_PYOBJECT,)
			),
		'redent-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,gobject.TYPE_STRING)
			),
			'open-link': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
	}
	def __init__(self,data,is_conv=False,is_direct=False):
		gtk.EventBox.__init__(self)
		#store the passed variables
		self.id = data['status_id']
		self.screen_name = data['screen_name']
		self.in_reply_to_id=data['in_reply_to_id']
		self.in_reply_to_screen_name=data['in_reply_to_screen_name']
		self.profile_url = data['profile_url']
		user_box = gtk.HBox(False,5)
		user_box.set_border_width(5)
		self.image = gtk.Image()
		#make an
		imagevbox = gtk.VBox(False,0)
		imagevbox.pack_start(self.image,False,False,0)
		user_box.pack_start(imagevbox,False,False,0)
		vbox = gtk.VBox(False,0)
		#vbox.set_border_width(5)
		user_box.pack_start(vbox,True,True,0)
		self.text_label = gtk.Label()		
		self.text_label.set_markup( data['markup'] )
		self.text_label.set_alignment(0,0)
		self.text_label.set_line_wrap(True)
		self.text_label.set_selectable(True)
		self.text_label.connect( 'size-allocate', self.label_size_allocate )
		#unset this things focus
		self.text_label.unset_flags(gtk.CAN_FOCUS)
		self.text_label.set_justify(gtk.JUSTIFY_LEFT)
		#keep track of clicks on the text
		self.text_label.connect('button-press-event', self.text_label_clicked)
		
		name_label = gtk.Label()
		name_label.set_markup("<b>%s</b>" % (self.screen_name))
		self.name_event_box = gtk.EventBox()
		self.name_event_box.add(name_label)
		#connect some signals to the event box
		self.name_event_box.connect('button-press-event', self.name_label_clicked )
		self.name_event_box.connect('realize',self.event_box_realized)
		#visited links may not work on some systems ( like my N810 )
		try:
			self.text_label.connect('activate-link', self.process_link )
			self.text_label.set_track_visited_links(False)
		except:
			#nothing to do
			pass
		#make the time label
		time_label = gtk.Label()
		#make an hbox for the name_button and time label
		hbox = gtk.HBox(False,0)
		hbox.pack_start(self.name_event_box,False,False,0)
		hbox.pack_start(time_label,False,False,0)
		#process time for the time label
		time_from_str = " <span size='x-small'> %s</span>" % (data['time'])
		time_label.set_markup(time_from_str )
		if data['source']!=None:
			source_label=gtk.Label()
			source_str=" <span size='x-small'> from %s</span>" % (data['source'])
			source_label.set_markup(source_str)
			hbox.pack_start(source_label,False,False,0)
		
		vbox.pack_start(hbox,False,False,0)
		vbox.pack_start(self.text_label,True,True,0)
		#make a hbox to hold the buttons
		hbox1 = gtk.HBox(False,0)
		if not is_direct:
			#check the loveydovey
			if data['favorited']=='false':
				#make a loveydovey button
				self.favorite_button = DentButton(u'\u2665')
				self.favorite_handler = self.favorite_button.connect('clicked',self.favorite_clicked)
			else:
				#make an unloveybutton
				self.favorite_button = DentButton(u'\u2661')
				self.favorite_handler = self.favorite_button.connect('clicked',self.unfavorite_clicked)
				
			hbox1.pack_start(self.favorite_button,False,False,0)
				
			#make a redent button
			if PlatformSpecific.has_hildon:
				redent_button=DentButton( 'RD' )
			else:
				redent_button=DentButton( u'\u267a' )
			redent_button.connect('clicked',self.redent_clicked)
			hbox1.pack_start(redent_button,False,False,0)
		
		if is_direct:
			#how about a 'direct' button?
			direct_button = DentButton(_("direct"))
			direct_button.connect('clicked',self.direct_clicked)
			hbox1.pack_start(direct_button,False,False,0)
		else:
			#add a "reply" button
			reply_button = DentButton('reply')
			reply_button.connect("clicked",self.reply_clicked)
			hbox1.pack_start(reply_button,False,False,0)
		
		#if there is a in reply to conversation happening
		if self.in_reply_to_id!=None:
			reply_to_button = DentButton(_("context"))
			reply_to_button.connect('clicked',self.view_conv_clicked)
			hbox1.pack_start(reply_to_button,False,False,0)
		
		
		##one last check for is direct
		if not is_direct:
			#add the dent number here
			id_label = gtk.Label()
			id_label.set_markup("<span size='x-small'>  %s</span>"%(self.id))
			id_label_event_box = gtk.EventBox()
			id_label_event_box.add(id_label)
			#connect some signals to the event box
			id_label_event_box.connect('button-press-event', self.id_label_clicked )
			id_label_event_box.connect('realize',self.event_box_realized)
			'''
			if not PlatformSpecific.links_unavailable:
				link = 'id:%s' % ( self.id )
				id_str=" <span size='x-small'> id:<a href='%s'>%s</a></span>" % (link, self.id)
				id_label.set_markup(id_str)
				id_label.connect('activate-link', self.process_link )
				id_label.set_track_visited_links(False)
			else:
				id_label.set_text("id:%s" % (self.id) )
				'''
			align = gtk.Alignment(yalign=0.9, xalign=0.0)
			align.add(id_label_event_box)
			
			hbox1.pack_start(align, True,True, 0)
		
		vbox.pack_start(hbox1,False,False,0)
		self.add(user_box)
	
	def event_box_realized(self,widget):
		hand2 = gtk.gdk.Cursor(gtk.gdk.HAND2)
		widget.window.set_cursor(hand2)
	
	def name_label_clicked(self,widget,event):
		self.emit('profile-clicked',self.profile_url, self.screen_name)
	
	def reply_clicked(self,button):
		self.emit('reply-clicked',self.screen_name)

	def direct_clicked(self,button):
		self.emit('direct-clicked',self.screen_name)

	def redent_clicked(self,button):
		text = self.text_label.get_text()
		self.emit('redent-clicked',self.screen_name, text)

	def view_conv_clicked(self,button):
		self.emit('view-conversation-clicked',self.id)
		
	def favorite_clicked(self,button):
		self.emit('favorite-clicked')	
		self.favorite_button.disconnect( self.favorite_handler )
		self.favorite_button.set_text(u'\u2661')
		self.favorite_handler = self.favorite_button.connect('clicked',self.unfavorite_clicked)
	
	def unfavorite_clicked(self,button):
		self.emit('unfavorite-clicked')	
		self.favorite_button.disconnect( self.favorite_handler )
		self.favorite_button.set_text(u'\u2665')
		self.favorite_handler = self.favorite_button.connect('clicked',self.favorite_clicked)
	
	def set_image(self,image_path):
		self.image.set_from_file(image_path)
		
	def process_link(self, label, uri ):
		if uri[0]=='@':
			screen_name=uri.lstrip('@')
			self.emit('user-clicked',screen_name)
			#since we are processing the uri return true
			return True
		elif uri[0]=='!':
			group_name=uri.lstrip('!')
			self.emit('group-clicked',group_name)
			#since we are processing the uri return true
			return True
		else:
			self.emit('open-link', uri )
			return True
			
	def text_label_clicked(self,widget,event):
		self.emit('text-label-clicked', widget)
	
	def id_label_clicked(self,widget,event):
		self.emit('id-clicked', self.id)
					
	
	def label_size_allocate( self, label, allocation ):
		self.text_label.set_size_request( allocation.width-5, -1 )				
			
