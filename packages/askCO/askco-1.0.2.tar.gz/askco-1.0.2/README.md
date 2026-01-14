# askCO: search and query records from Te Papa's collections API

This script provides an interface for getting data from the Museum of New Zealand Te Papa Tongarewa. With it, you can run searches and request individual records, which are returned as JSON.

See the [API documentation](https://data.tepapa.govt.nz/docs/) for what's available and how to construct searches.

Te Papa's API requires a registration key in the headers of each request – go to https://data.tepapa.govt.nz/docs/register.html to register. I recommend adding the API key to an environment variable called 'TE-PAPA-KEY', and then calling that from your script to pass to askCO.

## Install and run
Install using pip: `pip install askCO`

askCO requires the `requests` module.

To run a query, import the `AskCO` class, initialise it with your API key, and call the `get_single_record()` or `get_search_results()` methods with the necessary parameters.

## Try running a query
The `tryCO.py` file provides some prepared queries using `search`, `scroll` and various resource endpoints. It calls the API key, sets functional and query parameters, and sets up then runs the request.

You can also enter your own parameters to try out different queries.

## Types of query

### Record
You can get a single record by providing an endpoint and the record's id number.

This will return all the published metadata for the record, such as its title, description, and any associated images.

You can find a record's id number by searching with the API or on Collections Online. In the API, it's in the `id` field, and on CO it's at the end of the record's URL.

[This record's id is 1058008](https://collections.tepapa.govt.nz/object/1058008)

This kind of query doesn't need any extra parameters.

### Related records
You can check any record to see what other records it's related to. For example, the record for an artist will be related to their artworks.

Like a record query, you provide an endpoint and record id number, but because it's a kind of search you can also add some parameters.

The most useful parameter is `types`, which lets you filter the related records to just what you want. If you want to see an artist's related people but not their artworks, you can set `types` to `Person`.

### Searching and scrolling
There are two ways to search for records, `search` and `scroll`. Both kinds of search return all the same information as if you requested each record by itself.

The `search` query mode is what you're usually going to want to use. You can set a search term, various kinds of filters, and specify what fields you want returned. By default, it returns 100 records per page.

`scroll` is good to use when you want to harvest all the available records for your search, such as when you want to export and process the results. The initial query is a lot like a regular `search`, but the following pages are retrieved by pinging a special URL until all records have been returned. `scroll` also defaults to 1000 records per page.

Both search modes return all available records (up to 50,000 for `search`), but you can apply a `record_limit` to avoid getting more data than you need.

## Parameters

### Functional parameters
When initialising the `AskCO` class, you need to provide you `api_key`. This will be used to generate the needed authentication headers.

You can also set:
* `base_url`: defaults to `https://data.tepapa.govt.nz/collection`
* `quiet`: defaults to True

All queries require the following parameter.

* `query_mode`: `record`, `related`, `scroll`, or `search`

You can also set:
* `method`: defaults to `POST` for `scroll`, otherwise `GET`, and you can also set this to `HEAD`
* `record_limit`: On `related`, `scroll`, or `search`, the maximum number of records to return
* `attempts`: How many times to retry a failing query. Defaults to 3
* `timeout`: A tuple used to set an extending delay before timing out. Defaults to (0.5, 3)

### Query parameters
A `record` query only requires two parameters:
* `endpoint`
* `record_id`

For search queries `endpoint` is optional, but if you don't specify one you'll get results for all kinds of record. `record_id` is used for `related` but not `search` or `scroll`.

The valid endpoints are:
* agent
* category
* document
* fieldcollection
* group
* media
* object
* place
* scroll (can't be used for `record` or `related`)
* search (can't be used for `record` or `related`)
* taxon
* topic

Search queries also have a `params` parameter, which are the values that appear after the `?` in the query URL.

These include:
* `query`: Your search term, which is joined to any filters you provide. Defaults to "*"
* `size`: How many records you want to return in a page. Defaults to 100 for `search` and `related`, and 1000 for `scroll`
* `filters`: See below. Defaults to no filters
* `facets`: Not yet implemented
* `fields`: Which fields to return - useful if you know exactly what you need. Defaults to all available fields
* `from`: Used when paging through results, but can be manually set if you want to skip ahead
* `sort`: How to order your results - for example, "meta.modified" sorts by oldest first, and "-meta.modified" sorts by newest first. Defaults to the API's quality score
* `types`: Used for `related` queries, letting you filter to particular kinds of records, eg Object, Person, Category
* `duration`: Used for `scroll` queries, the length of time the scroll endpoint is kept alive in minutes. Defaults to 1 minute

### Query filters
On `search` and `scroll` queries you can filter your search results by adding fields and values to the `filters` parameter.

Some of the most useful filters are:
* `collection`: eg Art, PacificCultures, FossilVertebrates
* `type`: the main type of the record, eg Object, Specimen, Person
* `additionalType`: a more narrowly-defined type, eg PreservedSpecimen on a Specimen record
* `identifier`: the registration number for the item, eg RB001679 - helpful when you want to find a record but don't know its id number
* `hasRepresentation.rights.allowsDownload`: set to "true" to only return records with images that can be downloaded

Set up your filters as a list of dictionaries:

```
"filters": [
    {"type": "equals",
     "field": "collection",
     "value": "Photography"},
    {"type": "equals",
     "field": "hasRepresentation.rights.title",
     "value": "No Known Copyright"}
     ]
```

Filters get applied as `AND` predicates by default, but you can use others, as well as nest predicates.

```
"filters": [
    {"type": "in",
     "field": "collection",
     "value": [
        "Plants",
        "Photography"]
        },
    {"type": "not",
     "predicate": 
        {"type": "equals",
         "field": "_exists_",
         "value": "hasRepresentation"}
         }
    ]
```

When you supply a list of values with an `IN` predicate, they'll be sent through as a series of `OR` statements for that field.

Boolean filter values get turned into strings to make them work, and string values get put in quotes. This also lets you use spaces, slashes, and other special characters in your filter values.

Keep in mind that not all fields can be filtered - most nested fields like `production.contributor.title` or `identification.toTaxon.qualifiedName` aren't indexed to allow this. However, the values are still used when searching in general so you can include them in your query.

### Query facets
Faceting is not implemented in askCO yet.

[Faceting with the Te Papa API](https://github.com/te-papa/collections-api/wiki/Search-strategies#faceting)

## Returned objects
Individual `record` queries return both the Requests response object and the JSONified data.

```
response, record = askco.get_single_record(endpoint="object", record_id=123456...)
```

Search queries yield each page of results, providing the Requests response object and the JSONified results.

```
for response, results in askco.get_search_results(endpoint="object", params={"query": "cat", "filters"...}...):
    # process each page of results
```

The `results` JSON can be easily split into parts:

```
records = results.get("results")
facets = results.get("facets")
metadata = results.get("_metadata")
```

This gives you access to all the details of the Requests response, while also making it easy to work directly with the data.