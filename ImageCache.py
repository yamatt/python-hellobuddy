'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import sys
import os
import gobject
import tempfile
class ImageCache(gobject.GObject):
	__gsignals__ = {
		'get-widget-image': (
			gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
							 (gobject.TYPE_STRING,)
			)
		}
	
	def __init__(self):
		gobject.GObject.__init__(self)
		#where will files be cached?
		cache_dir = 'heybuddy_cache'
		try:
			cache_dir+="_"+os.environ["USER"]
		except:
			pass

		self.cache_dir = os.path.join(tempfile.gettempdir(),cache_dir)
		#if the cache_dir doesn't exist; make it
		if not os.path.exists(self.cache_dir):
			os.mkdir(self.cache_dir)
		#make a dict to hold widget/image data
		self.pending_widgets_images = {}	
		#make a list of images to get
		self.images_to_get = []
		#boolean is this disabled?
		self.disabled=False
	
	def set_disabled(self,bool):
		self.disabled=bool
	
	def add_image_to_widget(self,image,widget):
		if self.disabled: #if disabled, do nothing
			return
		image_file = self.image_file_name(image)
		image_path = os.path.join(self.cache_dir,image_file)
		if os.path.exists(image_path):
			widget.set_image( image_path )
		else:
			'''we need to get the image'''
			#add the info to the pending dictionary
			self.pending_widgets_images[widget]=image
			#does this image need to be downloaded?
			if not image in self.images_to_get:
				self.images_to_get.append(image)
	
	def image_file_name(self,string):
		parts = string.split('/')
		return parts[-1]
		
	def widget_image_add(self,data,image):
		image_file = self.image_file_name(image)
		image_path = os.path.join(self.cache_dir,image_file)
		#write the data to the file
		f = open( image_path,'w' )
		
		f.write(data)
		f.close()
		items = self.pending_widgets_images.items()
		#loop through the pending dictionary
		for k,v in items:
			if v==image:
				k.set_image( image_path )
				#delete the widget from the dictionary	
				del self.pending_widgets_images[k] 
	
	def get_images(self):
		while len(self.images_to_get)>0:
			image = self.images_to_get.pop()
			#emit a signal to get the image
			gobject.idle_add(self.emit,'get-widget-image',image)
          
	def get_image_path(self,image):
		return os.path.join(self.cache_dir, self.image_file_name(image))
            
