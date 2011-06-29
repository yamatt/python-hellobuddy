'''
this is a part of the heybuddy project
copyright 2010 jezra lickter http://www.jezra.net
'''
import gtk
#this might be on Maemo
try:
	import hildon
	has_hildon = True
except:
	has_hildon = False

#the gtk version may not handle links
if gtk.check_version(2,18,0)!=None:
	links_unavailable=True
else:
	links_unavailable=False

def ScrollThingy() :
  if has_hildon:
    try:
      #this will only work on maemo5; fuck Nokia's shitty documentation
      the_scroll_thing = hildon.PannableArea()
    except:
      # a simple version check would be better, but the documentation is crap
      the_scroll_thing = gtk.ScrolledWindow()
      hildon.hildon_helper_set_thumb_scrollbar(the_scroll_thing, True)
      the_scroll_thing.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
      the_scroll_thing.set_shadow_type(gtk.SHADOW_NONE)
  else:
    the_scroll_thing = gtk.ScrolledWindow()
    the_scroll_thing.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
    the_scroll_thing.set_shadow_type(gtk.SHADOW_NONE)
  return the_scroll_thing
