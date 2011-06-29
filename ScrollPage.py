'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
from DentScroller import DentScroller
import gtk
class ScrollPage(gtk.VBox):
	def __init__(self):
		gtk.VBox.__init__(self)
		self.set_homogeneous(False)
		self.dentScroller = DentScroller()
		self.pack_start(self.dentScroller,True,True,0)

