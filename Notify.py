'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
try:
	import pynotify
	has_pynotify = True
	notifier_reads_markup = 'body-markup' in pynotify.get_server_caps()
except:
	has_pynotify = False
	notifier_reads_markup = False



class Notify():
	def __init__(self):
		pynotify.init('Heybuddy')

	def notify_send(self,summary,content,image):
		notify=pynotify.Notification(summary,content,image)
		if not notify.show():
			print _("Failed to show notification")

	def notify_updates(self,num_updates,avatar):
		summary=_("New updates in timeline")
		content=_("%d new dents in timeline") % (num_updates)
		self.notify_send(summary,content,avatar)

	def notify_reply(self,name,message,image):
		summary=_("%s wrote:") % (name)
		self.notify_send(summary,message,image)

	def notify_updates_replies(self,updates,replies,image):
		summary=_("New updates in timeline")
		content=_("%d new dents in timeline, %d new @replies") % (updates,replies)
		self.notify_send(summary,content,image)

