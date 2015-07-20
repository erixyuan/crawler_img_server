# separator used by search.py, categories.py, ...
SEPARATOR = ";"

LANG            = "en_US" # can be en_US, fr_FR, ...
#ANDROID_ID      = "35e86077c2ed766c"
#ANDROID_ID      = "3855cd23ea0a143d"
#GOOGLE_LOGIN    = "simeji.qa@gmail.com"
#GOOGLE_PASSWORD = "simeji1234"

#3a8b755a2c339205||whoismeddo@gmail.com||BdInt@123||GT-I9300
ANDROID_ID = "3a8b755a2c339205"
GOOGLE_LOGIN = "whoismeddo@gmail.com"
GOOGLE_PASSWORD = "BdInt@123"
DEVICE          = "GT-I9300"
AUTH_TOKEN      = None # "yyyyyyyyy"
#proxies = None

# force the user to edit this file
if any([each == None for each in [ANDROID_ID, GOOGLE_LOGIN, GOOGLE_PASSWORD]]):
    raise Exception("config.py not updated")

