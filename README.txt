HEYBUDDY
========
Heybuddy is a *supposedly* light, feature free, identi.ca client licensed under GNU GPL v3.

<http://www.jezra.net/projects/heybuddy>  


REQUIREMENTS
------------
Heybuddy is written in the Python language and has the following requirements:  

* Python
* PyGTK (some distributions package it under the name pygtk2, some under just pygtk)
* GTK
* Python-gtkspell (optional)

**ENABLING SPELL CHECK**: Spell checking is supported if Aspell and the optional Python-gtkspell module are installed.

**ENABLING NOTIFICATIONS**: Sending notifications is supported if the python-notify module is installed. Some sort of notification display application will need to be installed to view the notifications that Heybuddy sends. Thanks @x1101 for the notification code. 

USAGE
-----
**CONNECTING TO YOUR ACCOUNT**   
In the Accounts tab, enter your identi.ca user name and password.  Heybuddy will start pulling your dents and you can start sending dents.

**SENDING A DENT**   
At the bottom of the Heybuddy window is the text area. To send a dent, simply type your message and hit return. 

**KEYBOARD SHORTCUTS**   
CTRL+u: set focus on the 'update status' field  
CTRL+l: clear and set focus on the 'update status' field  
CTRL+w: closes the window when in 'run as tray app' mode   
CTRL+q: quit
CTRL+page up/page down: navigate tabs
CTRL+arrow up/arrow down: scroll up/down

TABS
----

**Dents**  
The Dents tab will show your personal time line. Here you will see your dents, and the dents of people or groups you follow.  

**Mentions**   
The Mentions tab will show dents with your @username in them.

**Directs**  
The Directs tab will display dents sent to you that are *for your eyes only*.  To reply to a direct dent simply click the direct button. 

To initiate a direct dent, start by clicking on the users name.  This will bring you to the User Tab where you'll find a Direct Button.  Clicking the direct button will bring you to the Directs Tab and you should now see "Direct Message To User" above the input field.  Enter your message and the dent will be sent privately. 

**Context**  
Clicking on *Context* in any dent will bring you to the Context tab. The whole conversation that dent belongs to will be pulled in, starting with the most recent, and finishing with the earliest dent of the conversation.

**User**  
Clicking on a user's name will open up the User tab.  You will then see recent dents by that user.  There are also options to follow/un-follow, or block the user. 

**Group**  
Clicking on a group tag inside a dent will open the Group tab. You can then see all dents for that group as well as the option to join/leave the group.

**Settings**  
Account: Manage your Identi.ca account settings.  You can set a custom Status.net instance in the Service field.  

Options: Select options for how you would like Heybuddy to behave.

Number of dents at start-up: The Number of dents that are pulled in when Heybuddy first starts up.

Update interval: The Interval of time before the next pull. (A new Interval will take effect after the next pull.)

Link color: The default link color may not work well with your theme. To change it, type the name or HTML code of the color you would rather use in the Link Color field. Heybuddy will start using that color for future dents. 

Filters: Filter dents by a Username or String.
 
For Example: 

* Suppose someone you follow is excited about their new vuvuzela and they constantly post about it and tag their posts with #vuvuzela or !vuvuzela. Entering "vuvuzela" in the String Filter will block all dents containing "vuvuzela" from displaying in your "Dents" tab. 
Thanks @fabsh for making this a necessity during #wc2010.

**About**
See some information about Heybuddy.

OTHER
-----

**History**
The glasses icon: The project name was inspired by Jezra's friend who says, "Hey Buddy" a lot:

<http://www.jezra.net/images/gallery/red_glasses.jpg>

###Thank You###
Heybuddy wouldn't have been possible without users, testers, and bug reporters. Thank you one and all.

If you really really really want to submit a feature request, send the request via postcard to: 
Jezra 
P.O. Box 933 
Petaluma, CA 94953

