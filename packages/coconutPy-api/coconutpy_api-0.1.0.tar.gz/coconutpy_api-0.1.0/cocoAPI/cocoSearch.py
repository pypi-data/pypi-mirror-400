from cocoAPI.cocoBase import cocoBase
from cocoAPI import default_search_requests
import time


class cocoSearch(
                 cocoBase
                 ):
   """
   Class for COCONUT API search endpoints.
   """
   def __init__(
                self,
                cocoLog
                ):
      # inherits session, api_url
      super().__init__(cocoLog)

      # default search request body
      self.default_citations_search_req = default_search_requests.default_citations_search_req
      self.default_collections_search_req = default_search_requests.default_collections_search_req
      self.default_molecules_search_req = default_search_requests.default_molecules_search_req
      self.default_organisms_search_req = default_search_requests.default_organisms_search_req
      self.default_properties_search_req = default_search_requests.default_properties_search_req
      self.default_reports_search_req = default_search_requests.default_reports_search_req


   def query(
             self,
             resource_endpoint,
             search_query,
             sleep_time = 0
             ):
      """
      Performs COCONUT search request and returns the json response.

      Parameters
      ----------
      resource_endpoint
         COCONUT resource to search
      search_query
         List of entries, where each entry has format [key, field, value]
      sleep_time
         Time to sleep between requests to avoid rate limiting

      Returns
      -------
      dict
         Complete results from search request
      error
         Raises errors if found
      """
      # check search query
      self._check_search_query(
                               resource_endpoint = resource_endpoint,
                               search_query = search_query
                               )

      # build search request
      self.search_req = self._build_search_req(
                                               resource_endpoint = resource_endpoint,
                                               search_query = search_query
                                               )

      # execute search request
      return self._paginate_search_data(
                                        endpoint = f"{resource_endpoint}/search",
                                        json_body = self.search_req,
                                        sleep_time = sleep_time
                                        )


   def _check_search_query(
                           self,
                           resource_endpoint,
                           search_query
                           ):
      """
      Performs several checks on `search_query` to ensure correct format.

      Parameters
      ----------
      resource_endpoint
         COCONUT API endpoint to search
      search_query
         List of entries, where each entry has format [key, field, value]

      Returns
      -------
      error
         Raises errors if found
      """
      # check `search_query` structure
      if not isinstance(
                        search_query,
                        list
                        ) or not all(
                                     isinstance(
                                                entry, list
                                                ) and len(entry) == 3 
                                     for entry in search_query
                                     ):
         raise TypeError(
                         "`search_query` must be a list of [key, field, value]"
                         )

      # use default search request to get keys & fields
      attr_name = f"default_{resource_endpoint}_search_req"
      resource_search_req = getattr(
                                    self,
                                    attr_name, 
                                    None
                                    )

      # check keys
      resource_keys = resource_search_req["search"].keys()
      if not all(
                 entry[0] in resource_keys
                 for entry in search_query
                 ):
         raise ValueError(
                          f"keys must be a one of: {resource_keys}"
                          )

      # check fields; list needed to append None
      resource_fields = list(
                             self._get(
                                       endpoint = resource_endpoint
                                       )["data"]["fields"]
                             )
      resource_fields.append(
                             None
                             )
      if not all(
                 entry[1] in resource_fields
                 for entry in search_query
                 ):
         raise ValueError(
                          f"fields must be a one of: {resource_fields}"
                          )

      # check values
      for entry in search_query:
         if entry[0] == "select":
            if not isinstance(
                              entry[2],
                              None
                              ):
               raise ValueError(
                                f"for select entry, value must be None"
                                )
         if entry[0] == "page" or entry[0] == "limit":
            if entry[1] is not None:
               raise ValueError(
                                f"for `page` or `limit` key, field must be None"
                                )
            if not isinstance(
                              entry[2],
                              int
                              ):
               raise ValueError(
                                f"for `page` or `limit` key, value must be integer"
                                )


   def _build_search_req(
                         self,
                         resource_endpoint,
                         search_query
                         ):
      """
      Builds search request from a `search_query` list of entries, where each entry has format [key, field, value].

      Parameters
      ----------
      resource_endpoint
         COCONUT API endpoint to search
      search_query
         List of entries, where each entry has format [key, field, value]

      Returns
      -------
      dict
         Search request from `search_query`
      """
      # init search_request
      search_req = {
                    "search": {}
                    }
      for entry in search_query:
         key, field, value = entry
         if key in ["filters", "sorts", "selects"]:
            if key == "filters":
               search_req["search"].setdefault(
                                               "filters",
                                               []
                                               ).append(
                                                        {
                                                         "field": field,
                                                         "operator": "=",
                                                         "value": value
                                                         }
                                                        )
            elif key == "sorts":
               search_req["search"].setdefault(
                                               "sorts",
                                               []
                                               ).append(
                                                        {
                                                         "field": field,
                                                         "direction": value
                                                         }
                                                         )
            elif key == "selects":
               search_req["search"].setdefault(
                                               "selects", []
                                               ).append(
                                                        {
                                                         "field": field
                                                         }
                                                        )
         else:
            # simple key like "page", "limit"
            search_req["search"][key] = value
      return search_req


   def _paginate_search_data(
                             self,
                             endpoint,
                             json_body,
                             sleep_time
                             ):
      """
      Performs pagination on the data returned from the COCONUT API search request.

      Parameters
      ----------
      endpoint
         COCONUT API endpoint
      json_body
         JSON body for the search request
      sleep_time
         Time to sleep between requests to avoid rate limiting

      Returns
      -------
      dict
         Complete results from the COCONUT API search request
      error
         Raises errors if found
      """
      # checks
      if not isinstance(
                        json_body,
                        dict
                        ):
         raise TypeError(
                         "`json_body` must be a dictionary."
                         )

      # pagination input
      # create copy to modify page
      # create page if not present; page is below search
      json_copy = json_body.copy()
      json_copy.setdefault(
                           "search",
                           {}
                           ) \
               .setdefault(
                           "page",
                           1
                           )

      # paginate
      all_data = []
      while True:
         # progress
         curr_pg = json_copy["search"]["page"]

         # request
         response = self._post(
                               endpoint = endpoint,
                               json_body = json_copy
                               )

         # data
         pg_data = response.get(
                                "data",
                                []
                                )
         if not pg_data:
            print(
                  f"Warning: Empty data returned on page {curr_pg}. Pagination stopped."
                  )
            break
         all_data.extend(
                         pg_data
                         )

         # update progress
         last_pg = response["last_page"]
         print(
               f"Retrieved page {curr_pg} of {last_pg}.",
               end = "\r",
               flush = False
               )

         # check progress
         if curr_pg == last_pg:
            break
         json_copy["search"]["page"] += 1

         # sleep to avoid rate limiting
         time.sleep(sleep_time)

      # return json data
      return all_data


   def get_all_records(
                       self,
                       resource_endpoint,
                       pg_limit = 25,
                       sleep_time = 0
                       ):
      """
      Get all records from COCONUT API endpoint to search.

      Parameters
      ----------
      resource_endpoint
         COCONUT API endpoint to search
      pg_limit
         Number of results per page
      sleep_time
         Time to sleep to avoid rate limiting

      Returns
      -------
      dict
         Complete results from search request
      error
         Raises errors if found
      """
      # request json 
      all_records_req = {
                         "search": {
                                    "filters": [],
                                    "page": 1,
                                    "limit": pg_limit
                                    }
                         }

      # request data
      all_records_data = self._paginate_search_data(
                                                    endpoint = f"{resource_endpoint}/search",
                                                    json_body = all_records_req,
                                                    sleep_time = sleep_time
                                                    )

      # return data
      return all_records_data
