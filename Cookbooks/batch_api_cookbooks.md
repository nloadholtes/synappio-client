Onboarding a User
====================


#### Uploading a List 

As an ESP, it may be useful to know the quality of a potential user's list(s) before accepting them as a customer. This set of instructions will provide a means of doing so.

Before upload a list, a few questions must first be answered about the list being uploaded:

*   Does the csv have include a header on the first row?

    If yes, the query parameter 'header' should be set to 'true', otherwise 'false'.

*   What collumn is the email address in?

    If the email address is in the first collumn, the query parameter 'email' should be set to '0'. If the email address is in the second collumn, it should be set to '1' etc.

*   Is there data in each row (other than the email address) that you would like to store?
    
    You might want to store additional data such as first name, last name, unqiue ID etc. If so, the query parameter 'metadata' should be set to 'true', otherwise 'false'.

After adding a list, individual member grades will be available via this endpoint: /list/{list_slug}/member/{member_slug}/

'member_slug' is a unique ID specific to members in a list. If you prefer to specify 'member_slug', set the 'slug_col' query parameter to the collumn containing your provided identifier in your csv(collumn 1 = 0). If this parameter is not provided, member slugs will be generated automatically.

Note: If you intend on accessing individual member grades and not ALL member grades, be sure to include member slugs in your csv. Otherwise, you will have to make a call to '/list/{list_slug}/member/' to retrieve the member_slugs we provide and you will be charged a remediation token for each member in the list.

Sample command:

    $ curl -X POST
    -H "Content-Type: text/csv
        Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/?header=true&email=0&metadata=true&slug_col=2"
    -d "email_address,first_name,ID,
        foo@example.com,foo,001,
        bar@example.com,bar,002,
        baz@example.com,baz,003,"

Sample output:

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


#### Running a Validation Job 

To begin processing a list, a job must be created to start validating members within a list.

Note: An Onboarding Token will be charged for each member in the list when a job is created.

Command:

    $ curl -X POST
    -H "Authorization: bearer {api_key}"
    "https://api.datavalidation.com/1.0/list/{list_slug}/job"

Sample output:

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

Notice the 'pct_complete' field representing the current percent of completion.


#### Viewing List Grades 

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

Remediating a List After Onboarding
==================== 

After reviewing the overall grades of a list, it may or may not be necessary to remediate the list. The DataValidation Batch API provides multiple methods for viewing validation grades for individual members of a list.

#### To retrieve individual member grades for ALL members of a list:

Using the '/export.csv' endpoint will provide csv formatted output including only the member slugs, email addresses, and grades.

/list/{list_slug}/export.csv:

Command:

            curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/export.csv"

Sample output:

    BPopxToE,foo@example.com,D,K0,R0,H4,O4,W3,T4,D4
    FVCExahe,baz@example.com,D,K0,R0,H4,O4,W4,T1,D4
    MPM-h7D1,bar@example.com,D,K0,R0,H4,O4,W4,T4,D4


/list/{list_slug}/member/:
        
Using the '/member/' endpoint will provide json formatted output including member slugs, member email addresses, update timestamps as well as any metadata that may have been included in the list.

Command:

            curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/member/"

Sample output:

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


#### To retrieve individual grades for a single member of a list:

Using the '/member/{member_slug}/' endpoint will provide output similar to the '/member/' endpoint above but for just a single member.
    
/list/{list_slug}/member/{member_slug}/:

Command:

            curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/member/"

Sample output:

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


#### Remediating an Existing List 

Important!
    
30 days after a list has been uploaded, list members that have not been updated will be removed from our system, potentially resulting in the absence of some or all list members. If you require remediation of a list that is more than 30 days old, it is important to re-upload the list. If your list is less than 30 days old, the remediation process is the same as above.



Managing List Members 
====================

### Adding members to a list:

The DataValidation Batch API provides two methods for subscribing new members to an existing list. 

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
                -H "Content-Type: text/csv
                    Authorization: bearer {api_key}"
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


### Removing members from a list:

The DataValidation Batch API provides two methods for unsubscribing members from a list.

#### To unsubscribe a single member from a list:

By sending a DELETE request to the '/member/{member_slug}' endpoint, a single member of a list can be unsubscribed.

/list/{list_slug}/member/{member_slug}/:

Command:

                curl -X DELETE -H "Authorization: bearer {api_key}" "https://api.datavaliadtion.com/1.0/list/{list_slug}/member/{member_slug}"

Sample output:

             Status code: 204 No Content


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
                -H "Content-Type: text/csv
                    Authorization: bearer {api_key}"
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















