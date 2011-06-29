'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import gtk
import gobject
from DentScroller import DentScroller
from Dent import Dent
try:
	import gtkspell
	has_gtkspell=True
except:
	has_gtkspell=False

from PlatformSpecific import has_hildon
#make a fake enumeration
DENT,MENTION,DIRECT,CONVERSATION,USER,GROUP,ACCOUNT,ABOUT = range(8)
STATUS_MESSAGE,ERROR_MESSAGE = range(2)
class MainWindow(gtk.Window,gobject.GObject):
	__gsignals__ = {
		'update-status': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'get-conversation': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_INT,)
			),
		'show-user': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'show-group': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'notebook-page-change': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_INT,gobject.TYPE_INT)
			),
		'follow-user' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				(gobject.TYPE_STRING,gobject.TYPE_BOOLEAN)
			),
		'join-group' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				(gobject.TYPE_STRING,gobject.TYPE_BOOLEAN)
			),
		'add-tag-filter': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_STRING,)
			),
		'remove-tag-filter' : (
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
			),
		'add-group-filter': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 (gobject.TYPE_STRING,)
			),
		'remove-group-filter' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				(gobject.TYPE_STRING,)
			),
		'clear-respond-to-id' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				()
			),
		'quit' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				()
			),
		'window-to-tray' : (
			gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
				()
			)		 
	}
	def __init__(self,app_name,version,branch):
		gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)	
		gobject.GObject.__init__(self)
		self.textlimit = 140 #this is default
		self.last_clicked_label=None
		self.is_fullscreen=False
		self.set_title(app_name)
		self.set_default_size(500,500)
		self.notebook_current_page=DENT
		self.string_update_textview=_("Update Status")
		self.string_direct_message=_("Direct Message to")
		self.string_status_frame=self.string_update_textview
		self.conversation_page=None
		self.pre_conversation_page=None
		self.user_page=None
		self.pre_user_page=None
		self.pre_group_page=None
		self.is_direct_message_mode=False
		self.ctrl_enter = False
		#create an accellerator group for this window
		accel = gtk.AccelGroup()
		#add the ctrl+q to quit
		accel.connect_group(gtk.keysyms.q, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE, self.quit )
		#add ctrl+w to set tray app and close to tray
		accel.connect_group(gtk.keysyms.w, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE, self.window_to_tray )
		#add the ctrl+c to copy
		accel.connect_group(gtk.keysyms.c, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE, self.copy )
		#add the ctrl+Page_Up and ctrl Page_Down to notebook focus
		accel.connect_group(gtk.keysyms.Page_Up, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE, self.focus_notebook )
		accel.connect_group(gtk.keysyms.Page_Down, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE, self.focus_notebook )
		#select the current page first widget on Page up or down
		accel.connect_group(gtk.keysyms.Page_Down, 0, gtk.ACCEL_VISIBLE, self.focus_current_page_widget )
		accel.connect_group(gtk.keysyms.Page_Up, 0, gtk.ACCEL_VISIBLE, self.focus_current_page_widget )
		#set focus for ctrl+u		
		accel.connect_group(gtk.keysyms.u, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE, self.focus_update_textview )
		#set focus for ctrl+l		
		accel.connect_group(gtk.keysyms.l, gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE, self.focus_update_textview)
		#lock the group
		accel.lock()
		#add the group to the window
		self.add_accel_group(accel)
		
		''' make the GUI stuff '''
		#start with vbox
		self.main_vbox = gtk.VBox()
		#add the vbox to the self
		self.add(self.main_vbox)
		#make a notebook
		self.notebook = gtk.Notebook()
		#pack the note book in the vbox
		self.main_vbox.pack_start(self.notebook)
		#make the update status area
		self.update_textbuffer = gtk.TextBuffer()
		self.update_textview = gtk.TextView(self.update_textbuffer)
		#keep track of keypress events on the text view
		self.update_textview.connect('key-press-event', self.textview_keypress)
		#the text view needs to be multiline
		self.update_textview.set_wrap_mode(gtk.WRAP_WORD_CHAR)
		#try and add spell checking to the textview
		if has_gtkspell:
			#what if there is no aspell library?
			try:
				self.spell = gtkspell.Spell(self.update_textview)
				self.has_spell_library=True
			except Exception:
				#bummer
				self.has_spell_library=False
				print Exception.message
				
		#add a shadowed frame around the textview
		tvframe = gtk.Frame();
		tvframe.set_shadow_type(gtk.SHADOW_IN)
		tvframe.add(self.update_textview)
		#what happens when the buffer is changed?
		self.update_textbuffer.connect('changed', self.update_textbuffer_changed)
		update_frame = gtk.Frame()
		self.update_status_label = gtk.Label(self.string_status_frame)
		update_frame.add(tvframe)
		update_frame.set_label_widget(self.update_status_label)
		#make an hbox for the update frame and throbber
		update_hbox = gtk.HBox(False)
		self.throbber = gtk.Image()
		update_hbox.pack_start(update_frame,True,True)
		update_hbox.pack_start(self.throbber,False,False)
		self.main_vbox.pack_start(update_hbox,False,False,0)
		#make a message label that we might need to display to the user
		self.message_label = gtk.Label()
		self.main_vbox.pack_start(self.message_label,False,False,0)
		#check for a keypress
		self.connect('key-press-event',self.keypressed)
		
	def keypressed(self,widget,event):
		if event.keyval == 65475:
			self.toggle()
			
	def toggle(self):
		if self.is_fullscreen :
			self.unfullscreen()
			self.is_fullscreen=False
		else:
			self.fullscreen()
			self.is_fullscreen=True
	
	def run(self):
		#we don't want any signals until the app is running
		self.notebook.connect('switch-page', self.notebook_page_switch )
	
	def show_some(self):
		self.show_all()
		#hide *some* stuff
		self.message_label.hide()
	
	def add_notebook_page(self,widget,title):
		self.notebook.append_page(widget,title)
	
	def set_notebook_page(self,index):
		self.notebook.set_current_page(index)
		
	def get_notebook_index(self):
		return self.notebook.get_current_page()
		
	def add_dent(self,data,target_index,is_conv=False,conv_backwards=False):
		d = Dent(data)
		d.connect('reply-clicked', self.reply_clicked)
		d.connect('view-conversation-clicked', self.view_conversation)
		d.connect('user-clicked', self.view_user)
		d.connect('text-label-clicked',self.dent_text_clicked)
		d.connect('redent-clicked',self.redent_clicked)
		#add this to the dent it's targeting
		target = self.get_target_scroller(target_index)
		target.add_dent(d,is_conv,conv_backwards)	
		#return the dent
		return d
	#filters
	def add_tag_filter(self,filterframe,tag):
		self.emit('add-tag-filter',tag)
		
	def remove_tag_filter(self,filterframe,tag):
		self.emit('remove-tag-filter',tag)
	
	def set_tag_filters(self, filters ):
		self.filterpage.set_tag_filters(filters)
	
	def set_ctrl_enter(self, bool):
		self.ctrl_enter = bool
	
	def add_user_filter(self,filterframe,user):
		self.emit('add-user-filter',user)
		
	def remove_user_filter(self,filterframe,user):
		self.emit('remove-user-filter',user)
	
	def set_user_filters(self, filters ):
		self.filterpage.set_user_filters(filters)
	
	def add_group_filter(self,filterframe,group):
		self.emit('add-group-filter',group)
		
	def remove_group_filter(self,filterframe,group):
		self.emit('remove-group-filter',group)
	
	def set_group_filters(self, filters ):
		self.filterpage.set_group_filters(filters)
	
	def textview_keypress(self, widget, event) :
		#by default we don't submit
		submit = False
		#was a 'return' pressed?
		if event.keyval == gtk.keysyms.Return or event.keyval == gtk.keysyms.KP_Enter:
			if self.ctrl_enter:
				#check for the ctrl
				if event.state & gtk.gdk.CONTROL_MASK:
					submit=True
			else:
				submit=True
			if submit:
				self.emit_update_textview()
			#do *not* propogate the Return
			return True
			
	def set_textlimit(self, limit):
		self.textlimit = int(limit)
		
	def emit_update_textview(self):
		#get the text from the buffer
		start_iter = self.update_textbuffer.get_start_iter()
		end_iter = self.update_textbuffer.get_end_iter()
		text=self.update_textbuffer.get_text(start_iter,end_iter).strip()
		if(text!=""):
			#disable the textview
			self.update_textview.set_sensitive(False)
			self.emit('update-status',text)
			
	'''function process_update_response
	@param self self
	@param response the string response returned by the communicator
	'''
	def emit_update_textview_responsed(self, error = False):
		if not error:
			#detach the spellchecker
			self.detach_gtkspell()
			#clear the text area
			self.update_textbuffer.set_text('')
			#reattach the spellchecker
			self.connect_gtkspell()
		#enable the textview
		self.update_textview.set_sensitive(True)
			
	'''function update_textbuffer_changed
	@param self self
	@param textbuffer - the textbuffer that called the function
	'''
	def update_textbuffer_changed(self,textbuffer):
		#we aren't submitting, check the amount of characters
		char_count = textbuffer.get_char_count()
		self.string_update_textview_append_count(self.textlimit-char_count)
		if (char_count > self.textlimit ):
			#prune the text to self.textlimit chars
			start_iter = textbuffer.get_iter_at_offset(self.textlimit)
			end_iter = textbuffer.get_end_iter()
			textbuffer.delete(start_iter,end_iter)
		elif(char_count==0 and not self.is_direct_message_mode):
			#the text has possibly been deleted, clear associated stuff
			self.emit('clear-respond-to-id')

	def notebook_page_switch(self,nb,page,page_num):
		old_page = self.notebook_current_page
		self.notebook_current_page=page_num
		self.emit('notebook-page-change',old_page,page_num)


	def string_update_textview_append_count(self,count):
		if count<self.textlimit:
			string = "%s %d" % (self.string_status_frame,count)
		else:
			string = self.string_status_frame
		self.update_status_label.set_text(string)
	
	def set_message(self,message,type=STATUS_MESSAGE):
		if type==ERROR_MESSAGE:
			markup = "<span color='#dd0000'>%s</span>" % message
		else:
			markup = message
		self.message_label.set_markup(markup)
		#show the self.message label
		self.message_label.show()
	
	def clear_message(self):
		self.message_label.set_text('')
		self.message_label.hide()
	
	def close_conversation(self,widget):
		self.conversation_vbox.hide_all()
		self.notebook.set_current_page(self.pre_conversation_page)
	
	def quit(self,accel_group, acceleratable, keyval, modifier):
		self.emit("quit")
	
	def userpage_hide(self,widget):
		self.userpage.hide_all()
		self.set_notebook_page(self.pre_user_page)
	
	def grouppage_hide(self,widget):
		self.grouppage.hide_all()
		self.set_notebook_page(self.pre_group_page)
	
	def follow_user(self,widget,name,bool):
		self.emit('follow-user',name,bool)
	
	def join_group(self,widget,name,bool):
		self.emit('join-group',name,bool)
		
	def copy(self,accel_group,acceleratable,keyval,modifier):
		'''the user want to copy some text'''
		#can we get the selected text?
		try:
			#get the bounds of the last clicked label
			bounds = self.last_clicked_label.get_selection_bounds()
			#is the bounds empty or not?
			if bounds != ():
				#get the text from the last clicked label
				text = self.last_clicked_label.get_text()
				#get the text within the bounds
				selection = text[bounds[0]:bounds[1]]
				# get the clipboard
				clipboard = gtk.Clipboard()
				#set clipboard text
				clipboard.set_text(selection)
				#store that shit!
				clipboard.store()
		except:
			pass
		
	'''
	function window_to_tray
	emit 'window-to-tray' signal
	'''
	def window_to_tray(self,accel_group,acceleratable,keyval,modifier):
		self.emit('window-to-tray')
		
	def connect_gtkspell(self):
		if has_gtkspell and self.has_spell_library:
			self.spell = gtkspell.Spell(self.update_textview)
			
	def detach_gtkspell(self):
		if has_gtkspell and self.has_spell_library:
			self.spell.detach()

	def set_throbber(self,image_path):
		self.throbber.set_from_file(image_path)
		
	def dent_text_clicked(self,dent,text_label):
		self.last_clicked_label = text_label
	
	def set_is_direct_message_mode(self,mode,user=None):
		self.is_direct_message_mode=mode
		if mode:
			self.string_status_frame="%s %s" % (self.string_direct_message, user)
		else:
			self.string_status_frame=self.string_update_textview
			#clear the text
			self.update_textbuffer.set_text("")
		#update the label text
		self.update_status_label.set_text(self.string_status_frame)

	#we may need to set the focus on the notebook
	def focus_notebook(self,accel_group, acceleratable, keyval, modifier):
		#set the focus on the notebook
		self.notebook.grab_focus()
		
	def focus_current_page_widget(self,accel_group, acceleratable, keyval, modifier):
    #only change the focus if the tabs or textview has the focus
		if self.notebook.has_focus() or self.update_textview.has_focus():
			index = self.notebook.get_current_page()
			child = self.notebook.get_nth_page(index)
			focusable = self.first_focusable_widget( child )
			focusable.grab_focus()
		return False
			
	def first_focusable_widget(self,widget):
		#is this widget flagged "can_focus"?
		if widget.flags() & gtk.CAN_FOCUS:
			return widget
		#if this widget is a container, check it's children
		elif isinstance(widget, gtk.Container):
			children = widget.get_children()
			for child in children:
				child_widget = self.first_focusable_widget(child)
				if child_widget:
					return child_widget
		else:
			return False
		
	
	#we may need to set the focus on the status update textview
	def focus_update_textview(self,accel_group, acceleratable, keyval, modifier):
		#set the focus on the notebook
		self.update_textview.grab_focus()
		if keyval==gtk.keysyms.l:
			self.update_textbuffer.set_text('')
	
