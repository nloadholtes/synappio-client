Onboarding a User
====================


#### Uploading an Email List

As an ESP, it may be useful to know the quality of a potential user's list(s) before accepting them as a customer. This set of instructions will provide a means of doing so.

To vet whether a new user is a good sender or not, send their email lists through DataValidation’s API at onboarding. Retrieve an overview of a user’s list quality to recommend list remediation, or get the full validation results to clean on behalf of the user.

Before you upload a list to the API, a few questions must be answered about the list being uploaded:

1.   Does the csv have include a header on the first row? If yes, the query parameter 'header' should be set to 'true', otherwise 'false'.

2.   What column is the email address in? If the email address is in the first column, the query parameter 'email' should be set to '0'. If the email address is in the second column, it should be set to '1', etc.

3.   Is there data in each row (other than the email address) that you would like to store? You might want to store additional data such as first name, last name, unique ID etc. If so, the query parameter 'metadata' should be set to 'true', otherwise 'false'.

4.   Do you have a unique identifier for each email address? 'member_slug' is a unique ID specific to members in a list. If you prefer to specify 'member_slug', set the 'slug_col' query parameter to the column containing your provided identifier in your csv (column 1 = 0). If this parameter is not provided, member slugs will be generated automatically.

Note: Validation results can be retrieved on the member level or the list level. If you intend on accessing individual member grades and not ALL member grades, be sure to include member slugs in your csv. Otherwise, you will have to make a call to '/list/{list_slug}/member/' to retrieve the member_slugs we provide and you will be charged a remediation token for each member in the list.

'member_slug' is a unique ID specific to members in a list. If you prefer to specify 'member_slug', set the 'slug_col' query parameter to the column containing your provided identifier in your csv(column 1 = 0). If this parameter is not provided, member slugs will be generated automatically.


### Create and Import a List

Lists can be created in the API via a .CSV file or via URL. *We recommend that for larger lists, or larger databases, you upload through URL.

For lists imported via .csv file, you'll create the list and import to it in the same command line and you must include all mapping data in the command line. Please note that if you use curl to upload a .csv, you must make sure that the data you're uploading contains newline (\n) characters. Otherwise, the API will interpret your upload as a single (very long!) row.

To create a list using a .csv file, use the endpoint: POST /list

Sample Command:

    $ curl -X POST
    -H "Content-Type: text/csv"
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/\
    ?header=true&email=0&metadata=true&slug_col=2"\
    -d "email_address,first_name,ID,
        foo@example.com,foo,001,
        bar@example.com,bar,002,
        baz@example.com,baz,003,"

Sample Output:

    {
        "list": [
            {
                "status": "new",
                "size": 0,
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/Ko3yuDOI/",
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
                "slug": "Ko3yuDOI",
                "metadata": {}
            }
        ]
    }

**Be sure to store the slug, as this will be needed to access the list in the future.**

If you upload a list via URL, you will need to create an empty list and then import using the URL. Note: You must provide mapping data in the URL parameters.

To create an empty list:

Sample Command:

    curl -X POST -H 'authorization: bearer {list_slug}' "https://api.datavalidation.com/\
    1.0/list/?email=0&header=false&metadata=false"

Sample Output:

~~~~
    {"list": [{"size": 0, "meta": {"href": "http://core-list/list/1.0/list/skjdhfksjdhf/",\
    "links": [{"href": "import/", "rel": "imports"}, {"href": "job/", "rel": "jobs"},\
     {"href": "member/", "rel": "members"}]}, "slug": "T4Vt8OvnQU5fkyo9", "tags": []}]
~~~~

After creating an empty list, then import the the list via download URL.

Sample Command:

    curl -X POST -H "Authorization: bearer {api_key}"
        "https://api.datavalidation.com/1.0/list/{list_slug}/import/" -d
            '{
                "href": "{list_url}",
                "note": "{notes}",
                "mapping": {
                    "header_row": true,
                    "email_col": 0,
                    "include_metadata": false
            }
         }'

Sample Output:

~~~~
    [{"status": "New", "tags": [], "created": "2015-09-02T18:51:10.654000Z", "mapping": {"header_row":\
     false, "email_col":\ 1, "include_metadata": false, "slug_col": 0}, "note": "List Example",\
     "href": "https://www.dropbox.com/s/vqasnxgx77tu77p/email_key_new%202.csv?dl=1", "meta":\
     {"href": "http://core-list/list/1.0/list/6iT4uwzFNYbvj8w1/import/nsJUsuLn/"},\
     "validate": false, "total_imported": 0, "slug": "nsJUsuLn"}]
~~~~

When importing to the empty list (via URL), be sure to include mapping data for URL, header row, email column, metadata, and slug column (if you have one). Use this command to create an import from a URL.

#### Check the Status of an Import

Imports must be 100% complete before starting a job! To check the status of an import, use the endpoint: GET /list/{list_slug}/import/{import_slug}/

Sample Command:

    curl -H 'authorization: bearer {api_key}' "https://api.datavalidation.com/1.0/list/{list_slug}/\
    import/{import_slug}/?pretty=true"


Sample Output:

    {
        "status": "Complete",
        "tags": [],
        "created": "2015-09-02T18:51:10.654000Z",
        "mapping": {
            "header_row": false,
            "email_col": 1,
            "include_metadata": false,
            "slug_col": 0
        },
        "note": "Example Import",
        "href": "https://www.dropbox.com/s/vqasnxgx77tu77p/email_key_new%202.csv?dl=1",
        "meta": {
            "href": "http://core-list/list/1.0/list/6iT4uwzFNYbvj8w1/import/nsJUsuLn/"
        },
        "validate": false,
        "total_imported": 349333,
        "slug": "nsJUsuLn"
    }

List imports must be 100% complete before creating the job that kicks off validation of a list.**

#### To add a single member to an existing list

An ESP may want to add individual subscribers to lists as they get added to user lists within their platform. You can subscribe a single member to a specified existing list (list_slug) by sending a POST request to the appropriate list slug, using the endpoint: /{list_slug}/member/

Sample Command:

    curl -X POST -H "Authorization:bearer {api_key}" -H "Content-Type:application/json" "https://api.datavalidation.com/1.0/list/{list_slug}/member/" -d '{
        "slug": "random-or-user-defined-slug",
        "address": "test@synapp.io",
        "tags": [
            {
                "name": "Test Email",
                "value": "Some value"
            }
        ]
     }'

Sample Output:

    {
        "status": 400,
      "errors": "additionalProperties: Additional properties are not allowed (u'slug' was unexpected)",
        "value": {
         "tags": [
            {
                "name": "Ashley",
                "value": "Some value"
                }
            ],
            "slug": "random-or-user-defined-slug",
            "address": "ashley@synapp.io"
         }
    }

#### To add multiple members to an existing list

ESPs may want to add newly created lists by their users directly to the API, to an existing list within their API account. Adding multiple members to an existing list can be done by POSTing a .csv file to the list or by providing us with a download link (URL) to a .csv file containing the members you want to subscribe.

To add members by POSTing a .csv, send a POST request to the appropriate list slug, using the endpoint: /list/{list_slug}/subscribe.csv

*Please Note: The required parameters are the same as the '/list/' endpoint when using a POST request to create new list. Use the following Parameters:

Parameters:

**header**
* paramType: query
* required: true
* type: boolean
* description: Specifies if there is a header row present in the .csv file

**email_col**
* paramType: query
* required: true
* type: integer
* description: Specifies which column the email address is found in? (0 = first column)

**metadata**
* paramType: query
* required: true
* type: string
* description: Specifies if metadata (non-email) is present in the .csv file (true or false)

**slug_col**
* paramType: query
* required: false
* type: integer
* description: Specifies if a unique identifier is available for the address.
If this is omitted, a slug will be generated automatically for each address.

Sample Command:

    curl -X POST
    -H "Content-Type: text/csv"
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/\
    subscribe.csv?header=true&email=0&metadata=true&member_slug=2"\
    -d "email_address,first_name,ID,
    oof@example.com,oof,005,
    rab@example.com,rab,006,
    baz@example.com,baz,007,"

Sample Output:

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

To add members via download URL, send a POST request to the appropriate list slug, using the endpoint: /{list_slug}/import/. You can subscribe multiple members to an existing list by providing us with a download link to a csv file containing the members you want to subscribe.

Sample Command:

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

Sample Output:

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
            "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZa-\
            gFxG9aiAXbaHeKSk7OoddI9I0lw3LTy8jHwueoSLFvvGn5R4qH7Kzc/import/vYG7J_XT/"
        },
        "slug": "vYG7J_XT"
    }
]
~~~~

Email Assurance, our automated list maintenance solution, runs once a day. We will analyze any new email data in the system on a daily basis, and any existing data in the system on a weekly basis. After creating/importing a new list of addresses, you can 1. Automatically start a validation job when the import is created. 2. Run a validation job after a list import is complete 3. Wait for the daily Email Assurance run to pull in any new email and validate your email list

To **automatically start a validation job** when an import is created, add the parameter "validate=true" when creating the import.

Sample Command:

    $ curl -X POST
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/?email=0&header=false&metadata=false"

Sample Output:

    {"list": [{"size": 0, "meta": {"href": "https://api.datavalidation.com/1.0/\
    list/fwHpJX3E8dTIl6tE/","links": [{"href": "import/", "rel": "imports"},\
    {"href": "job/", "rel": "jobs"}, {"href": "member/", "rel": "members"}]},\
     "slug": "fwHpJX3E8dTIl6tE", "tags":
    []}]}

A Vetting Token will be charged for each member in the list when a job is created.


### Run a Validation Job

After an import is complete, the next step is to create a validation job for the imported list. Note: A Vetting Token will be charged for each member in the list when a job is created. Creating a validation job kicks off the validation process. When the job has finished, the Vetting Tokens consumed will provide you with an overview report of the list's quality.

To start a validation job, use the endpoint: GET /list/{list_slug}/job

Sample Command:

    $ curl -X POST
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/job/"

Sample Output:

    {
        "job": [
            {
                "status": "New",
                "list_slug": "JItNx3th",
                "stats": {},
                "created": "2014-10-15 14:36:21.749000",
                "webhook": {
                    "status": null,
                    "complete": null
                },
                "priority": {
                    "mu": 10,
                    "sigma": 0
                },
                "original_chunks": null,
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/JItNx3th/job/XdH8rZQk/"
                },
                "current_chunks": null,
                "pct_complete": 0,
                "slug": "XdH8rZQk"
            }
        ]
    }


If the list is large or we currently have a large number of list members to validate in our queue, it may take some time to validate the members in your list.

### View the Progress of a Job

To view the progress of a validation job, construct the following request using the job's slug from the above result:

Command:

    $ curl -X GET
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/job/{job_slug}/"


If the job is not finished, you should see a response similar to:

    {
        "job": [
            {
                "status": "New",
                "list_slug": "Ko3yuDOI",
                "stats": {},
                "created": "2014-10-15 15:29:28.335000",
                "webhook": {
                    "status": null,
                    "complete": null
                },
                "priority": {
                    "mu": 10,
                    "sigma": 0
                },
                "original_chunks": null,
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/Ko3yuDOI/job/XLoklKeI/"
                },
                "current_chunks": null,
                "pct_complete": 0,
                "slug": "XLoklKeI"
            }
        ]
    }

Notice the 'pct_complete' field representing the current percent of completion. If the list is large or we currently have a large number of list members to validate in our queue, it may take some time to validate the members in your list.

To view the progress of a validation job, construct the following request using the job's slug from the above result.

### Retrieve Overview Reporting

Viewing a list’s quality will provide you (the ESP) with the necessary information to determine whether a list needs to be validated or not. Overview Reporting is an overview of an email list’s quality. Reporting includes the total number of subscribers in each Email Assurance Grade category: A+, A, B, D, and F, and the number of subscribers that have each Deliverability Code. Deliverability Codes represent the historical deliverability information on subscribers, and together determine a subscriber's Email Assurance Grade.

After a job is complete, repeating the GET request from above will yield a response similar to:

    {
        "job": [
            {
                "status": "Ready",
                "list_slug": "E5RIlS2B",
                "stats": {
                    "optout": {
                        "O4": 3
                    },
                    "grade": {
                        "D": 3
                    },
                    "hard": {
                        "H4": 3
                    },
                    "complain": {
                        "W4": 2,
                        "W3": 1
                    },
                    "trap": {
                        "T4": 2,
                        "T1": 1
                    },
                    "open": {
                        "R0": 3
                    },
                    "click": {
                        "K0": 3
                    },
                    "deceased": {
                        "D4": 3
                    }
                },
                "created": "2014-10-15 20:46:53.218000",
                "webhook": {
                    "status": null,
                    "complete": null
                },
                "priority": {
                    "mu": 10,
                    "sigma": 0
                },
                "original_chunks": 2,
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/E5RIlS2B/job/zJSSU1HE/"
                },
                "current_chunks": 0,
                "pct_complete": 100,
                "slug": "zJSSU1HE"
            }
        ]
    }

 This report does not provide data on specific email addresses.

For ESPs wanting to use the API at Onboarding, follow all of the steps listed above for lists coming into your platform. Starting a validation job will kick off validation and will provide you (the ESP), or your users, with reporting to decide whether or not a list needs to be cleaned.

Performing any of the steps above will consume one Vetting Token per email address. Vetting Tokens are consumed when the validation job is started. If you decide that a user needs to have their list(s) remediated, proceed to exporting results of individual members or a list, or results of lists. By exporting, you will consume one Remediation Token for each member on a list.

API Tokens can be pre-purchased or post-paid, depending on the ESP plan or subscription. To determine how many Vetting Tokens you have consumed, insert -v into the curl command line calling the 'POST/list/{list_slug}/job' endpoint. If any API call consumes tokens, the summary of tokens consumed will be in the x-synappio-tokens-consumed header

For instruction on Remediating a list read the <a href="https://github.com/synappio/synappio-client/blob/master/Cookbooks/Email-Assurance-Cookbook.md" target="_blank">Email Assurance Cookbook.</a>

