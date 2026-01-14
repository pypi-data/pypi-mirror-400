from cocoAPI.cocoBase import cocoBase

class cocoGet(
              cocoBase
              ):
   """
   Class for COCONUT API GET requests.
   """
   def __init__(
                self,
                cocoLog
                ):
      # inherits session, api_url
      super().__init__(cocoLog)


   def resource_json(
                     self,
                     resource_endpoint
                     ):
      """
      Retrieves resource JSON from the COCONUT API endpoint.

      Parameters
      ----------
      resource_endpoint
         COCONUT API endpoint

      Returns
      -------
      dict
         Resource JSON from the COCONUT API endpoint
      error
         Raises errors if found
      """
      return self._get(
                       endpoint = resource_endpoint
                       )


   def resource_fields(
                       self,
                       resource_endpoint
                       ):
      """
      Retrieves resource fields from the COCONUT API endpoint.

      Parameters
      ----------
      resource_endpoint
         COCONUT API endpoint

      Returns
      -------
      dict
         Resource fields from the COCONUT API endpoint
      error
         Raises errors if found
      """
      return self._get(
                       endpoint = resource_endpoint
                       )["data"]["fields"]
