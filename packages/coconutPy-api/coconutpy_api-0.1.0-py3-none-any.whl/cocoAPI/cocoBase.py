class cocoBase:
   """
   Base class for COCONUT API GET and POST requests.
   """
   def __init__(
                self,
                cocoLog
                ):
      # login attributes
      self.session = cocoLog.session
      self.api_url = cocoLog.api_url

      # login check
      if not cocoLog.token:
         raise RuntimeError(
                            "Authentication required. Please log in using cocoLog"
                            )


   def _get(
            self,
            endpoint,
            params = None
            ):
      """
      Performs GET request to the COCONUT API endpoint.

      Parameters
      ----------
      endpoint
         COCONUT API endpoint
      params
         GET parameters

      Returns
      -------
      dict
         JSON response from the COCONUT API endpoint
      error
         Raises errors if found
      """
      # build url
      url = f"{self.api_url}/{endpoint}"

      # request
      res = self.session.get(
                             url = url,
                             params = params
                             )

      # check response
      res.raise_for_status()

      # return json response
      return res.json()


   def _post(
             self,
             endpoint,
             json_body
             ):
      """
      Performs POST request to the COCONUT API endpoint.

      Parameters
      ----------
      endpoint
         COCONUT API endpoint
      json_body
         JSON body for the POST request

      Returns
      -------
      dict
         JSON response from the COCONUT API endpoint
      error
         Raises errors if found
      """
      # build url
      url = f"{self.api_url}/{endpoint}"

      # request
      res = self.session.post(
                              url = url,
                              json = json_body
                              )

      # check response
      res.raise_for_status()

      # return json response
      return res.json()
