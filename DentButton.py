'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import gtk
try:
	import hildon
	has_hildon = True
except:
	has_hildon = False
	
class DentButton(gtk.Button):
	def __init__(self,string):
		gtk.Button.__init__(self)
		#add a "reply" button
		self.set_relief(gtk.RELIEF_HALF)
		self.button_label = gtk.Label()
		self.set_text(string)
		self.add(self.button_label)
	
	def set_text(self,string):
		if not has_hildon:
			markup="<span size='x-small' weight='bold'>%s</span>" % (string)
		else:
			markup = string
		self.button_label.set_markup(markup)
