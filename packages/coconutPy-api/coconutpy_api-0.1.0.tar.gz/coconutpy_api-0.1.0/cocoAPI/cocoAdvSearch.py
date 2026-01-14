from this import d
from cocoAPI.cocoBase import cocoBase
from cocoAPI import default_search_requests
import copy
import time


class cocoAdvSearch(
                    cocoBase
                    ):
   """
   Class for COCONUT API advanced search endpoint.
   """
   def __init__(
                self,
                cocoLog
                ):
      # inherits session, api_url
      super().__init__(cocoLog)

      # default search request body
      self.adv_mol_search_info = default_search_requests.adv_mol_search_info
      self.adv_mol_search_types = [
                                   "tags",
                                   "filters",
                                   "basic"
                                   ]
      self.default_adv_mol_search_req = self.adv_mol_search_info["search"]


   def advanced_query(
                      self,
                      adv_search_query,
                      sleep_time: int = 0,
                      pg_limit: int = 25
                      ):
      """
      Runs advanced search request from `adv_search_query` and returns the json response.

      Parameters
      ----------
      adv_search_query
         List of entries, where each entry has format [`type`, `tag|filter`, `value`]
      sleep_time
         Time to sleep between requests to avoid rate limiting. Default is 0
      pg_limit
         Number of results per page. Default is 25

      Returns
      -------
      dict
         Complete results from the COCONUT API advanced search request
      error
         Raises errors if found
      """
      # check advanced search query
      self._check_adv_search_query(
                                   adv_search_query = adv_search_query
                                   )

      # build advanced search request
      self._build_adv_search_req(
                                 adv_search_query
                                 )

      # execute advanced search request
      return self._paginate_adv_search_data(
                                            json_body = self.adv_mol_search_req,
                                            sleep_time = sleep_time,
                                            pg_limit = pg_limit
                                            )

   def _check_adv_search_query(
                               self,
                               adv_search_query
                               ):
      """
      Performs several checks on `adv_search_query` to ensure correct format.

      Parameters
      ----------
      adv_search_query
         List of entries, where each entry has format [`type`, `tag|filter`, `value`]

      Returns
      -------
      error
         Raises errors if found
      """
      # check input structure
      if not isinstance(
                        adv_search_query,
                        list
                        ) or not all(
                                     isinstance(
                                                entry,
                                                list
                                                ) and len(entry) == 3
                                     for entry in adv_search_query
                                     ):
         raise TypeError(
                         "`adv_search_query` must be a list of [`type`, `tag|filter`, `value`]"
                         )

      # data
      valid_types = self.adv_mol_search_types
      valid_tags = self.adv_mol_search_info["tags"]
      valid_filters = self.adv_mol_search_info["filters"]
      search_types = []

      # go through entries
      for entry in adv_search_query:
         curr_search_type = entry[0]
         curr_tag_filter = entry[1]
         curr_search_value = entry[2]
         search_types.append(
                             curr_search_type
                             )

         # check type
         if curr_search_type not in valid_types:
            raise ValueError(
                             f"Invalid type: {curr_search_type}. Valid types are: {valid_types}"
                             )

         # check tag
         if curr_search_type == "tags":
            if curr_tag_filter not in valid_tags:
               raise ValueError(
                                f"Invalid tag: {curr_tag_filter}. Valid tags are: {valid_tags}"
                                )

         # check filters
         if curr_search_type == "filters":
            if curr_tag_filter not in valid_filters:
               raise ValueError(
                                f"Invalid filter: {curr_tag_filter}. Valid filters are: {valid_filters}"
                                )

         # check basic query
         if curr_search_type == "basic":
            if curr_tag_filter is not None:
               raise TypeError(
                               "For basic query, tag/filter must be of type None"
                               )
            if not isinstance(
                              curr_search_value,
                              str
                              ):
               raise TypeError(
                               "basic query must be a string of name, SMILES, InChI, or InChI key"
                               )

      # check type count
      if len(
             set(
                 search_types
                 )
             ) > 1:
         raise ValueError(
                          f"Only one type of advanced search allowed, either tag-based, filter-based, or basic."
                          )
      if search_types.count("basic") > 1:
         raise ValueError(
                          f"Only one basic query allowed at the same time"
                          )
      if search_types.count("tags") > 1:
         raise ValueError(
                          f"Only one tag-based query allowed at the same time"
                          )


   def _build_adv_search_req(
                             self,
                             adv_search_query
                             ):
      """
      Builds advanced search request from a `adv_search_query` list of entries, where each entry has format [`type`, `tag|filter`, `value`].

      Parameters
      ----------
      adv_search_query
         List of entries, where each entry has format [`type`, `tag|filter`, `value`]

      Returns
      -------
      dict
         Advanced search request from `adv_search_query`
      error
         Raises errors if found
      """
      # check advanced search query
      self._check_adv_search_query(
                                   adv_search_query
                                   )

      # get search template
      # copy to avoid modifying default search req
      self.adv_mol_search_req = copy.deepcopy(
                                              self.default_adv_mol_search_req
                                              )

      # build advanced search request
      filter_search = None
      filter_query = []
      for entry in adv_search_query:
         curr_search_type = entry[0]
         curr_tag_filter = entry[1]
         curr_search_value = entry[2]

         # build filter-based advanced search request
         if curr_search_type == "filters":
            filter_search = True
            self.adv_mol_search_req["type"] = curr_search_type
            filter_query.append(
                                f"{curr_tag_filter}:{curr_search_value}"
                                )

         # build tag-based advanced search request
         if curr_search_type == "tags":
            self.adv_mol_search_req["type"] = curr_search_type
            self.adv_mol_search_req["tagType"] = curr_tag_filter
            self.adv_mol_search_req["query"] = curr_search_value
            break

         # build basic advanced search request
         if curr_search_type == "basic":
            self.adv_mol_search_req["query"] = curr_search_value
            break

      # build filter-based advanced search request
      if filter_search:
         self.adv_mol_search_req["query"] = " ".join(
                                                     filter_query
                                                     )


   def _paginate_adv_search_data(
                                 self,
                                 json_body: dict,
                                 sleep_time: int = 0,
                                 pg_limit: int = 25
                                 ):
      """
      Performs pagination on the data returned from the COCONUT API advanced search request.

      Parameters
      ----------
      json_body
         JSON body for the advanced search request
      sleep_time
         Time to sleep to avoid rate limiting. Default is 0
      pg_limit
         Number of results per page. Default is 25

      Returns
      -------
      dict
         Complete results from the COCONUT API advanced search request
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
      # assign page and limit if not specified
      adv_mol_search_req_copy = json_body.copy()
      if not adv_mol_search_req_copy.get("page"):
         adv_mol_search_req_copy["page"] = 1
      if not adv_mol_search_req_copy.get("limit"):
         adv_mol_search_req_copy["limit"] = pg_limit

      # paginate
      all_data = []
      while True:
         # progress
         curr_pg = adv_mol_search_req_copy["page"]

         # request
         adv_search_json = self._post(
                                      endpoint = "search",
                                      json_body = adv_mol_search_req_copy
                                      )

         # data
         pg_data = adv_search_json.get(
                                       "data", {}
                                       )\
                                  .get(
                                       "data", []
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
         per_pg = adv_search_json.get(
                                      "data"
                                      )\
                                 .get(
                                      "per_page"
                                      )
         total_recs = adv_search_json.get(
                                          "data"
                                          )\
                                     .get(
                                          "total"
                                          )
         curr_recs = curr_pg * per_pg
         print(
               f"Retrieved {curr_recs} of {total_recs} records",
               end = "\r",
               flush = True
               )

         # check progress
         if curr_recs >= total_recs:
            break
         adv_mol_search_req_copy["page"] += 1

         # sleep to avoid rate limiting
         time.sleep(sleep_time)

      # return data
      return all_data


   def get_all_adv_records(
                           self,
                           pg_limit: int = 25,
                           sleep_time: int = 0
                           ):
      """
      Get all records from COCONUT API advanced search endpoint.

      Parameters
      ----------
      pg_limit
         Number of results per page. Default is 25
      sleep_time
         Time to sleep to avoid rate limiting. Default is 0

      Returns
      -------
      dict
         Complete results from the COCONUT API advanced search request
      error
         Raises errors if found
      """
      # get default search template to retrieve all records
      # empty fields retrieve all records
      adv_mol_search_req_copy = copy.deepcopy(
                                              self.default_adv_mol_search_req
                                              )

      # retrieve all records
      all_data = self._paginate_adv_search_data(
                                                json_body = adv_mol_search_req_copy,
                                                sleep_time = sleep_time,
                                                pg_limit = pg_limit
                                                )

      # return data
      return all_data
