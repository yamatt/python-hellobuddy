'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
from DentScroller import DentScroller
from DentButton import DentButton
import gtk,gobject
from PlatformSpecific import links_unavailable
class GroupPage(gtk.VBox,gobject.GObject):
	__gsignals__={
		'group-page-hide': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 ()
		),
		'join-group' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				(gobject.TYPE_STRING,gobject.TYPE_BOOLEAN)
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

		self.image = gtk.Image()
		#make an
		imagevbox = gtk.VBox(False,0)
		imagevbox.pack_start(self.image,False,False,0)

		#make an hbox to hold image and group info
		self.grouphbox=gtk.HBox(False,5)
		self.pack_start(self.grouphbox,False,False,0)
		self.grouphbox.pack_start(imagevbox,False,False,0)
		infovbox = gtk.VBox(False)
		self.grouphbox.pack_start(infovbox,False,False)
		
		self.name_label = gtk.Label()
		infovbox.pack_start(self.name_label,False,False,0)
		
		self.homepage_label = gtk.Label()
		if not links_unavailable:
			self.homepage_label.connect('activate-link', self.process_link )
		infovbox.pack_start(self.homepage_label,False,False,0)
		
		self.description_label = gtk.Label()
		infovbox.pack_start(self.description_label,False,False,0)
		self.description_label.set_line_wrap(True)
		
		self.location_label = gtk.Label()
		infovbox.pack_start(self.location_label,False,False,0)
		
		#widget box for the horizontal stuff
		self.widgetbox = gtk.HBox(False)
		self.pack_start(self.widgetbox,False,False,0)
		
		#make a checkbutton if we are following
		self.joined_checkbutton = gtk.CheckButton(_("joined"))
		self.joined_checkbutton.connect('toggled', self.joined_toggled)
		self.widgetbox.pack_start(self.joined_checkbutton,False,False,0)
		
		#collapse button
		collapsebox = gtk.Alignment(xalign=1.0)
		self.collapse_button = DentButton(u'\u25b2')
		self.collapse_button.connect('clicked',self.collapse_clicked)
		collapsebox.add(self.collapse_button)
		self.widgetbox.pack_end(collapsebox,True,True,0)
		
		#collapsed widget box and name label
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
		
		#create a group dent scroller and add it to the group page
		self.dentScroller = DentScroller()
		self.pack_start(self.dentScroller)
		
	def set_group_data(self,data):
		self.joined_checkbutton.set_sensitive(True)
		self.group_id= data['id']
		self.group_name = data['fullname']
		self.name_label.set_text("%s" %(data['fullname']) )
		self.name_label_collapsed.set_text("%s" %(data['fullname']) )
		if data['location']!=None:
			self.location_label.set_text("%s: %s" %(_("Location"), data['location']) )
			self.location_label.show()
		else:
			self.location_label.hide_all()
			
		if data['description']!=None:
			self.description_label.set_text("%s" %(data['description']) )
			self.description_label.show()
		else:
			self.description_label.hide_all()
		
		if data['homepage']!=None:
			try:
				self.homepage_label.set_markup('<a href="%(homepage)s">%(homepage)s</a>' % ({'homepage':data['homepage']}) )
			except:
				self.homepage_label.set_text("%s" %(data['homepage']) )
			self.homepage_label.show()
		else:
			self.homepage_label.hide_all()
		#is the user a member?
		if data['member']=='true':
			self.set_is_member(True)
	
	def set_image(self,image):
		self.image.set_from_file(image)
		self.image.show()
			
	def set_is_member(self,bool):
		self.toggle_enabled=False
		self.is_joined=bool
		self.joined_checkbutton.set_active( bool )
		self.toggle_enabled=True
		
	def clear(self):
		self.dentScroller.clear()
		self.image.hide()
	
	def joined_toggled(self,widget):
		if self.toggle_enabled:
			self.new_is_joined = self.joined_checkbutton.get_active()
			self.emit('join-group',self.group_id,self.new_is_joined)
		
	def close(self,button):
		#we don't need to talk to the controller
		#self.hide()
		self.emit('group-page-hide')
		
	def collapse_clicked(self,widget):
		self.grouphbox.hide()
		self.widgetbox.hide()
		self.widgetbox_collapsed.show()
	
	def expand_clicked(self,widget):
		self.grouphbox.show()
		self.widgetbox.show()
		self.widgetbox_collapsed.hide()
	
	def process_link(self, label, uri ):
		self.emit('open-link', uri )
		return True
