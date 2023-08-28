__author__ = "Ernesto"
__email__ = "ernestondieki12@gmail.com"

# pip install plyer
from plyer import notification as n
import os
from time import sleep

os.chdir(os.path.expanduser("~\\Pictures\\icons"))
# not the file extensions (.ico)
default_icon = "message.ico"
giftbox_icon = "giftbox.ico"
birthday_icon = "birthdaycake.ico"
# our notifications format (title, message, icon)
notifications = (("Message from the future",
                  "Food suppliments consumption is going to increase rapidly.",
                  default_icon),
                 ("Upcoming events",
                  "10 days remaining to your friend's birthday.",
                  giftbox_icon),
                 ("Today's events",
                  "Jose has a birthday today.",
                  birthday_icon)
                 )
# for every notification in notifications, grab the title, message and icon
for title, message, icon in notifications:
    n.notify(title=title,
             message=message,
             app_icon=icon)
    # wait for at least 10 seconds before showing the next notification
    sleep(11)
