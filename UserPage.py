'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
from DentScroller import DentScroller
from DentButton import DentButton
import gtk,gobject
from PlatformSpecific import links_unavailable
class UserPage(gtk.VBox,gobject.GObject):
	__gsignals__={
		'user-page-hide': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 ()
		),
		'follow-user' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				(gobject.TYPE_STRING,gobject.TYPE_BOOLEAN)
			),
		'direct-clicked': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
			'block-create': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
			'block-destroy': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
			'open-link': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
	}
	def __init__(self):
		gtk.VBox.__init__(self)
		gobject.GObject.__init__(self)
		self.set_homogeneous(False)
		self.toggle_enabled=True
		self.block_sent=False
		#start doing the image stuff
		self.image = gtk.Image()
		#make an
		imagevbox = gtk.VBox(False,0)
		imagevbox.pack_start(self.image,False,False,0)
		labelvbox = gtk.VBox(False,0)
		#we need a grip of labels
		self.name_label = gtk.Label()
		labelvbox.pack_start(self.name_label,False,False,0)
		
		self.description_label = gtk.Label()
		labelvbox.pack_start(self.description_label,False,False,0)
		self.description_label.set_line_wrap(True)
		
		self.location_label = gtk.Label()
		self.url_label = gtk.Label()
		if not links_unavailable:
			self.url_label.connect('activate-link', self.process_link )
		
		labelvbox.pack_start(self.location_label,False,False,0)
		labelvbox.pack_start(self.url_label,False,False,0)
		#make an hbox to hold the image and labels
		self.userhbox=gtk.HBox(False,5)
		#make an hbox to hold widgets
		self.widgetbox = gtk.HBox(False)
		#add the imagevbox
		self.userhbox.pack_start(imagevbox,False,False,0)
		self.userhbox.pack_start(labelvbox,False,False,0)
		self.pack_start(self.userhbox,False,False,0)
		self.pack_start(self.widgetbox,False,False,0)
		#make a checkbutton if we are following
		self.following_checkbutton = gtk.CheckButton(_("Following"))
		self.following_checkbutton.connect('toggled', self.following_toggled)
		self.widgetbox.pack_start(self.following_checkbutton,False,False,0)
		#how about a 'direct' button?
		self.direct_button = DentButton('direct')
		self.direct_button.connect('clicked',self.direct_clicked)
		self.widgetbox.pack_start(self.direct_button,False,False,0)
		#create stuff for blocking -- commented out 9.3.10 x1101
		blockbox=gtk.HBox()
		#enabler
		self.enable_block_checkbutton = gtk.CheckButton(_("Enable Blocking"))
		self.enable_block_checkbutton.connect('toggled', self.block_enable_toggled)
		
		#the blocking buttons
		self.block_button = DentButton('block')
		self.block_button.connect('clicked',self.block_clicked)
		self.block_button.set_sensitive(False)
		blockbox.pack_start(self.block_button,False,False,0)
		blockbox.pack_start(self.enable_block_checkbutton,False,False,0)
		self.widgetbox.pack_start(blockbox,False,False,0)
		
		#the collapse button
		collapsebox = gtk.Alignment(xalign=1.0)
		self.collapse_button = DentButton(u'\u25b2')
		self.collapse_button.connect('clicked',self.collapse_clicked)
		collapsebox.add(self.collapse_button)
		self.widgetbox.pack_end(collapsebox,True,True,0)
		
		#the collapsed widget box and name label
		self.widgetbox_collapsed = gtk.HBox(False)
		self.name_label_collapsed = gtk.Label()
		self.widgetbox_collapsed.pack_start(self.name_label_collapsed,False,False,0)
		#its expand button
		expandbox = gtk.Alignment(xalign=1.0)
		self.expand_button = DentButton(u'\u25bc')
		self.expand_button.connect('clicked',self.expand_clicked)
		expandbox.add(self.expand_button)
		self.widgetbox_collapsed.pack_end(expandbox,True,True,0)
		#pack it up
		self.pack_start(self.widgetbox_collapsed,False,False,0)
		
		#create a user dent scroller and add it to the user page
		self.dentScroller = DentScroller()
		self.pack_start(self.dentScroller)
		
	def set_image(self,image):
		self.image.set_from_file(image)
		self.image.show()
	
	def set_user_data(self,data):
		self.screen_name = data['screen_name']
		self.user_id=data['id']
		self.name_label.set_text("%s (%s)" %(data['name'],data['screen_name']) )
		self.name_label_collapsed.set_text("%s (%s)" %(data['name'],data['screen_name']) )
		if data['location']!=None:
			self.location_label.set_text("%s: %s" % (_("Location"),data['location']) )
			self.location_label.show()
		else:
			self.location_label.hide()
			
		if data['url']!=None:
			try:
				self.url_label.set_markup('<a href="%(url)s">%(url)s</a>' % ({'url':data['url']}) )
			except:
				self.url_label.set_text("%s" %(data['url']) )
		else:
			self.url_label.hide()
			
		self.description_label.set_text("%s" %(data['description']) )
		if data['following']=='true':
			self.set_is_friend(True)
		else:
			self.set_is_friend(False)
		#enable the stuff
		self.enable()
		
	def set_is_friend(self,bool):
		self.toggle_enabled=False
		self.is_friend=bool
		self.following_checkbutton.set_active( bool )
		self.toggle_enabled=True
		
	def following_toggled(self,widget):
		if self.toggle_enabled:
			self.new_is_friend = self.following_checkbutton.get_active()
			self.emit('follow-user',self.screen_name,self.new_is_friend)

	def clear(self):
		self.dentScroller.clear()
		#self.image.hide()
		
	def close(self,button):
		self.emit('user-page-hide')
		
	def direct_clicked(self,button):
		self.emit('direct-clicked',self.screen_name)
		
	def disable(self):
		self.following_checkbutton.set_sensitive(False)
		self.direct_button.set_sensitive(False)
		self.enable_block_checkbutton.set_sensitive(False)
		self.enable_block_checkbutton.set_active(False)
		#reset the block sent
		self.block_sent=False
	
	def enable(self):
		self.following_checkbutton.set_sensitive(True)
		self.direct_button.set_sensitive(True)
		self.enable_block_checkbutton.set_sensitive(True)

	def block_enable_toggled(self,widget):
		value = widget.get_active()
		if not self.block_sent:
			self.block_button.set_sensitive(value)
		
	def block_clicked(self,widget):
		#keep track of the block being sent
		self.block_sent=True
		#disable the button
		widget.set_sensitive(False)
		self.emit('block-create',self.user_id)

	def collapse_clicked(self,widget):
		self.userhbox.hide()
		self.widgetbox.hide()
		self.widgetbox_collapsed.show()
	
	def expand_clicked(self,widget):
		self.userhbox.show()
		self.widgetbox.show()
		self.widgetbox_collapsed.hide()
	
	def process_link(self, label, uri ):
		self.emit('open-link', uri )
		return True

