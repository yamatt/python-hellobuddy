'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import gtk,gobject
class FilterFrame(gtk.VBox):
	__gsignals__={
		'add-filter': (
				gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		'remove-filter' : (
				gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE,
					(gobject.TYPE_STRING,)
			)
		}
	def __init__(self,title):
		gtk.VBox.__init__(self)
		#self.set_label(title+"s")
		#title_label = gtk.Label(title)
		#self.pack_start(title_label)
		'''start making the internals'''
		#create a vbox to be the widget of the frame
		#vbox = gtk.VBox(False)
		#self.add(vbox)
		entry_wrapper = gtk.HBox(False)
		label = gtk.Label(_("%s to filter: ") % title)
		self.add_button = gtk.Button(_("Add"))
		self.add_button.connect('clicked', self.add_entry)
		#disable the button
		self.add_button.set_sensitive(False)
		#create a text entry
		self.filter_entry = gtk.Entry()
		#
		self.filter_entry.connect('changed', self.filter_entry_changed)
		#add the filter_entry to the entry_wrapper
		entry_wrapper.pack_start(label,False,False,0)
		entry_wrapper.pack_start(self.filter_entry,False,False,0)
		#add the button to the wrapper
		entry_wrapper.pack_start(self.add_button,False,False,0)
		#add the wrapper to the vbox
		self.pack_start(entry_wrapper,False,False,0)
		#we need a liststore to hold the items to filter
		self.liststore = gtk.ListStore(gobject.TYPE_STRING)
		#we need a treeview to display the liststore
		self.treeview = gtk.TreeView(self.liststore)
		#create a cell renderer
		cell = gtk.CellRendererText()
		#create a column for the treeview
		col = gtk.TreeViewColumn(_("Filtered %s") % (title), cell,text=0)
		self.treeview.append_column(col)
		#check for changes to the treeview
		self.treeview.connect('cursor-changed', self.filter_selected)
		#add the treeview to self
		self.pack_start(self.treeview,False,False,0)
		#create a remove button
		self.remove_button = gtk.Button(_("Remove"))
		self.remove_button.connect('clicked',self.remove_selected_filter )
		self.remove_button.set_sensitive(False)
		remove_wrapper = gtk.HBox(False)
		remove_wrapper.pack_start(self.remove_button,False,False,0)
		#add the wrapper to self
		self.pack_start(remove_wrapper,False,False,0)
			
	def add_entry(self,button):
		text = self.filter_entry.get_text().strip()
		if len(text)>0:
			self.emit('add-filter',text)
			self.filter_entry.set_text('')
			
	def filter_entry_changed(self,entry):
		text = entry.get_text().strip()
		button_active = (len(text) > 0 )
		self.add_button.set_sensitive(button_active )
		
	def set_filters(self,filters):
		#clear the liststore
		self.liststore.clear()
		self.current_selected_index=None
		self.remove_button.set_sensitive(False)
		#loop through the filters
		for filter in filters:
			#add the filter to the liststore
			iter = self.liststore.append( )
			self.liststore.set_value(iter,0,filter)
	
	def filter_selected(self,tv):
		#get the currently selected filter
		cursor = self.treeview.get_cursor()
		index=cursor[0][0]
		if index >=0 and index != None:
			self.remove_button.set_sensitive(True)
			self.current_selected_index=index
	
	def remove_selected_filter(self,button):
		selection = self.treeview.get_selection()
		selected = selection.get_selected()
		iter = selected[1]
		filter = self.liststore.get_value(iter,0)
		if len(filter)>0:
			self.emit('remove-filter',filter)
