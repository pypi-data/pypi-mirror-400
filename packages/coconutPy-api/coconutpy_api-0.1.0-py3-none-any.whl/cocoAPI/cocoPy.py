from cocoAPI.cocoLog import cocoLog
from cocoAPI.cocoGet import cocoGet
from cocoAPI.cocoSearch import cocoSearch
from cocoAPI.cocoAdvSearch import cocoAdvSearch


class cocoPy:
   """
   Class for COCONUT API.

   Parameters
   ----------
   email
      Email address for COCONUT account
   password
      Password for COCONUT account
   """
   def __init__(
                self,
                email,
                password
                ):
      # create login instance
      self.log = cocoLog()
      self.log.login(
                     email = email,
                     password = password
                     )
      self.get = cocoGet(self.log)
      self.search = cocoSearch(self.log)
      self.advSearch = cocoAdvSearch(self.log)