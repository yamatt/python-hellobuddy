'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import gtk
import PlatformSpecific	
#what is the max number of dents we want to keep track of?
class DentScroller(gtk.EventBox):
	def __init__(self):
		gtk.EventBox.__init__(self)
		#keep track of this dentscroller's ids
		self.ids = []
		main_child= PlatformSpecific.ScrollThingy()
		self.add(main_child)	
		self.dent_scroll_vbox=gtk.VBox(spacing=1)
		self.viewport = gtk.Viewport()
		self.viewport.add(self.dent_scroll_vbox)
		try:
			the_color = gtk.gdk.color_parse('#666')
			self.viewport.modify_bg(gtk.STATE_NORMAL,the_color )
		except:
			#what the hell version of python-gtk is this?
			pass
		main_child.add(self.viewport)
		# add an empty "something" to the vbox
		self.dent_scroll_vbox.pack_end(gtk.Label(),True,True,0)
		
	def add_dent(self,dent,is_conv=False,conv_backwards=False):
		#is this id already in this scroller?
		dent_id = dent.id
		if not dent_id in self.ids:
			self.ids.append(dent_id)
			if is_conv and not conv_backwards:
				self.dent_scroll_vbox.pack_start(dent,False,False,0)
			else:
				self.dent_scroll_vbox.pack_end(dent,False,False,0)

			#it would be nice to see this dent
			dent.show_all()
			return True
		else:
			del dent_id
			del dent
			return False

	def prune(self, number):
		#hey! how many children does the self.dent_scroll_vbox have?
		children=self.dent_scroll_vbox.get_children()
		while len(children)>number:
			self.dent_scroll_vbox.remove( children[-1] )
			d = children.pop()
			try:
				self.ids.remove(d.id)
			except:
				pass
			d.unrealize()
			d.destroy()
			del d

	def clear(self):
		children=self.dent_scroll_vbox.get_children()
		#clear the ids
		self.ids = []
		for child in children:
			child.unrealize()
			child.destroy()
		
