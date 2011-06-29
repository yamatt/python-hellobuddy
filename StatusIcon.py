'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import gtk
import gobject

class StatusIcon(gtk.StatusIcon,gobject.GObject):
	__gsignals__ = {
		'quit-selected': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
						   ()
			)
		}
	def __init__(self):
		gtk.StatusIcon.__init__(self)
		self.connect('popup-menu', self.display_menu )
		'''make some menu shit'''
		self.menu = gtk.Menu()
		#make a quit menu item
		menu_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		menu_item.connect('activate', self.quit_selected)		
		self.menu.append(menu_item);		
		self.menu.show_all()
		
	def set_icon(self,icon_path):
		self.set_from_file( icon_path )
	
	def quit_selected(self,widget):
		self.emit('quit-selected')
	
	def display_menu(self,status_icon, button, activate_time):
		self.menu.popup(None,None,None, button,activate_time)
