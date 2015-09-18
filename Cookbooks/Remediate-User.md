Remediate a List
====================

#### Running a Validation Job

By using the DataValidation API, Email Service Providers have the ability to vet the quality of email lists coming into their platform. ESPs can automate the process of checking List Quality prior to ever letting an email marketer send through their platform. View the Onboarding Cookbook for instructions on how this is done.

To remediate an email list, an ESP must first follow the steps listed in the <a href="https://github.com/synappio/synappio-client/blob/master/Cookbooks/Onboard-user.md" target="_blank">Onboarding Cookbook.</a> To receive reporting on List Quality, and to kick off validation of an email list, a job must be created. One Vetting Token will be consumed per email address when the job is created. Note: List imports must be 100% complete before creating the job that kicks off validation of a list.

### Create a Validation Job

To start a validation job, use the endpoint: GET /list/{list_slug}/job

Sample Command:

~~~~
$ curl -X POST \
-H "Authorization: bearer {api_key}" \
"https://api.datavalidation.com/1.0/list/{list_slug}/job/" \
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


### View the Progress of a Job

To view the progress of a validation job, construct the following request using the job's slug from the above result:

Sample Command:

    $ curl -X GET \
    -H "Authorization: bearer {api_key}" \
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

If the job is not finished, you should see a response similar to the one below. Notice the 'pct_complete' field representing the current percent of completion.


### Retrieve Overview Reporting

Viewing a list’s quality will provide you (the ESP) with the necessary information to determine whether a list needs to be validated or not. After a job is complete, repeating the GET request from above will yield a response similar to:

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

This is an overview of an email list’s quality. It includes the total number of subscribers in each Email Assurance Grade category (A+, A, B, D, and F) and the number of addresses that have each Deliverability Code.


### Retrieve Validation Results

After reviewing a list’s quality, it may or may not be necessary to remediate the list. The API provides multiple methods for viewing validation grades for individual members of a list. Note: Retrieving validation results will consume one Remediation Token for each address within a list.

ESPs can choose to create one list and post separate jobs to this list, or they can create numerous lists with jobs for each. Validation results can be retrieved for all members of a single list, from specific jobs, or for single members of a list.

#### To retrieve individual member grades for ALL members of a list:

This will provide a .csv formatted output including only the member slugs, email addresses, and Email Assurance grades.
To retrieve validation results for all members, use the endpoint: GET /list/{list_slug}/export.csv:

Sample Command:

    curl -X GET -H "Authorization: bearer {api_key}" \
    "https://api.datavalidation.com/1.0/list/{list_slug}/export.csv"

Sample Output:

    BPopxToE,foo@example.com,D,K0,R0,H4,O4,W3,T4,D4
    FVCExahe,baz@example.com,D,K0,R0,H4,O4,W4,T1,D4
    MPM-h7D1,bar@example.com,D,K0,R0,H4,O4,W4,T4,D4

A Remediation Token will be charged for EACH member in a list when using the '/export.csv' or '/member/' endpoints to retrieve member grades.

#### To retrieve individual member grades from a specific job:

Using the '/{job_slug}/export.csv' endpoint will provide a URL linking to the results of a previous run job. After a job is completed a .csv will be created containing the result data. Accessing this URL will generate a link to an S3 bucket where the .csv file is located. The provided url will be valid for 300 seconds (5 minutes). After this time expires, a new call to this endpoint will generate a new valid link to the csv results. This .csv will contain a header row, and will include the member slug, address, and analysis fields.

To export results from a specific job use the endpoint: /list/{list_slug}/job/{job_slug}/export.csv

Sample Command:

~~~~
curl -X GET \
-H "Authorization: bearer {api_key}" \
"https://api.datavalidation.com/1.0/list/{list_slug}/job/{job_slug}/export.csv"
~~~~

Sample Output:

~~~~
{
    "href": "https://dv-prod.s3.amazonaws. com/db/20141023/fGilGyUrDnw0bGhfnsnvLfAZhuenLVM9vhFM5d3LZDVWG6udAvRK6o6GVx3vkXNZ/M2V8TPTA-_qZc.csv?Signature=Sdu3I4jq08wvImEsXzfE8TDTUWc%3D&Expires=1414099679&AWSAccessKeyId=AKIAJ6DQJUDEB7L7MRZA"
}
~~~~

**Link Output:**

A Remediation Token will be charged for EACH member in a list when using the '/{job_slug}/export.csv' endpoint to retrieve member grades.

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

    curl -X GET -H "Authorization: bearer {api_key}" \
    "https://api.datavalidation.com/1.0/list/{list_slug}/ \
    member/{member_slug}"

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

### Remediate an Existing List

List maintenance is the key to upholding great deliverability. Using DataValidation’s API, Email Service Providers can monitor the quality of email lists in their system, as well as provide a way for their users to do the same. Whether you want to re-validate lists on a monthly or weekly basis, or always provide the most recent deliverability information for users, list maintenance can be achieved by continuous remediation existing lists.

Email Assurance is DataValidaton's list maintenance solution. We re-validate any existing addresses in our system on a weekly basis, and any new addresses on a daily basis. ESPs have access to the most recent deliverability information on any address within our system.

To kick off validation for an existing list within your API account, create a new validation job using an existing list slug.

>Important!

>30 days after a list has been uploaded, list members that have not been updated will be removed from our system, potentially resulting in the absence of some or all list members. If you require remediation of a list that is more than 30 days old, it is important to re-upload the list. If your list is less than 30 days old, the remediation process is the same as above.

### Remove Subscribers from a List

After a list has been validated you'll want to remove any undeliverable addresses from the email list. Undeliverable email addresses will have an Email Assurance Grade of F. Some ESPs may recommend that users do not send to any email addresses other than those with Email Assurance Grades of A+ and A (those known to be deliverable). These addresses can be removed as well.

DataValidation API provides two methods for unsubscribing members from a list.

#### Unsubscribe a Single Member from a List

This command will allow you to remove individual subscribers from email lists by using an address's member slug. To unsubscribe a single member from a list, send a DELETE request to the endpoint: /list/{list_slug}/member/{member_slug}/

Sample Command:

    curl -X DELETE -H "Authorization: bearer {api_key}" \
    "https://api.datavaliadtion.com/1.0/list/{list_slug}/ \
    member/{member_slug}"

Sample Response:

    204: No Content

The command's response will show that the member is longer part of the list.

#### To unsubscribe multiple members from a list:

This command will allow you to remove multiple members from a list at once by POSTing a .csv of addresses that you'd like to unsubscribe. After validating a list, specify multiple members to be unsubscribed by passing a .csv list of members to: /{list_slug}/unsubscribe.csv

**Parameters:**

header (boolean): Specifies if there is a header row present in the .csv file

slug_col (integer): Specifies if a unique identifier is available for the address. If this is omitted, a slug will be generated automatically for each address.

Sample Command:

    curl -X POST \
    -H "Content-Type: text/csv" \
    -H "Authorization: bearer {api_key}" \
        "https://api.datavalidation.com/1.0/list/{list_slug}/ \
        unsubscribe.csv?header=true&slug_col=2" \
    -d "email_address,first_name,ID, \
        oof@example.com,oof,005, \
        rab@example.com,rab,006, \
        zab@example.com,zab,007" \

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
    }


### Token Consumption

API Tokens can be pre-purchased or post-paid, depending on the ESP plan or subscription. To determine how many Remediation Tokens you have consumed, insert -v into a curl command that consumes tokens. If any API call consumes tokens, the summary of tokens consumed will be in the x-synappio-tokens-consumed header.

To find out more about list maintenance and Email Assurance for ESPs, read the <a href="https://github.com/synappio/synappio-client/blob/master/Cookbooks/Email-Assurance-Cookbook.md" target="_blank">Email Assurance Cookbook.</a>

