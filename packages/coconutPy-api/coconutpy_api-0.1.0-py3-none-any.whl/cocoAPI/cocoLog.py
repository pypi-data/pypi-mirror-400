import requests
API_BASE = "https://coconut.naturalproducts.net/api"


class cocoLog:
    def __init__(
                 self
                 ):
       self.api_url = API_BASE.rstrip("/")
       self.session = requests.Session()
       self.logSession = None # store login response
       self.token = None # store access token


    def login(
              self,
              email,
              password
              ):
       """
       Log in to the COCONUT API and store the access token.
       On success, stores the access token and sets the Authorization header.

       Parameters
       ----------
       email
         Email address for COCONUT account
       password
         Password for COCONUT account

       Returns
       -------
       error
         Raises errors if found
       """
       # build login request
       login_post = f"{self.api_url}/auth/login"
       login_json = {
                     "email" : email,
                     "password" : password
                     }

       # request login
       self.logSession = self.session.post(
                                           url = login_post,
                                           json = login_json
                                           )

       # check response
       self.logSession.raise_for_status()

       # get access token
       self.token = self.logSession.json().get(
                                               "access_token"
                                               )

       # update session headers
       if self.token:
          self.session.headers.update(
                                      {
                                       "Authorization": f"Bearer {self.token}"
                                       }
                                      )


    def logout(
               self
               ):
       """
       Log out from the COCONUT API. Clears stored access token and Authorization header.
       """
       # validate login
       if not self.token:
          raise RuntimeError("not logged in")

       # initiate logout
       logout_get = f"{self.api_url}/auth/logout"
       self.logSession = self.session.get(
                                          url = logout_get
                                          )

       # check response
       self.logSession.raise_for_status() # check

       # clear access token and Authorization header
       self.session.headers.pop(
                                "Authorization",
                                None
                                )
       self.token = None