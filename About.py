'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import gtk,gobject
import os
import PlatformSpecific
import platform
class About(gtk.VBox,gobject.GObject):
	__gsignals__={
		'open-link': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			),
		}
	def __init__(self,version,branch,icon,readme_file):
		gtk.VBox.__init__(self)
		#we are not homogenous
		self.set_homogeneous(False)
		self.set_border_width(5)
		#make an hbox for some stuff
		hbox = gtk.HBox(False)
		image = gtk.Image()
		image.set_from_file(icon)
		hbox.pack_start(image,False,False,0)
		vbox = gtk.VBox(False)
		app_label = gtk.Label()
		app_label.set_markup("<b>Heybuddy</b> %s %s" % ( version,branch ) )
		vbox.pack_start(app_label,False,False,0)
		cp_label = gtk.Label('copyright 2010 Jezra Lickter')
		vbox.pack_start(cp_label,False,False,0)
		url_label = gtk.Label()
		url = 'http://www.jezra.net/projects/heybuddy'
		if not PlatformSpecific.links_unavailable:
			url_label.set_markup("<a href='%(url)s'>%(url)s</a>" % {'url':url})
			url_label.connect('activate-link', self.process_link )
		else:
			url_label.set_text(url)
			
		vbox.pack_start(url_label,False,False,0)
		(maj,min,mic) = gtk.gtk_version
		gtk_label=gtk.Label("GTK: %d.%d.%d " % ((maj,min,mic)) )
		(maj,min,mic) = gtk.pygtk_version
		pygtk_label = gtk.Label("PyGTK: %d.%d.%d " % ((maj,min,mic)) )
		python_label = gtk.Label("Python: %s" %(platform.python_version()) )

		sysvbox = gtk.VBox(False)
		sysvbox.set_border_width(10)
		sysvbox.pack_start(gtk.Label(_("System Info")),False,False)
		sysvbox.pack_start(gtk_label,False,False,0)
		sysvbox.pack_start(pygtk_label,False,False,0)
		sysvbox.pack_start(python_label,False,False,0)
		#vbox.pack_start(sysvbox)
		
		hbox.pack_start(vbox,False,False,0)
		self.pack_start(hbox,False,False,0)
		self.pack_start(sysvbox,False,False,0)
		#get the text of the readme
		f = open(readme_file)
		text = f.read()
		f.close()
		#figure out where to put the text
		tb = gtk.TextBuffer()
		tv = gtk.TextView(tb)
		tv.set_property('left-margin', 3)
		tv.set_editable(False)
		tv.set_wrap_mode(gtk.WRAP_WORD_CHAR)
		tb.set_text(text)
		tscroll = PlatformSpecific.ScrollThingy()
		tscroll.add(tv)
		self.pack_start(tscroll)
	
	def process_link(self, label, uri ):
		self.emit('open-link', uri )
		return True
		
