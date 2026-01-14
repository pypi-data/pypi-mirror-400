import time
from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AskCO:
	def __init__(self,
	             base_url="https://data.tepapa.govt.nz/collection",
	             api_key=None,
	             quiet=True):
		self.base_url = base_url.rstrip("/")
		self.api_key = api_key
		self.quiet = quiet
		self.headers = self._prepare_headers()

		self.valid_endpoints = ["agent",
		                        "category",
		                        "document",
		                        "fieldcollection",
		                        "group",
		                        "media",
		                        "object",
		                        "place",
		                        "scroll",
		                        "search",
		                        "taxon",
		                        "topic"]

		self.search_defaults = {"from": 0,
		                        "size": 100}

		if not self.quiet:
			print("Ready to query Te Papa's API")

	def _prepare_headers(self):
		if not self.api_key:
			raise ValueError("No API key provided")
		return {"x-api-key": self.api_key, "Content-Type": "application/json",
		        "Accept": "application/json;profiles=tepapa.collections.api.v1"}

	def _prepare_request(self, **kwargs):
		if not self.quiet:
			for k, v in kwargs.items():
				print(k, v)

		# Check if the provided endpoint is valid
		endpoint = kwargs.get("endpoint")
		if endpoint:
			if endpoint not in self.valid_endpoints:
				raise ValueError(f"{endpoint} endpoint not valid")

		request_url = None
		request_params = None
		request_body = None
		query_mode = kwargs.get("query_mode")

		match query_mode:
			case "resource":
				if not endpoint:
					raise ValueError("No endpoint provided")

				record_id = kwargs.get("record_id")
				if not record_id:
					raise ValueError("No record_irn provided")

				request_url = f"{self.base_url}/{endpoint}/{record_id}"

			case "related":
				if not endpoint:
					raise ValueError("No endpoint provided")

				record_id = kwargs.get("record_id")
				if not record_id:
					raise ValueError("No record_irn provided")

				request_url = f"{self.base_url}/{endpoint}/{record_id}/related"
				request_params = self._prepare_query_params(kwargs.get("params"))

			case "scroll":
				# Set default scroll parameters before formatting
				if not endpoint:
					endpoint = "search"
				params = kwargs.get("params")
				params["from"] = 0
				if not params.get("duration"):
					params["duration"] = 1
				if not params.get("size"):
					params["size"] = 1000

				request_url = f"{self.base_url}/{endpoint}/_scroll"
				request_params = self._prepare_query_params(params)

				# Todo: Handle POST body creation

			case "search":
				# Set default search parameters before formatting
				params = kwargs.get("params")
				params["from"] = 0
				if not params.get("size"):
					params["size"] = 100

				request_url = f"{self.base_url}/{endpoint}"
				request_params = self._prepare_query_params(params)

		if not self.quiet:
			print(f"Request prepared: {request_url}")
			if request_params:
				print(f"Request parameters: {request_params}")

		return request_url, request_params, request_body

	def _prepare_query_params(self, unformatted_params):
		# Supported parameters:
		# q, from, size, sort, fields, duration (scroll only), types (related only)
		params = {}
		if unformatted_params:
			search_string = unformatted_params.get("query")
			if not search_string:
				search_string = "*"

			for key, value in unformatted_params.items():
				if key == "query":
					pass
				elif key == "filters":
					filter_string = self._format_query_filters(value)
					if filter_string:
						search_string = f"{search_string} {filter_string}"

					if not self.quiet:
						print(f"Complete search string: {search_string}")

				elif isinstance(value, list):
					params[key] = ",".join(value)
				else:
					params[key] = value

			params["q"] = search_string

		for default_key, default_value in self.search_defaults.items():
			if default_key not in params:
				params[default_key] = default_value

		return params

	def _format_query_filters(self, filters):
		# Generate a filter string from a list of filters
		# Filter field names should be camelCase and if nested, separated with "."
		# To filter to records where a particular field is populated, use "_exists_"
		if isinstance(filters, list):
			filter_type = filters[0].get("type")
			if filter_type == "not":
				filter_predicate = "NOT"
			elif filter_type == "or":
				filter_predicate = "OR"
			else:
				filter_predicate = "AND"

			filter_string = self._chain_filter_predicates(filters, predicate=filter_predicate, top_level=True)

		else:
			filter_string = None

		return filter_string


	def _chain_filter_predicates(self, filters, predicate="AND", top_level=False):
		# Run through a list of filters and return a usable string, validating common filters like 'collection'
		filter_string_parts = []
		for filter_element in filters:
			# If no type has been provided, assume equals
			filter_type = filter_element.get("type")
			if not filter_type:
				filter_type = "equals"

			match filter_type:
				case "equals":
					field_field = filter_element["field"]
					filter_value = filter_element["value"]

					# Apply any validations
					if field_field == "collection":
						filter_value = self._validate_collection_filters(filter_value)

					if isinstance(filter_value, bool):
						filter_value = str(filter_value).lower()

					if isinstance(filter_value, str):
						filter_value = f'"{filter_value}"'

					filter_string_parts.append(f"{predicate} {field_field}:{filter_value}")

				case "and":
					child_filters = filter_element["predicates"]
					child_filter_string = self._chain_filter_predicates(child_filters, "AND")
					filter_string_parts.append(f"{predicate} {child_filter_string}")

				case "in":
					# Turns a list of values for a single field into joined OR predicates
					child_filters = [{"type": "equals", "field": filter_element["field"], "value": val} for val in filter_element["value"]]
					child_filter_string = self._chain_filter_predicates(child_filters, "OR")
					filter_string_parts.append(f"{predicate} {child_filter_string}")

				case "not":
					child_filters = filter_element.get("predicates")
					if not child_filters:
						child_filters = [filter_element.get("predicate")]

					child_filter_string = self._chain_filter_predicates(child_filters, "NOT")
					filter_string_parts.append(f"{child_filter_string}")

				case "or":
					child_filters = filter_element["predicates"]
					child_filter_string = self._chain_filter_predicates(child_filters, "OR")
					filter_string_parts.append(f"{predicate} {child_filter_string}")

		# Move _exists_ to the end of the string if present
		for filter_string_part in filter_string_parts:
			if "_exists_" in filter_string_part:
				filter_string_parts.remove(filter_string_part)
				filter_string_parts.append(filter_string_part)

		filter_string = " ".join(filter_string_parts)
		if not top_level:
			if len(filter_string_parts) > 1:
				if filter_string.startswith("AND"):
					filter_string = filter_string[4:]
				if filter_string.startswith("OR"):
					filter_string = filter_string[3:]
				filter_string = f"({filter_string})"

		if not self.quiet:
			print(f"Filter string part: {filter_string}")

		return filter_string

	def _validate_collection_filters(self, query_coll):
		# Collection filter values must be CamelCase with no spaces
		# If collection value(s) provided are invalid, search will run without collection filter
		collections = ["Archaeozoology", "Art", "Birds", "CollectedArchives", "Crustacea", "Fish",
		               "FossilVertebrates", "Geology", "History", "Insects", "LandMammals",
		               "MarineInvertebrates", "MarineMammals", "Molluscs", "MuseumArchives",
		               "PacificCultures", "Philatelic", "Photography", "Plants", "RareBooks",
		               "ReptilesAndAmphibians", "TaongaMāori"]

		if isinstance(query_coll, str):
			if query_coll in collections:
				return query_coll
			else:
				if not self.quiet:
					print(f"Provided collection filter {query_coll} is not valid")

		elif isinstance(query_coll, list):
			valid_colls = []
			for q_coll in query_coll:
				if q_coll in collections:
					valid_colls.append(q_coll)
				else:
					if not self.quiet:
						print(f"Provided collection filter {q_coll} is not valid")
			if valid_colls:
				return valid_colls

		return None

	def get_single_record(self, **kwargs):
		# Request a single record. Requires a valid endpoint and a record_irn
		endpoint = kwargs.get("endpoint")
		if endpoint == ("search" or "scroll"):
			raise ValueError(f"Cannot use {endpoint} endpoint for single record requests")

		method = kwargs.get("method")
		if not method:
			method = "GET"

		request_url, request_params, request_body = self._prepare_request(**kwargs)

		response =  Query(url=request_url,
		                  method=method,
		                  headers=self.headers,
		                  quiet=self.quiet).response

		if response.ok:
			response_json = response.json()
			return response, response_json

		return None, None

	def get_search_results(self, **kwargs):
		# If search or related, prepare the base url using endpoint or endpoint + record id
		# If scroll, prepare the base url and POST body
		query_mode = kwargs.get("query_mode")
		allow_redirects = True
		if query_mode == "scroll":
			allow_redirects = False

		# Ensure method is suitable for the query, but allow user to set "HEAD" or "OPTIONS"
		method = kwargs.get("method")
		if not method:
			if query_mode == ("search" or "related"):
				method = "GET"
			elif query_mode == "scroll":
				method = "POST"

		request_url, request_params, request_body = self._prepare_request(**kwargs)
		scroll_initiated = False

		search_result_record_count = 0
		retrieved_page_count = 0
		retrieved_record_count = 0

		while True:
			page_response = Query(url=request_url,
			                      params=request_params,
			                      method=method,
			                      headers=self.headers,
			                      data=request_body,
			                      allow_redirects=allow_redirects,
			                      quiet=self.quiet).response

			if page_response.ok:
				page_json = page_response.json()
				page_records = page_json.get("results")
				page_metadata = page_json.get("_metadata")

				# Count and yield the page of results
				if page_records:
					if not search_result_record_count:
						search_result_record_count = page_metadata.get("resultset").get("count")
					retrieved_page_count += 1
					retrieved_record_count += len(page_records)

					yield page_response, page_json

					# Break if a record limit was set and has been reached, or all records have been retrieved
					if kwargs.get("record_limit") is not None:
						if retrieved_record_count >= kwargs.get("record_limit"):
							break
					else:
						if retrieved_record_count >= search_result_record_count:
							break

					# Update search or related params with new from param
					if query_mode == "search":
						request_params["from"] += request_params["size"]

					elif query_mode == "related":
						request_params["from"] += request_params["size"]

					# Update scroll after initial POST request
					elif query_mode == "scroll":
						if not scroll_initiated:
							print("Scroll initiated, running further page requests")
							method = "GET"
							scroll_target = page_response.headers.get("Location")
							request_url = f"{self.base_url}{scroll_target}"
							request_params = None
							scroll_initiated = True

				else:
					# If no records in page results, break
					break

			elif page_response.status_code == 429:
				# API rate limit reached - wait and try again
				time.sleep(10)


class Query:
	def __init__(self,
	             url=None,
	             method=None,
	             params=None,
	             headers=None,
	             data=None,
	             allow_redirects=True,
	             stream=False,
	             timeout=(0.5, 3),
	             attempts=3,
	             quiet=True):

		if not method:
			method = "GET"

		# Configure retry strategy
		retry_strategy = Retry(total=attempts,
		                       backoff_factor=1,
		                       status_forcelist=[429, 500, 502, 503, 504],
		                       allowed_methods=["HEAD", "GET", "OPTIONS", "POST"])
		adapter = HTTPAdapter(max_retries=retry_strategy)
		session = Session()
		session.mount("https://", adapter)
		session.mount("http://", adapter)

		if not quiet:
			print(url)
			if params:
				print(params)

		self.response = None

		try:
			if method == "GET":
				self.response = session.get(url=url,
				                            params=params,
				                            headers=headers,
				                            stream=stream,
				                            allow_redirects=allow_redirects,
				                            timeout=timeout)
			elif method == "HEAD":
				self.response = session.head(url,
				                             params=params,
				                             headers=headers,
				                             allow_redirects=allow_redirects,
				                             timeout=timeout)
			elif method == "POST":
				self.response = session.post(url,
				                             params=params,
				                             headers=headers,
				                             allow_redirects=allow_redirects,
				                             timeout=timeout,
				                             data=data)
		except exceptions.ConnectionError as e:
			print(f"Request failed: {e}")
