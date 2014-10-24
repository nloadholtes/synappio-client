Remediate a List
====================

#### Running a Validation Job 

To begin processing a list, a job must be created to start validating members within a list.

Note: An Onboarding Token will be charged for each member in the list when a job is created.

Command:

~~~~
$ curl -X POST
-H "Authorization: bearer {api_key}"
"https://api.datavalidation.com/1.0/list/{list_slug}/job"
~~~~

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

### Retrieve validation results 

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


#### To retrieve individual member grades from a specific job:

Using the '/{job_slug}/export.csv' endpoint will provide a url linking to the results of a previous run job. After a job is completed we generate a csv of the result data. Accessing this url will generate a link to an S3 bucket where the csv file is located. The provided url will be valid for 300 seconds (5 minutes). After this time expires, a new call to this endpoint will generate a new valid link to the csv results. This csv will contain a header row, and will include the member slug, address, and analysis fields.

/list/{list_slug}/job/{job_slug}/export.csv:

Command:

~~~~
curl -X GET
-H "Authorization: bearer {api_key}"
"https://api.datavalidation.com/1.0/list/{list_slug}/job/{job_slug}/export.csv"
~~~~

Sample output:

~~~~
{
    "href": "https://dv-prod.s3.amazonaws.com/db/20141023/fGilGyUrDnw0bGhfnsnvLfAZhuenLVM9vhFM5d3LZDVWG6udAvRK6o6GVx3vkXNZ/M2V8TPTA-_qZc.csv?Signature=Sdu3I4jq08wvImEsXzfE8TDTUWc%3D&Expires=1414099679&AWSAccessKeyId=AKIAJ6DQJUDEB7L7MRZA"
}
~~~~

Link output:

~~~~
slug,address,grade,click,open,hard,optout,complain,trap,deceased
R18y23L8,baz@example.com,D,K0,R0,H4,O4,W4,T1,D4
Zl42d0zw,bar@example.com,D,K0,R0,H4,O4,W4,T4,D4
fZS_PEs-,foo@example.com,D,K0,R0,H4,O4,W3,T4,D4
~~~~

A Remediation Token will be charged for EACH member in a list when usling the '/{job_slug}/export.csv' endpoint to retrieve member grades.


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

>Important!
    
>30 days after a list has been uploaded, list members that have not been updated will be removed from our system, potentially resulting in the absence of some or all list members. If you require remediation of a list that is more than 30 days old, it is important to re-upload the list. If your list is less than 30 days old, the remediation process is the same as above.
