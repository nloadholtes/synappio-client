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

<    {
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
    } />

Notice the 'pct_complete' field representing the current percent of completion.


After reviewing the overall grades of a list, it may or may not be necessary to remediate the list. The DataValidation Batch API provides multiple methods for viewing validation grades for individual members of a list.

#### To retrieve individual member grades for ALL members of a list:

Using the '/export.csv' endpoint will provide csv formatted output including only the member slugs, email addresses, and grades.

/list/{list_slug}/export.csv:
    
        Command:

            curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/export.csv"

        Sample output:

                *********************************************
                ************** sample output ****************
                *********************************************


Using the '/member/' endpoint will provide json formatted output including member slugs, member email addresses, update timestamps as well as any metadata that may have been included in the list.

/list/{list_slug}/member/:

        Command:

            curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/member/"

        Sample output:

                *********************************************
                ************** sample output ****************
                *********************************************

**A Remediation Token will be charged for EACH member in a list when using the '/export.csv' or '/member/' endpoints to retrieve member grades.**


#### To retrieve individual grades for a single member of a list:
    
/list/{list_slug}/member/{member_slug}/:

Using the '/member/{member_slug}/' endpoint will provide output similar to the '/member/' endpoint above but for just a single member.

        Command:

            curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/list/{list_slug}/member/"

        Sample output:

                *********************************************
                ************** sample output ****************
                *********************************************

**A single Remediation Token will be charged for each call to the '/member/{member_slug}' endpoint.**


#### Remediating an Existing List 

>Important!
>   
>30 days after a list has been uploaded, list members that have not been updated will be removed from our system, potentially resulting in the absence of some or all list members. If you require remediation of a list that is more than 30 days old, it is important to re-upload the list. If your list is less than 30 days old, the remediation process is the same as above.

