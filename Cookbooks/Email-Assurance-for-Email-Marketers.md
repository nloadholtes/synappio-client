Email Assurance for Email Marketers
====================


### Uploading a List

As an email marketer, you’ll want to make sure you’re sending mail to quality email lists to ensure the best deliverability. Email marketers can upload email lists to the API, receive deliverability reporting to determine whether a list needs remediation or not, and then clean the list of undeliverable email addresses. This set of instructions will provide a means of doing so.

Before you upload a list to the API, a few questions must be answered about the list being uploaded:

1.   Does the csv have include a header on the first row? If yes, the query parameter 'header' should be set to 'true', otherwise 'false'.

2.   What column is the email address in? If the email address is in the first column, the query parameter 'email' should be set to '0'. If the email address is in the second column, it should be set to '1', etc.

3.   Is there data in each row (other than the email address) that you would like to store? You might want to store additional data such as first name, last name, unique ID etc. If so, the query parameter 'metadata' should be set to 'true', otherwise 'false'.

4.   Do you have a unique identifier for each email address? 'member_slug' is a unique ID specific to members in a list. If you prefer to specify 'member_slug', set the 'slug_col' query parameter to the column containing your provided identifier in your csv (column 1 = 0). If this parameter is not provided, member slugs will be generated automatically.

Note: Validation results can be retrieved on the member level or the list level. If you intend on accessing individual member grades and not ALL member grades, be sure to include member slugs in your csv. Otherwise, you will have to make a call to '/list/{list_slug}/member/' to retrieve the member_slugs we provide and you will be charged a remediation token for each member in the list.
'member_slug' is a unique ID specific to members in a list. If you prefer to specify 'member_slug', set the 'slug_col' query parameter to the column containing your provided identifier in your csv(column 1 = 0). If this parameter is not provided, member slugs will be generated automatically.

###Create a List

Lists can be created in the API by importing a .csv file directly or via download URL to the .csv file. **We recommend that for larger lists, or larger databases, you upload through URL.**

**Import via .csv file**

Create the list and import in the same command line. You must include all mapping data in the command line. Please note that if you use curl to upload a .csv, you must make sure that the data you're uploading contains newline (\n) characters. Otherwise, the API will interpret your upload as a single (very long!) row.

To create a list using a .csv file, use the endpoint: POST /list

Sample Command:

    $ curl -X POST
    -H "Content-Type: text/csv
        Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/?header=true&email=0&metadata=true&slug_col=2"
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

Note: Be sure to store the slug, as this will be needed to access the list in the future.

**Import via download URL**

If you import a list via URL, you will need to create an empty list and then import using the download URL. Note: You must provide mapping data in the URL parameters for the email list.

To create an empty list, use the endpoint: POST /list

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

    [{"status": "New", "tags": [], "created": "2015-08-14T15:42:59.009000Z", "mapping":
    {"header_row": true,
    "email_col": 0,
    "include_metadata": false},
    "note": "Test List",
    "href": "https://www.dropbox.com/s/39z6q9kgjjss242/TestList_540.csv?dl=0",
    "meta":
    {"href": "https://api.datavalidation.com/1.0/list/
    fwHpJX3E8dTIl6tE/import/jaRdKHI5/"}, "total_imported": 0,
    "slug": "jaRdKHI5"}
    ]

When importing to the empty list (via URL), be sure to include mapping data for URL, header row, email column, metadata, and slug column (if you have one). Use this command to create an import from a URL.

Sample Command:

    curl -X POST -H "Authorizaiton: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/member/"
    -d "biz@example.com"

Sample Output:

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

**Please Note: The output above shows "total_imported": 0. List imports must be 100% complete before creating the job that kicks off validation of a list.**

### See all of the lists you have created

You can easily retrieve summary or detailed information about all of the lists you’ve created within your API account by calling the endpoint: /list/

~~~~
    curl -X GET
    -H "Authorization: bearer {api_key}"
    -H "Content-Type: application/json"
    "https://api/datavalidation.com/1.0/list/"
~~~~

If you see the response below, then you have not uploaded any lists to your account.

~~~~
    [
    {
        "items": [],
        "paging": {
            "skip": 0,
            "total": 0,
            "limit": 0
        },
        "meta": {
            "href": "https://api.datavalidation.com/1.0/list/",
            "links": [
                {
                    "href": "{slug}/",
                    "rel": "item"
                }
            ]
        }
    }
    ]
~~~~

Once there are lists in your account, you will see something similar to response below.

~~~~
    [
    {
        "items": [],
        "paging": {
            "skip": 0,
            "total": 0,
            "limit": 0
        },
        "meta": {
            "href": "https://api.datavalidation.com/1.0/list/",
            "links": [
                {
                    "href": "{slug}/",
                    "rel": "item"
                }
            ]
        }
    }
    ]
~~~~

#### To add a single member to an existing list

As an email marketer, you most likely have a way for people to sign up for your mailing list. The addresses collected will be subscribed one-by-one and you may wish to add these to an existing list within the API. You can subscribe a single member to a specified existing list by sending a POST request to the appropriate list slug, using the endpoint: /{list_slug}/member/

Sample Command:

    curl -X POST -H "Authorizaiton: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/member/"
    -d "biz@example.com"

Sample Output:

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

#### To add multiple members to an existing list

Email marketers may want to add newly created lists directly to the API, to an existing list within their API account. Adding multiple members to an existing list can be done by POSTing a .csv file to the list or by providing us with a download link (URL) to a .csv file containing the members you want to subscribe.

**To add members by POSTing a .csv**

Send a POST request to the appropriate list slug, using the endpoint: /list/{list_slug}/subscribe.csv
*Please Note: The required parameters are the same as the '/list/' endpoint when using a POST request to create new list.

Use the following Parameters:


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

Sample Command:


    curl -X POST
    -H "Content-Type: text/csv"
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/subscribe.csv?header=true&email=0&metadata=true&member_slug=2"
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

**To add members via download URL**

Send a POST request to the appropriate list slug, using the endpoint: /{list_slug}/import/. You can subscribe multiple members to an existing list by providing us with a download link to a .csv file containing the members you want to subscribe.

Please Note: To add members to an existing list via URL link, you MUST provide a **slug_col** within the specified parameters of the list import.

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
            "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZa-gFxG9aiAXbaHeKSk7OoddI9I0lw3LTy8jHwueoSLFvvGn5R4qH7Kzc/import/vYG7J_XT/"
        },
        "slug": "vYG7J_XT"
    }
]
~~~~

Email Assurance, DataValidation's list maintenance solution, runs once a day. We will analyze any new email data in the system on a daily basis, and any existing data in the system on a weekly basis. After importing a new list of addresses, you can 1. Automatically start a validation job when the import is created 2. Run a validation job after a list import is complete or 3. Wait for the daily Email Assurance run to pull in any new email and validate your email list.

To automatically start a validation job at import, API users should include the additional parameter (listed below) in the curl command for importing via URL. To run a validation job after a list import, **the import must be 100% complete.** To wait for Email Assurance to pick up any new email addresses, or any new email lists, simply create the import for the email data and we'll do the rest!

To automatically start a validation job when an import is created, add the parameter **"validate":true** in the curl command for creating an import via URL.

Sample Command:

    curl -X POST -H "Authorization: bearer {api_key}"
        "https://api.datavalidation.com/1.0/list/{list_slug}/import/" -d
            '{
                "href": "{list_url}",
                "note": "{notes}",
                "validate": true,
                "mapping": {
                    "header_row": true,
                    "email_col": 0,
                    "include_metadata": false
            }
         }'

Sample Output:

[{"status": "New", "tags": [], "created": "2015-08-26T14:12:23.572000Z", "mapping": {"header_row": true, "email_col": 0, "include_metadata": false, "slug_col": 0}, "note": "Click2Sell Onboarding", "href": "https://www.dropbox.com/s/vqasnxgx77tu77p/email_key_new%202.csv?dl=0", "meta": {"href": "http://core-list/list/1.0/list/GKGu8YEKU6IQGzvT/import/yffkMW9l/"}, "validate": true, "total_imported": 0, "slug": "yffkMW9l"}]

A Vetting Token will be charged for each member in the list when the job is automatically created.

### Run a Validation Job

For lists that have been imported (no automatic job created), the next step is to create a validation job for the imported list. Note: A Vetting Token will be charged for each member in the list when a job is created. Creating a validation job kicks off the validation process. When the job has finished, the Vetting Tokens consumed will provide you with an overview report of the list's quality.

To start a validation job, use the endpoint: GET /list/{list_slug}/job

Sample Command:

~~~~
$ curl -X POST
-H "Authorization: bearer {api_key}"
"https://api.datavalidation.com/1.0/list/{list_slug}/job/"
~~~~

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

#### View the Progress of a Job

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

Viewing a list’s quality will provide you with the necessary information to determine whether a list needs to be validated or not. Overview Reporting is an overview of an email list’s quality. Reporting includes the total number of subscribers in each Email Assurance Grade category: A+, A, B, D, and F, and the number of subscribers that have each Deliverability Code. Deliverability Codes represent the historical deliverability information on subscribers, and together determine a subscriber's Email Assurance Grade.

Visit our <a href="http://www.datavalidation.com/kb/12105-What-do-the-codes-in-my-Email-Assurance-Report-mean.html" target="_blank">Knowledge Base</a> for more information on Email Assurance Grades.

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

This report does not provide data on specific email addresses. This is an overview of an email list’s quality. It includes the total number of subscribers in each Email Assurance Grade category (A+, A, B, D, and F) and the number of addresses that have each Deliverability Code.

### Retrieve Validaton Results

After reviewing a list’s quality, it may or may not be necessary to remediate the list. The API provides multiple methods for viewing validation grades for individual members of a list. Note: Retrieving validation results will consume one Remediation Token for each address within a list.

Email marketers can choose to create one list and post separate jobs to this list, or they can create numerous lists with jobs for each. Validation results can be retrieved for all members of a single list, from specific jobs, or for single members of a list.

#### To retrieve individual member grades for ALL members of a list:

This will provide a .csv formatted output including only the member slugs, email addresses, and Email Assurance grades. To retrieve validation results for all members, use the endpoint: GET /list/{list_slug}/export.csv:

Sample Command:

    curl -X GET -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/export.csv"

Sample Output:

    BPopxToE,foo@example.com,D,K0,R0,H4,O4,W3,T4,D4
    FVCExahe,baz@example.com,D,K0,R0,H4,O4,W4,T1,D4
    MPM-h7D1,bar@example.com,D,K0,R0,H4,O4,W4,T4,D4


Using the '/member/' endpoint will provide json formatted output including member slugs, member email addresses, update timestamps as well as any metadata that may have been included in the list.

To retrieve / filter the members of your list use endpoint: /list/{list_slug}/member/. Using the '/member/' endpoint will provide json formatted output including member slugs, member email addresses, update timestamps as well as any metadata that may have been included in the list.

Sample Command:

    curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/list/
    {list_slug}/member/"

Sample Output:

    {
        "members": [
            {
                "updated": "2014-10-15 20:45:13.803000",
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
                    "href": "https://api.datavalidation.com/1.0/list/E5RIlS2B/member/MPM-h7D1/"
                },
                "f_upload": false,
                "address": "bar@example.com",
                "slug": "MPM-h7D1",
                "metadata": {
                    "": "",
                    "first_name": "bar",
                    "email_address": "bar@example.com",
                    "ID": "002"
                }
            },
            {
                "updated": "2014-10-15 20:45:13.802000",
                "list_slug": "E5RIlS2B",
                "analysis": {
                    "optout": "O4",
                    "grade": "D",
                    "hard": "H4",
                    "click": "K0",
                    "trap": "T4",
                    "open": "R0",
                    "complain": "W3",
                    "deceased": "D4"
                },
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/E5RIlS2B/member/BPopxToE/"
                },
                "f_upload": false,
                "address": "foo@example.com",
                "slug": "BPopxToE",
                "metadata": {
                    "": "",
                    "first_name": "foo",
                    "email_address": "foo@example.com",
                    "ID": "001"
                }
            },
            {
                "updated": "2014-10-15 20:45:13.803000",
                "list_slug": "E5RIlS2B",
                "analysis": {
                    "optout": "O4",
                    "grade": "D",
                    "hard": "H4",
                    "click": "K0",
                    "trap": "T1",
                    "open": "R0",
                    "complain": "W4",
                    "deceased": "D4"
                },
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/E5RIlS2B/member/FVCExahe/"
                },
                "f_upload": false,
                "address": "baz@example.com",
                "slug": "FVCExahe",
                "metadata": {
                    "": "",
                    "first_name": "baz",
                    "email_address": "baz@example.com",
                    "ID": "003"
                }
            }
        ]
    }

A Remediation Token will be charged for EACH member in a list when using the '/export.csv' or '/member/' endpoints to retrieve member grades.

#### To retrieve individual member grades from a specific job:

Using the '/{job_slug}/export.csv' endpoint will provide a URL linking to the results of a previous run job. After a job is completed a .csv will be created containing the result data. Accessing this URL will generate a link to an S3 bucket where the .csv file is located. The provided url will be valid for 300 seconds (5 minutes). After this time expires, a new call to this endpoint will generate a new valid link to the csv results. This .csv will contain a header row, and will include the member slug, address, and analysis fields.

To export results from a specific job use the endpoint: /list/{list_slug}/job/{job_slug}/export.csv

Sample Command:

~~~~
curl -X GET
-H "Authorization: bearer {api_key}"
"https://api.datavalidation.com/1.0/list/{list_slug}/job/{job_slug}/export.csv"
~~~~

Sample Output:

~~~~
{
    "href": "https://dv-prod.s3.amazonaws.com/db/20141023/fGilGyUrDnw0bGhfnsnvLfAZhuenLVM9vhFM5d3LZDVWG6udAvRK6o6GVx3vkXNZ/M2V8TPTA-_qZc.csv?Signature=Sdu3I4jq08wvImEsXzfE8TDTUWc%3D&Expires=1414099679&AWSAccessKeyId=AKIAJ6DQJUDEB7L7MRZA"
}
~~~~

**Link Output:**

The link provided for export will provide you with a downloadable .csv file. The file will contain member_slug, email address, Email Assurance Grade, and Deliverability Codes including: clicks, opens, hard bounces, outouts, complaints, spam traps, and deceased individuals. A Remediation Token will be charged for EACH member in a list when using the '/{job_slug}/export.csv' endpoint to retrieve member grades.

~~~~
slug,address,grade,click,open,hard,optout,complain,trap,deceased
R18y23L8,baz@example.com,D,K0,R0,H4,O4,W4,T1,D4
Zl42d0zw,bar@example.com,D,K0,R0,H4,O4,W4,T4,D4
fZS_PEs-,foo@example.com,D,K0,R0,H4,O4,W3,T4,D4
~~~~

A Remediation Token will be charged for EACH member in a list when usling the '/{job_slug}/export.csv' endpoint to retrieve member grades.


#### To retrieve individual grades for a single member of a list:

Retrieving individual grades for a single member of a list will provide validation results for a single address within a list. Using the '/member/{member_slug}/' endpoint will provide output similar to the '/member/' endpoint above but for just a single member.
To retrieve individual member grades, use the endpoint: /list/{list_slug}/member/{member_slug}/

Sample Command:

            curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/list/
            {list_slug}/member/"

Sample Output:

    {
        "members": [
            {
                "updated": "2014-10-15 20:45:13.802000",
                "list_slug": "E5RIlS2B",
                "analysis": {
                    "optout": "O4",
                    "grade": "D",
                    "hard": "H4",
                    "click": "K0",
                    "trap": "T4",
                    "open": "R0",
                    "complain": "W3",
                    "deceased": "D4"
                },
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/E5RIlS2B/member/BPopxToE/"
                },
                "f_upload": false,
                "address": "foo@example.com",
                "slug": "BPopxToE",
                "metadata": {
                    "": "",
                    "first_name": "foo",
                    "email_address": "foo@example.com",
                    "ID": "001"
                }
            }
        ]
    }


A single Remediation Token will be charged for each call to the '/member/{member_slug}' endpoint.


#### Remediating Existing Lists

List maintenance is the key to upholding great deliverability. Using DataValidation’s API, email marketers can monitor the quality of their email lists and always know where they stand prior to sending. List maintenance can be achieved by continuous remediation existing lists.

Email Assurance is DataValidaton's list maintenance solution. We re-validate any existing addresses in our system on a weekly basis, and any new addresses on a daily basis. Email Assurance generally runs at 10pm EST everyday.

If new addresses have been added to existing lists within the API, Email Assurance will pick them up that same day after 10pm EST, or you can kick off a validation job for an existing list within your API account. To revalidate an existing list, create a new validation job using the list’s existing list slug.

>Important!

>30 days after a list has been uploaded, list members that have not been updated will be removed from our system, potentially resulting in the absence of some or all list members. If you require remediation of a list that is more than 30 days old, it is important to re-upload the list. If your list is less than 30 days old, the remediation process is the same as above.

### Manage List Members

#### Removing subscribers from a List

After a list has been validated you'll want to remove any undeliverable addresses from the email list. Undeliverable email addresses will have an Email Assurance Grade of F. Some ESPs may recommend that email marketers do not send to any email addresses other than those with Email Assurance Grades of A+ and A (those known to be deliverable). These addresses can be removed as well. When deploying mail to validated addresses, we highly recommend following the best practices and compliance rules stated by your specific ESP.

DataValidation API provides two methods for unsubscribing members from a list.

#### Unsubscribing a Single Member from a List

This command will allow you to remove individual subscribers from email lists by using an address's member slug. To unsubscribe a single member from a list, send a DELETE request to the endpoint: /list/{list_slug}/member/{member_slug}/

Command:

    curl -X DELETE -H "Authorization: bearer {api_key}" "https://api.datavaliadtion.com/1.0/list
    /{list_slug}/member/{member_slug}"

Sample output:

    Status code: 204 No Content


#### Unsubscribe Multiple Members from a List:

This will allow you to remove multiple members from a list at once by POSTing a .csv of addresses that you'd like to unsubscribe. After validating a list, specify multiple members to be unsubscribed by passing a .csv list of members to: /{list_slug}/unsubscribe.csv
Parameters:

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

Sample Command:

    curl -X POST
    -H "Content-Type: text/csv
        Authorization: bearer {api_key}"
        "https://api.datavalidation.com/1.0/list/{list_slug}/unsubscribe.csv?header=true&slug_col=2"
    -d "email_address,first_name,ID,
        oof@example.com,oof,005,
        rab@example.com,rab,006,
        zab@example.com,zab,007"

Sample Output:

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

#### API Token Consumption

API Tokens can be pre-purchased or post-paid, depending on the ESP plan or subscription. To determine how many Remediation Tokens you have consumed, insert -v into a curl command that consumes tokens (ie. when running a validation job or exporting validated results). If any API call consumes tokens, the summary of tokens consumed will be in the x-synappio-tokens-consumed header.

### Email Assurance for Email Marketers

This API allows email marketers to retrieve list level data and quickly view the data quality on an email list. Every email address is scanned on a list and you are provided an Email Assurance Report. This report is an overview of an email list’s quality. It includes the total number of subscribers in each grade category: A+, A, B, D, and F, and the count of addresses with each Deliverability Code.

Email marketers can use this reporting to assess the quality of an email list, and to decide whether it needs to be cleaned or not. If a list needs remediation, marketers can easily download the results. We highly recommend that email marketers follow the best practices and compliance standards of their specific email service provider.

We also recommend creating a "Safe" segment for A+ and A grades. This should not be a static segment, as every time you update the list members you will want the new A+ and A grades to auto-populate in the segment. This segment allows your users to quickly deploy mail to the deliverable email addresses. You may also want to create segments for B and D grades. An address with a result of B can be upgraded to an A+ if our system detects positive engagement, or downgraded to an F if it detects negative engagement. The same holds true with the D results.

Continuous monitoring and remediation of email lists (in combination with email best practices, such as double opt-in)  is the best way to maintain high list quality and great deliverability as an email sender. Each time someone subscribes to your mailing list, they can automatically be added to an existing list in your API account. If you acquire new mailing lists, you can create and validate these new lists with the API - we’ll monitor the list’s quality and keep each address updated with the most recent deliverability information.

**This is important:**

For email addresses to be maintained with the most recent deliverability information, you must PUT member updates on all the members in your database (within lists) at least once every 30 days. When an email address or list has not been touched in 30 days, we remove it from our database. If this happens, the email list and all members will need to be created in the API again.
This API does not currently support scheduling jobs. You should set up a periodic task in your code to create jobs in the API. These periodic tasks can be utilized to set up ongoing monitoring and ongoing remediation.

Because the grades are being updated daily in our system, you can retrieve the member level grades for all lists daily or weekly. Export.csv does not PUT updates to the members on a list.

This API does not currently support filtering members by grade. After calling export.csv you may want to input this data into your users' accounts and set up a task in your code to automatically unsubscribe the F results.

#### Email Assurance Grades

This grade — A+, A, B, D, or F— indicates an emails likelihood to be deliverable. Additional deliverability data is provided with the grade.
&nbsp;&nbsp;&nbsp;&nbsp;A+ indicates Deliverable + Engagement History
&nbsp;&nbsp;&nbsp;&nbsp;A indicates Deliverable
&nbsp;&nbsp;&nbsp;&nbsp;B indicates Accepts-All
&nbsp;&nbsp;&nbsp;&nbsp;D indicates Indeterminate
&nbsp;&nbsp;&nbsp;&nbsp;F indicates Undeliverable

**Uses of the grades:**

Determine what grades a user can deploy email to - A+ and A results are deliverable based on our most recent data. If a user is a trusted sender, perhaps B results can be allowed. D results should not be deployed email. F results should be unsubscribed.
Emails graded with B or D cannot be confirmed deliverable or undeliverable unless mail is deployed to these codes. You may consider allowing these grades to remain on a user's list with the understanding that they cannot be mailed to unless the grade changes to an A+ or A.

#### Deliverability Codes

In addition to the Email Assurance grade you are provided deliverability data for each email address. This data may influence the Email Assurance grade given to a particular address, and is intended to provide more insight into the deliverability history of the email address.

Deliverability codes are provided on a scale of 1-4, with 1 being the least deliverable and 4 being the most. You may see a 0 associated with Historical Opens (R) and Historical Clicks (K), meaning that we do not have any engagement data on that particular member.

#### Setting Up Email Assurance

The following process should be repeated in order to monitor your list(s) and keep them up to date with respect to new subscribers, unsubscribes, and grade changes. This process should be used if you are setting up daily or weekly monitoring and remediation. Please use this endpoint in place of the list/list_slug/{csv_link}/import endpoint if you are monitoring lists daily or weekly.
Resetting the 'changed' Flag

#### Resetting the Changed Flag

First, you’ll want to reset the ‘changed’ flag on the members of a list. This indicates that the deliverability information on an address has not changed. The following command will set the ‘changed’ flag to ‘false’ for each member in a list.
To reset the ‘changed’ flag, use the endpoint: /list/{list_slug}/member/

Sample Command:

~~~~
    curl -X PATCH
    -H "Authorization: bearer {api_key}"
    -H "Content-Type: application/json"
    "https://api/datavalidation.com/1.0/list/{list_slug}/member/"
    -d '{"changed":false}'
~~~~

Sample Output:

~~~~
    {
        "updated": -1,
        "unsubscribed": 0,
        "subscribed": 0
    }
~~~~

#### Removing Unsubscribes

After resetting the 'changed' flag for list members, you should remove members from a list that have unsubscribed from your mailing list OR have results in an Email Assurance grade of F (undeliverable). The following command will remove specified members from a list by supplying CSV input via POST to the unsubscribe.csv endpoint.

To remove unsubscribes from your list, use the same endpoint as listed previously for unsubscribes: /list/{list_slug}/unsubscribe.csv

Parameters:

~~~~
    name: header
    paramType: query
    description: Is there a header row present in the CSV data
    required: true
    type: boolean

    name: slug_col
    paramType: query
    required: true
    description: The column in the csv containing the slug for each member.
    type: integer
~~~~

Sample Command:

~~~~
    curl -X POST
    -H "Content-Type: text/csv"
    -H "Authorization: bearer {api_key}"
       "https://api.datavalidation.com/1.0/list/{list_slug}/unsubscribe.csv?header=true&slug_col=2"
    -d "email_address,first_name,ID,
        oof@example.com,oof,005,
        rab@example.com,rab,006,
        zab@example.com,zab,007"
~~~~

Sample Output:

~~~~
    {
        "list": [
            {
                "status": "new",
                "size": 3,
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/{list_slug}/",
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
~~~~

#### Adding New Subscribers

Once unsubscribed members have been removed, you will want to add any new subscribers to the existing list. New members can be added to an existing list by posting a .csv file OR by providing a URL link to the .csv file of new subscribers.

The following command will add specified members to a list by supplying CSV input via POST to the subscribe.csv endpoint. To add new subscribers to an existing list via .csv file, use the same command mentioned previously: /list/{list_slug}/subscribe.csv

Parameters:

~~~~
    name: header
    paramType: query
    description: Is there a header row present in the CSV data
    required: true
    type: boolean

    name: email_col
    paramType: query
    description: Which column is the email address in? (0 = first column)
    required: true
    type: integer

    name: metadata
    paramType: query
    description: Should the metadata (non-email) in the CSV be stored? (true or false)
    required: true
    type: string
    format: other

    name: slug_col
    paramType: query
    description: The column in the csv containing a slug for each member. If this is omitted, a slug will be generated automatically.
    required: false
    type: integer
~~~~

Sample Command:

~~~~
    curl -X POST
    -H "Content-Type: text/csv"
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/subscribe.csv?header=true&email=0&metadata=true&member_slug=2"
    -d "email_address,first_name,ID,
        oof@example.com,oof,005,
        rab@example.com,rab,006,
        baz@example.com,baz,007,"
~~~~

Sample Output:

~~~~
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
~~~~

The following command will add specified members to a list by providing a URL link to the .csv file. To add new subscribers to an existing list via URL, use the same command mentioned previously:

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
            "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZa-gFxG9aiAXbaHeKSk7OoddI9I0lw3LTy8jHwueoSLFvvGn5R4qH7Kzc/import/vYG7J_XT/"
        },
        "slug": "vYG7J_XT"
    }
]
~~~~

**Please Note: To add members to an existing list via URL link, you MUST provide a slug_col within the specified parameters of the list import.

### Start a Validation Job

Now that the list has been updated with new subscribers, the next step is to run a validation job. Imports MUST be 100% complete before starting a validation job. Run the validation job the same way specified in the instructions above.

To run validation, send a POST request to the endpoint: /list/job/

Sample Command:

~~~~
$ curl -X POST
-H "Authorization: bearer {api_key}"
"https://api.datavalidation.com/1.0/list/{list_slug}/job/"
~~~~

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

If the list is large or we currently have a large number of list members to validate in our queue, it may take some time to validate the members in your list. To monitor the progress of the job started above, send a GET request to the list/{list_slug}/job/{job_slug}/ endpoint and monitor the 'pct_complete' field. Once this has reached 100, proceed to the next step.

At this point, you only want to retrieve data for members that have changed. This means that an address has a new Email Assurance Grade or newly appended Deliverability Codes since it’s last validation export by you.

To retrieve a list of changed members, send a GET request to the member/{member_slug}/ endpoint and use the changed query parameter.

Sample Command:

~~~~
    curl -X GET
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/member/?changed=true"
~~~~

Sample Output:

~~~~
    {
        "members": [
            {
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/NnKOdJUjjtdNhtQa/member/ftL5TysJ/"
                }
            },
            {
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/NnKOdJUjjtdNhtQa/member/wxM4337f/"
                }
            },
            {
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/NnKOdJUjjtdNhtQa/member/HqghS1Cv/"
                }
            }
        ]
    }
~~~~

If you would like more detailed member output, add the '_expand' query parameter to your GET command.

Sample Command:

~~~~
    curl -X GET
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/member/?changed=true&_expand=true"
~~~~

Sample Output:

~~~~
    {
        "members": [
            {
                "address": "oof@example.com",
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/NnKOdJUjjtdNhtQa/member/ftL5TysJ/"
                },
                "slug": "ftL5TysJ",
                "tags": [],
                "changed": true
            },
            {
                "address": "rab@example.com",
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/NnKOdJUjjtdNhtQa/member/wxM4337f/"
                },
                "slug": "wxM4337f",
                "tags": [],
                "changed": true
            },
            {
                "address": "bar@example.com",
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/NnKOdJUjjtdNhtQa/member/HqghS1Cv/"
                },
                "slug": "HqghS1Cv",
                "tags": [],
                "changed": true
            }
        ]
    }
~~~~

Using the ‘Changed’ flag when monitoring and continuously remediating existing lists is how users of the API can simulate automated list maintenance. DataValidation will validate any new email data coming into the system on a daily basis (Email Assurance currently runs at 10pm EST) and any existing email data on a weekly basis.

Exporting only the changed results will ensure that you do not consume more API Remediation Tokens than necessary, and will provide you (the email marketer) with the most recent deliverability information we have on the addresses within your lists.
Email marketers should retrieve changed results as necessary for their business. Whether you want to retrieve them daily, weekly or monthly, DataValidation will maintain the deliverability status of the addresses in your emai lists as long as you keep them updated! (See information above on updating every 30 days)

API Tokens can be pre-purchased or post-paid, depending on the ESP plan or subscription. To determine how many Remediation Tokens you have consumed, insert -v into the curl command when starting a validation job or when exporting validated results (these two endpoints consume API Tokens). If any API call consumes tokens, the summary of tokens consumed will be in the x-synappio-tokens-consumed header.








