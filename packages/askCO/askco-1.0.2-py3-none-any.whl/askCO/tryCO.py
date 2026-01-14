import os
import json
from __init__ import AskCO


# Register for an API key at https://data.tepapa.govt.nz/docs/register.html
# Save it to the environment variable "TE-PAPA-KEY"
api_key = os.environ.get("TE-PAPA-KEY")

# Set functional parameters
quiet = False
timeout = (0.5, 3) # Tuple used to allow extended backoff on retries
attempts = 3

# Use one of these queries below in try_query()
prepared_queries = {"search_wellington": {"query_mode": "search",
                                          "endpoint": "object",
                                          "query": "wellington",
                                          "filters": [{"type": "equals",
                                                       "field": "collection",
                                                       "value": "Photography"},
                                                      {"type": "equals",
                                                       "field": "hasRepresentation.rights.title",
                                                       "value": "No Known Copyright"}],
                                          "record_limit": 500
                                          },
                    "search_aroha": {"query_mode": "search",
                                     "endpoint": "agent",
                                     "query": "aroha",
                                     "filters": [{"type": "equals",
                                                  "field": "type",
                                                  "value": "Person"}]
                                      },
                    "search_algae_no_images": {"query_mode": "search",
                                               "endpoint": "object",
                                               "query": "algae",
                                               "filters": [{"type": "in",
                                                            "field": "collection",
                                                            "value": ["Plants", "Photography"]},
                                                           {"type": "not",
                                                            "predicate": {"type": "equals",
                                                                          "field": "_exists_",
                                                                          "value": "hasRepresentation"}}]},
                    "scroll_plants": {"query_mode": "scroll",
                                      "endpoint": "object",
                                      "query": "Angiosperms",
                                      "filters": [{"type": "equals",
                                                   "field": "collection",
                                                   "value": "Plants"},
                                                  {"type": "equals",
                                                   "field": "type",
                                                   "value": "Specimen"}],
                                      "record_limit": 10000
                                      },
                    "scroll_fashion": {"query_mode": "scroll",
                                       "endpoint": None,
                                       "query": "fashion",
                                       "filters": [{"type": "equals",
                                                    "field": "_exists_",
                                                    "value": "hasRepresentation"},
                                                   {"type": "equals",
                                                    "field": "hasRepresentation.rights.allowsDownload",
                                                    "value": True}],
                                       "fields": ["id", "title", "collection", "production", "depicts", "creditLine"]
                                       },
                    "resource_opo": {"query_mode": "resource",
                                     "endpoint": "object",
                                     "record_id": 742452
                                     },
                    "resource_related": {"query_mode": "related",
                                         "endpoint": "agent",
                                         "record_id": 6190,
                                         "filters": [{"type": "equals",
                                                      "field": "types",
                                                      "value": "Object"}],
                                         "record_limit": 300
                                         }
                    }


def try_query():
	# Choose an option from the prepared_queries dict above or fill in
	# your own query details below
	query_details = prepared_queries["search_wellington"]
	# query_details = None
	if not query_details:
		query_details = {"query_mode": None,
		                 "endpoint": None,
		                 "record_id": None,
		                 "query": None,
		                 "filters": None,
		                 "fields": None,
		                 "record_limit": None}

	if query_details.get("query_mode") == "resource":
		try_resource(query_details)
	else:
		try_search(query_details)


def try_resource(query_details):
	# Create API interface object
	askco = AskCO(api_key=api_key,
	              quiet=quiet)

	# Set the search request's functional details
	query_mode = query_details.get("query_mode")
	endpoint = query_details.get("endpoint")
	record_id = query_details.get("record_id")
	method = query_details.get("method")
	if not method:
		method = "GET"

	response, record = askco.get_single_record(endpoint=endpoint,
	                                           record_id=record_id,
	                                           method=method,
	                                           query_mode=query_mode,
	                                           attempts=attempts,
	                                           timeout=timeout)

	if record:
		print("Here's the record you requested:")
		print(record.get("id"), record.get("title"))
		formatted_record = json.dumps(record, indent=4)
		print(formatted_record)
	else:
		print("No record found for this endpoint and record id")


def try_search(query_details):
	# Create API interface object
	askco = AskCO(api_key=api_key,
	              quiet=quiet)

	# Set the search request's functional details
	query_mode = query_details.get("query_mode")
	endpoint = query_details.get("endpoint")
	record_id = query_details.get("record_id")
	record_limit = query_details.get("record_limit")

	# You can also use "HEAD" and "OPTIONS" methods, but we'll keep it simple for now
	if query_mode == "scroll":
		method = "POST"
	else:
		method = "GET"

	# Set the request parameters
	if query_mode == "scroll":
		params = {"size": 1000,
		          "duration": 1}
	else:
		params = {"size": 100}

	if query_details.get("query"):
		params.update({"query": query_details.get("query")})

	if query_details.get("filters"):
		params.update({"filters": query_details.get("filters")})

	if query_details.get("fields"):
		params.update({"fields": query_details.get("fields")})

	search_result_record_count = 0
	search_results = []
	for response, results in askco.get_search_results(endpoint=endpoint,
	                                                  record_id=record_id,
	                                                  method=method,
	                                                  params=params,
	                                                  query_mode=query_mode,
	                                                  attempts=attempts,
	                                                  timeout=timeout,
	                                                  record_limit=record_limit):

		records = results.get("results")
		# Faceting is not implemented yet
		facets = results.get("facets")
		metadata = results.get("_metadata")

		if not search_result_record_count:
			search_result_record_count = metadata.get("resultset").get("count")
			print(f"{search_result_record_count} records found for your search")
		if records:
			first_record = records[0]
			print("First record on this page:")
			print(first_record.get("id"), first_record.get("title"))
			search_results.extend(records)

	if search_results:
		print("Here's the first few records for your search:")
		print_limit = 3
		if len(search_results) < print_limit:
			print_limit = len(search_results)
		for i in range(print_limit):
			print_record = search_results[i]
			formatted_record = json.dumps(print_record, indent=4)
			print(formatted_record)
	else:
		print("No records found for this search")


if __name__ == "__main__":
	try_query()
