'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
from ScrollPage import ScrollPage
import gtk,gobject
class ContextPage(ScrollPage,gobject.GObject):
	__gsignals__={
		'context-page-hide': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						 ()
		),

	}
	def __init__(self):
		ScrollPage.__init__(self)
	
	def close(self,button):
		#we can just hid ourself
		self.emit('context-page-hide')
