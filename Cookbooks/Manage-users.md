Managing List Members 
====================

### Adding members to a list:

The DataValidation Batch API provides multiple methods for subscribing new members to an existing list. 

#### To add a single member:

By sending a POST request to the '/{list_slug}/member/', you can subscribe a single member to a specified list (list_slug).

/list/{list_slug}/member/:

Command:

    curl -X POST -H "Authorizaiton: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/member/"
    -d "biz@example.com"

Sample output:

    [
        {
            "updated": "2014-10-15 21:16:56.054000",
            "list_slug": "E5RIlS2B",
            "analysis": {
                "optout": "O4",
                "grade": "D",
                "hard": "H4",
                "click": "K0",
                "trap": "T4",
                "open": "R0",
                "complain": "W4",
                "deceased": "D4"
            },
            "meta": {
                "href": "https://api.datavalidation.com/1.0/list/E5RIlS2B/member/8UKN-s-H/"
            },
            "f_upload": true,
            "address": "biz@example.com",
            "slug": "8UKN-s-H",
            "metadata": {}
        }
    ]



#### To add multiple members:

If you would like to subscribe multiple members to a list at one time, send POST request to the '/list/{list_slug}/subscribe.csv' endpoint. The required parameters are the same as the '/list/' endpoint when using a POST request to create new list.

/list/{list_slug}/subscribe.csv:

Parameters:

              - name: header
                paramType: query
                description: Is there a header row present in the CSV data
                required: true
                type: boolean

              - name: email_col
                paramType: query
                description: Which column is the email address in? (0 = first column)
                required: true
                type: integer

              - name: metadata
                paramType: query
                required: true
                type: string
                format: other
                description: Should the metadata (non-email) in the CSV be stored? (true or false)

              - name: slug_col
                required: false
                paramType: query
                type: integer
                description: The column in the csv containing a slug for each member. If this is omitted, a slug will be generated automatically.

Command:

    curl -X POST
    -H "Content-Type: text/csv"
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/subscribe.csv?header=true&email=0&metadata=true&member_slug=2"
    -d "email_address,first_name,ID,
    oof@example.com,oof,005,
    rab@example.com,rab,006,
    baz@example.com,baz,007,"

Sample output:

    {
        "list": [
            {
                "status": "new",
                "size": 6,
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/E5RIlS2B/",
                    "links": {
                        "jobs": "job/",
                        "batch_subscribe": "subscribe.csv",
                        "member": "member/{member_slug}/",
                        "job": "job/{job_slug}/",
                        "batch_unsubscribe": "unsubscribe.csv",
                        "export": "export.csv",
                        "members": "member/"
                    }
                },
                "slug": "E5RIlS2B",
                "metadata": {}
            }
        ]
    }

#### Adding members via download url:

By using the '/{list_slug}/import/' endpoint, you can subscribe multiple members to an existing list by providing us with a download link to a csv file containing the members you want to subscribe.

/list/{list_slug}/import/:

Command:

~~~~
curl -X POST
-H "Authorization: bearer {api_key}"
-H "Content-Type: application/json"
"https://api.datavalidation.com/1.0/list/{list_slug}/"
-d '{
        "href": {csv_download_url_in_quotes},
        "mapping":
	    {
    		"email_col":0,
		    "slug_col":2,
		    "header_row":true,
		    "include_metadata":false,
	    }
    }'
~~~~

Sample output:

~~~~
[
    {
        "status": "New",
        "created": "2014-10-24T21:52:31.225000Z",
        "mapping": {
            "header_row": true,
            "email_col": 0,
            "include_metadata": false,
            "slug_col": 2
        },
        "note": "",
        "href": {csv_download_url_in_quotes},
        "meta": {
            "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZa-gFxG9aiAXbaHeKSk7OoddI9I0lw3LTy8jHwueoSLFvvGn5R4qH7Kzc/import/vYG7J_XT/"
        },
        "slug": "vYG7J_XT"
    }
]
~~~~

You can now send a GET request to the slug received in the previous request to view the status of the import job.

list/{list_slug}/import/{import_slug}/:

Command:

~~~~
curl -X GET
-H "Authorization: bearer {api_key}"
"https://api.datavalidation.com/1.0/list/{list_slug}/import/{import_slug}/"
~~~~

Output (when complete):

~~~~
[
    {
        "status": "Complete",
        "created": "2014-10-24T21:52:31.225000Z",
        "mapping": {
            "header_row": true,
            "email_col": 0,
            "include_metadata": false,
            "slug_col": 2
        },
        "note": "",
        "href": {csv_download_url_in_quotes},
        "meta": {
            "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZa-gFxG9aiAXbaHeKSk7OoddI9I0lw3LTy8jHwueoSLFvvGn5R4qH7Kzc/import/vYG7J_XT/"
        },
        "slug": "vYG7J_XT"
    }
]
~~~~

To view a list of previous import jobs, send a GET request to the '{list_slug}/import/' endpoint. This endpoint will return a list of all imports jobs that have been run on the list. The list will be in reverse-chronological order (newest first).

list/{list_slug}/import/:

Command:

~~~~
curl -X GET
-H "Authorization: bearer {api_key}"
"https://api.datavalidation.com/1.0/list/{list_slug}/import/"
~~~~

Sample output:

~~~~
{
    "imports": [
        {
            "items": [
                {
                    "meta": {
                        "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZa-gFxG9aiAXbaHeKSk7OoddI9I0lw3LTy8jHwueoSLFvvGn5R4qH7Kzc/import/x_jFVU7B/"
                    }
                },
                {
                    "meta": {
                        "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZa-gFxG9aiAXbaHeKSk7OoddI9I0lw3LTy8jHwueoSLFvvGn5R4qH7Kzc/import/vYG7J_XT/"
                    }
                }
            ],
            "paging": {
                "skip": 0,
                "total": 2,
                "limit": 2
            },
            "meta": {
                "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZa-gFxG9aiAXbaHeKSk7OoddI9I0lw3LTy8jHwueoSLFvvGn5R4qH7Kzc/import/",
                "links": [
                    {
                        "href": "{slug}/",
                        "rel": "item"
                    }
                ]
            }
        }
    ]
}
~~~~

To clean up the list of import jobs correlating to a list, send a DELETE request to the 'import/{import_slug}/' endpoint to remove a specific import job entry.

/list/{list_slug}/import/{import_slug}/:

Command:

~~~~
curl -X DELETE
-H "Authorization: bearer {api_key}"
"https://api.datavalidation.com/1.0/list/{list_slug}/import/{import_slug}/"
~~~~

Response:
~~~~
204: No Content
~~~~

After sending this request, you will notice that your list of import jobs no longer contains the entry you have deleted.


### Removing members from a list:

The DataValidation Batch API provides two methods for unsubscribing members from a list.

#### To unsubscribe a single member from a list:

By sending a DELETE request to the '/member/{member_slug}' endpoint, a single member of a list can be unsubscribed.

/list/{list_slug}/member/{member_slug}/:

Command:

    curl -X DELETE -H "Authorization: bearer {api_key}" "https://api.datavaliadtion.com/1.0/list/{list_slug}/member/{member_slug}"

Response:

    204: No Content


#### To unsubscribe multiple members from a list:

By sending a POST request to /{list_slug}/unsubscribe.csv endpoint, you can specify multiple members to be unsubscribed by passing a csv list of members to remove.

/list/{list_slug}/unsubscribe.csv:

Parameters:

              - name: header
                paramType: query
                description: Is there a header row present in the CSV data
                required: true
                type: boolean
            
              - name: slug_col
                required: true
                paramType: query
                type: integer
                description: The column in the csv containing the slug for each member.

Command:

                curl -X POST
                -H "Content-Type: text/csv"
                -H "Authorization: bearer {api_key}"
                   "https://api.datavalidation.com/1.0/list/{list_slug}/unsubscribe.csv?header=true&slug_col=2"
                -d "email_address,first_name,ID,
                    oof@example.com,oof,005,
                   rab@example.com,rab,006,
                   zab@example.com,zab,007"

Sample output:

    {
    "list": [
        {
            "status": "new",
            "size": 3,
            "meta": {
                "href": "https://api.datavalidation.com/1.0/list/E5RIlS2B/",
                "links": {
                    "jobs": "job/",
                    "batch_subscribe": "subscribe.csv",
                    "member": "member/{member_slug}/",
                    "job": "job/{job_slug}/",
                    "batch_unsubscribe": "unsubscribe.csv",
                    "export": "export.csv",
                    "members": "member/"
                }
            },
            "slug": "E5RIlS2B",
            "metadata": {}
        }
    ]
    }

