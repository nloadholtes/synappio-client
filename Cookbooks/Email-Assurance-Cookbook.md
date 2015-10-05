Email Assurance for ESPs
=======================

### Overview of Email Assurance

During the onboarding process, this API allows you to retrieve list level data and quickly view the data quality on an email list. Every email address is scanned on a list and you are provided an Email Assurance Report. This report is an overview of an email list’s quality. It includes the total number of subscribers in each grade category, A+, A, B, D, and F, and an overall grade for the list.

After viewing the Email Assurance Report, there are several possible scenarios:

*   Onboard a user without remediation
*   Onboard a user and remediate select lists
*   Onboard a user and remediate all lists
*   Do not onboard a user

As the ESP, you decide which grades you are going to allow your users to deploy email to. During the onboarding process, you may think about having stricter compliance thresholds around what grades you will allow a user to email. For example, we always recommend unsubscribing the F grades but maybe at onboarding you require the user to remove D grades as well.

Once a user has been onboarded, we recommend creating a "Safe" segment for A+ and A grades. This should not be a static segment, as every time you update the list members you will want the new A+ and A grades to auto-populate in the segment. This segment allows your users to quickly deploy mail to the deliverable email addresses. You may also want to create segments for B and D grades. A B result can be upgraded to an A+ if our system detects positive engagement, or downgraded to an F if it detects negative engagement. The same holds true with the D results. This data is not reliant on *your* users deploying mail to B and D results.

Ongoing monitoring allows you to retrieve an Email Assurance Report for a list at anytime. As the ESP you can keep this data internal, or maybe you want to build a widget in your user dashboard to display the Email Assurance Report data for users to see. If you choose to do this, we recommend displaying only the Email Assurance Grades rather than all of the deliverability data on the user dashboard.

Ongoing remediation provides you with Email Assurance grades and deliverability data for each member on a list. This data can be added to the merge fields in a user's list. You may choose to update only one merge field with Email Assurance grades, or you may choose to update multiple merge fields with all of the deliverability data. If a user has a large number of merge fields already, you will only want to add the Email Assurance grade. We have found that most users only care about the grade.

We run Email Assurance daily on all of the email addresses in our database. When you make an API call to retrieve a report or a member grade, we return the most recent data in our system.

>This is important:

>You **must PUT member updates on *all* the members in your database at least once every 30 days**. When an email address or list has not been touched in 30 days, we remove it from our database. If this happens, the email list and all members will need to be created in the API again.

>This API does not currently support scheduling jobs. You should set up a periodic task in your code to create jobs in the API. These periodic tasks can be utilized to set up ongoing monitoring and ongoing remediation.

>Because the grades are being updated daily in our system, you can retrieve the member level grades for all lists daily or weekly. Export.csv does not PUT updates to the members on a list.

>This API does not currently support filtering members by grade. After calling export.csv you may want to input this data into your users' accounts and set up a task in your code to automatically unsubscribe the F results.


Email Assurance Reports and Grades
-----------------

#### Email Assurance Report

This report is an overview of an email list’s quality. It includes the total number of subscribers in each grade category, A+, A, B, D, and F, and an overall grade for the list. This report does not provide data on specific email addresses.

**Uses of this report:**

*   **When onboarding a new user** - retrieve Email Assurance Reports on all of the lists a prospective/new user intends to use. These reports can be used to determine whether to accept the user as a trusted sender. If the user has several problematic lists, remediation can be recommended prior to deploying mail. If the user has highly questionable lists, it can be required that these lists be removed and not used in the ESP platform.

*   **Prior to deploying email from a previously inactive user account** - after a user has not deployed email for at least 3 months, retrieve an Email Assurance Report on the list prior to allowing the email to be deployed. If the data is acceptable, the user can move forward without remediation. If not, the user can be recommended remediation prior to deploying the campaign.

*   **When a current user imports a new list** - retrieve an Email Assurance Report prior to allowing email to be deployed. If the data is acceptable, the user can move forward without remediation. If not, the user can be recommended remediation prior to deploying the campaign. If the list is too risky, it can be disallowed altogether.

*   **Embed the data to allow users to always see the Email Assurance Report** - users can always know the list quality so it is not a surprise if remediation is recommended.


#### Email Assurance Grades

This grade — A+, A, B, D, or F— indicates an emails likelihood to be deliverable. Additional deliverability data is provided with the grade.

&nbsp;&nbsp;&nbsp;&nbsp;A+ indicates Deliverable + Engagement History

&nbsp;&nbsp;&nbsp;&nbsp;A indicates Deliverable

&nbsp;&nbsp;&nbsp;&nbsp;B indicates Accepts-All

&nbsp;&nbsp;&nbsp;&nbsp;D indicates Indeterminate

&nbsp;&nbsp;&nbsp;&nbsp;F indicates Undeliverable

**Uses of the grades:**

*   Determine what grades a user can deploy email to - A+ and A results are deliverable based on our most recent data. If a user is a trusted sender, perhaps B results can be allowed. D results should not be deployed email. F results should be unsubscribed.

*   Emails graded with B or D cannot be confirmed deliverable or undeliverable unless mail is deployed to these codes. You may consider allowing these grades to remain on a user's list with the understanding that they cannot be mailed to *unless* the grade changes to an A+ or A.


#### Deliverability Codes

In addition to the Email Assurance grade you are provided deliverability data for each email address. This data may influence the Email Assurance grade given to a particular address, and is intended to provide more insight into the deliverability history of the email address.

Deliverability codes are provided on a scale of 1-4, with 1 being the least deliverable and 4 being the most. You may see a 0 associated with Historical Opens (R) and Historical Clicks (K), meaning that we do not have any engagement data on that particular member.

**Hard Bounces (H)**

Historical Hard Bounce information illustrates which emails have a hard bounce history and how many sources we've received this information from.

**Opt-Outs (O)**

Historical Opt-Outs illustrates the members that have a history of opting-out from email lists. A subscriber's opt-out history is based on their overall email history and can help in determining the likelihood of opting-out from your emails as well. This is a good indication that the email address is most likely deliverable.

**Complainers (W)**

Complainers are members who have a history of reporting email as spam. A historical complainer code will indicate whether a member has a history of complaining. Keep in mind that spam complaints can be correlated with expired permission or undesireable content. This is not a prediction as to whether the member will report a message as spam.

**Spam-Traps (T)**

Email addresses that are associated with historical spam-trap data are indicated here. We do not include spam trap data in determining an Email Assurance Grades. This information changes frequently and we cannot guarantee every instance to be accurate. This information can used for segmenting.

**Deceased Individuals (D)**

This code indicates whether an email address belongs to a person who is deceased or not.

**Historical Opens (R)**

This is a measure of the historical level of engagement based on the amount of deliverable mail sent to an address. This is a historical reference, and does not determine how likely one is to open your email.

**Historical Clicks (K)**

This is a measure of the historical level of engagement based on the amount of deliverable mail sent to an address. This is a historical reference, and does not determine how likely one is to click your email.

### Setting up Email Assurance

ESPs can set up Email Assurance to validate new email lists coming into their system, monitor the qality of these lists on an ongoing basis, and to remediate these lists whenever necessary. To get started, you can import and start an initial validation on all of your existing email lists. Once lists have been validated initially, ESPs can export only the 'changed' results however frequently they see fit.

'Changed' results will include any email addresses that have changed deliverability information. If Deliverability Codes have changes, and the Email Assurance Grade given to an address has changed because of this, you can retrieve this information to update the ESPs system accordingly.

Email Assurance will automatically run on the existing lists within your API account [once a list has been added to the account, there is no need to create a validation job each time you wish to retrieve results]. Simply add new lists to be validated, or export only the 'changed' results for a list of addresses that have been updated.

Below explains how to create and import new lists within your API Account, add subscribers to existing lists within the API, and how to retrieve changed results for automated list maintenance.

### For Initial List Validation

#### Create and Import a List

Lists can be created in the API by importing a .csv file directly or via download URL to the .csv file. ESPs can create lists for any new email data they have. **We recommend that for larger lists, or larger databases, you upload through URL.**

##### Import via .csv file

Create the list and import in the same command line. You must include all mapping data in the command line. Please note that if you use curl to upload a .csv, you must make sure that the data you're uploading contains newline (\n) characters. Otherwise, the API will interpret your upload as a single (very long!) row.

To create a list using a .csv file, use the endpoint: POST /list

Sample Command:

    $ curl -X POST \
    -H "Content-Type: text/csv \
        Authorization: bearer {api_key}" \
        "https://api.datavalidation.com/1.0/list/?header=true&email=0&metadata=true&slug_col=2" \
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

##### Import via download URL

If you import a list via URL, you will need to create an empty list and then import using the download URL. You must provide mapping data in the URL parameters for the email list. Note: If you use a Dropbox link as you list_url, be sure to use dl=1 at the end of the link so that we can access the actual data within the .csv file.

To create an empty list:

Sample Command:

    curl -X POST -H 'authorization: bearer {list_slug}' "https://api.datavalidation.com/ \
    1.0/list/?email=0&header=false&metadata=false"

Sample Output:

~~~~
    {"list": [{"size": 0, "meta": {"href": "http://api.datavalidation.com/1.0/list/skjdhfksjdhf/", \
    "links": [{"href": "import/", "rel": "imports"}, {"href": "job/", "rel": "jobs"}, \
     {"href": "member/", "rel": "members"}]}, "slug": "T4Vt8OvnQU5fkyo9", "tags": []}]
~~~~

To import the list via download URL.

Sample Command:

    curl -X POST -H "Authorization: bearer {api_key}" \
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
    [{"status": "New", "tags": [], "created": "2015-09-02T18:51:10.654000Z", "mapping": {"header_row": \
    false, "email_col":\ 1, "include_metadata": false, "slug_col": 0}, "note": "List Example", \
    "href": "https://www.dropbox.com/s/vqasnxgx77tu77p/email_key_new%202.csv?dl=1", "meta": \
    {"href": "http://api.datavalidation.com/1.0/list/6iT4uwzFNYbvj8w1/import/nsJUsuLn/"}, \
    "validate": false, "total_imported": 0, "slug": "nsJUsuLn"}]
~~~~

When importing to the empty list (via URL), be sure to include mapping data for URL, header row, email column, metadata, and slug column (if you have one). Use this command to create an import from a URL.

#### Check the Status of an Import

Imports must be 100% complete before starting a job! To check the status of an import, use the endpoint: GET /list/{list_slug}/import/{import_slug}/

Sample Command:

    curl -H 'authorization: bearer {api_key}' "https://api.datavalidation.com/1.0/list/{list_slug}/ \
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
            "href": "http://api.datavalidation.com/1.0/list/6iT4uwzFNYbvj8w1/import/nsJUsuLn/"
        },
        "validate": false,
        "total_imported": 349333,
        "slug": "nsJUsuLn"
    }

List imports must be 100% complete before creating the job that kicks off validation of a list.**

#### See all of the lists you have created

You can easily retrieve summary or detailed information about all of the lists you’ve created within your API account by calling the endpoint: /list/

~~~~
    curl -X GET \
    -H "Authorization: bearer {api_key}" \
    -H "Content-Type: application/json" \
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
        "items": [
            {
                "size": 1000000,
                "meta": {
                    "href": "https://api.datavalidation.com/1.0/list/{api_key}/",
                    "links": [
                        {
                            "href": "import/",
                            "rel": "imports"
                        },
                        {
                            "href": "job/",
                            "rel": "jobs"
                        },
                        {
                            "href": "member/",
                            "rel": "members"
                        }
                    ]
                },
                "slug": "{slug}",
                "tags": []
            }
~~~~

### To Add Subscribers to Existing Lists

#### To add a single member to an existing list

As an ESP, there will be subscribers signing up for numerous users' emails lists on a daily basis. The addresses collected will be subscribed one-by-one and you may wish to add these to an existing list within the API. You can subscribe a single member to a specified existing list by sending a POST request to the appropriate list slug, using the endpoint: /{list_slug}/member/

Sample Command:

    curl -X POST -H "Authorization:bearer {api_key}" -H "Content-Type:application/json" \
    "https://api.datavalidation.com/1.0/list/{list_slug}/member/" -d '{
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
                "name": "Test Email",
                "value": "Some value"
                }
            ],
            "slug": "random-or-user-defined-slug",
            "address": "ashley@synapp.io"
         }
    }

#### To add multiple members to an existing list

Email marketers may want to add newly created lists to their ESP account, and you (the ESP) may wish to add these new lists to an existing list within your API account. Adding multiple members to an existing list can be done by POSTing a .csv file to the list or by providing us with a download link (URL) to a .csv file containing the members you want to subscribe.

**To add members by POSTing a .csv**

Send a POST request to the appropriate list slug, using the endpoint: /list/{list_slug}/subscribe.csv
*Please Note: The required parameters are the same as the '/list/' endpoint when using a POST request to create new list.

**Parameters:**

header (boolean): Specifies if there is a header row present in the .csv file

email_col (integer): Specifies which column the email address is found in? (0 = first column)

metadata (string): Specifies if metadata (non-email) is present in the .csv file (true or false)

slug_col (integer): Specifies if a unique identifier is available for the address. If this is omitted, a slug will be generated automatically for each address.


Sample Command:

    curl -X POST \
    -H "Content-Type: text/csv" \
    -H "Authorization: bearer {api_key}" \
    "https://api.datavalidation.com/1.0/list/{list_slug}/subscribe.csv? \
    header=true&email=0&metadata=true&member_slug=2" -d "email_address,first_name,ID, \
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
curl -X POST \
-H "Authorization: bearer {api_key}" \
-H "Content-Type: application/json" \
"https://api.datavalidation.com/1.0/list/{list_slug}/" \
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
            "href": "https://api.datavalidation.com/1.0/list/CrT3YdNZagFxG9aiAXb/\
            import/vYG7J_XT/"
        },
        "slug": "vYG7J_XT"
    }
]
~~~~

Email Assurance, DataValidation's list maintenance solution, runs once a day. We will analyze any new email data in the system on a daily basis, and any existing data in the system on a weekly basis. After creating and importing a new list of addresses, you can:

1. Automatically start a validation job when the import is created [import .csv directly]
2. Run a validation job after a list import is complete
3. Wait for the daily Assurance run to pull in and validate any new email data

To automatically start a validation job at import, ESPs should include the additional parameter (listed below) in the curl command for importing via URL. To run a validation job after a list import, **the import must be 100% complete.** To wait for Email Assurance to pick up any new email addresses, or any new email lists, simply create the import for the email data and we'll do the rest!

To **automatically start a validation job when an import is created**, add the parameter **"validate": true** in the curl command for creating an import via URL.

Sample Command:

    curl -X POST -H "Authorization: bearer {api_key}" \
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

    [{"status": "New", "tags": [], "created": "2015-08-26T14:12:23.572000Z", "mapping":\
    {"header_row": true, "email_col": 0, "include_metadata": false, "slug_col": 0},\
    "note": "Sample Onboarding", "href": "https://www.dropbox.com/s/vqas77p/202.csv?dl=0",\
    "meta": {"href": "http://api.datavalidation.com/1.0/list/GKGu8YEKU6IQGzvT/import/yffkMW9l/"},\
    "validate": true, "total_imported": 0, "slug": "yffkMW9l"}]

**A Vetting Token will be charged for each member in the list when the job is automatically created.**

#### Run a Validation Job

For lists that have been imported (no automatic job created), the next step is to create a validation job for the imported list. Note: A Vetting Token will be charged for each member in the list when a job is created. Creating a validation job kicks off the validation process. When the job has finished, the Vetting Tokens consumed will provide you with an overview report of the list's quality.

To start a validation job, use the endpoint: GET /list/{list_slug}/job

Sample Command:

~~~~
$ curl -X POST \
-H "Authorization: bearer {api_key}" \
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

### Retrieve Overview Reporting

Viewing a list’s quality will provide you with the necessary information to determine whether a user's list needs to be validated or not. Overview Reporting is an overview of an email list’s quality. Reporting includes the total number of subscribers in each Email Assurance Grade category: A+, A, B, D, and F, and the number of subscribers that have each Deliverability Code. Deliverability Codes represent the historical deliverability information on subscribers, and together determine a subscriber's Email Assurance Grade.

This reporting can be shown to email marketers to either prompt list hygiene or keep marketers updated with their list's quality overtime.

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

### Retrieve Validaton Results for Intitial Validation

After reviewing a list’s quality, it may or may not be necessary to remediate the list. The API provides multiple methods for viewing validation grades for individual members of a list. Note: Retrieving validation results will consume one Remediation Token for each address within a list.

Email service providers can choose to create one list for their entire database and post separate jobs to this list, or they can create numerous lists with jobs for each. Validation results can be retrieved for all members of a single list, from specific jobs, or for single members of a list.

#### To retrieve individual member grades for ALL members of a list:

This will provide a .csv formatted output including only the member slugs, email addresses, and Email Assurance grades. To retrieve validation results for all members, use the endpoint: GET /list/{list_slug}/export.csv:

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
    "href": "https://dv-prod.s3.amazonaws.com/db/20141023/ \
    fGilGyUrDnw0bGhfnsnvLfAZhuenLVM9vhFM5d3LZDVWG6udAvRK6o6GVx3vkXNZ/M2V8TPTA-_qZc.csv? \
    Signature=Sdu3I4jq08wvImEsXzfE8TDTUWc%3D&Expires=1414099679&AWSAccessKeyId=AKIAJ6DQJUDEB7L7MRZA"
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

    curl -X GET -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/ \
    1.0/list/{list_slug}/member/"

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

### Managing Existing Lists and Retrieving Changed Results

List maintenance is the key to upholding great deliverability. Using DataValidation’s API, ESPs can monitor the quality of email lists within their system, and provide a way email marketers to always know where they stand prior to sending. List maintenance can be achieved by continuous remediation existing lists.

Email Assurance is DataValidaton's list maintenance solution. We re-validate any existing addresses in our system on a weekly basis, and any new addresses on a daily basis. Email Assurance generally runs at 10pm EST everyday.

If new addresses have been added to existing lists within the API, Email Assurance will pick them up that same day after 10pm EST, or you can kick off a validation job for an existing list within your API account. To revalidate an existing list, create a new validation job using the list’s existing list slug.

>This is important!

>For email addresses to be maintained with the most recent deliverability information, you must PUT member updates on all the members in your database (within lists) at least once every 30 days. When an email address or list has not been touched in 30 days, we remove it from our database. If this happens, the email list and all members will need to be created in the API again.
This API does not currently support scheduling jobs. You should set up a periodic task in your code to create jobs in the API. These periodic tasks can be utilized to set up ongoing monitoring and ongoing remediation.

>Because the grades are being updated daily in our system, you can retrieve the member level grades for all lists daily or weekly. Export.csv does not PUT updates to the members on a list.

>This API does not currently support filtering members by grade. After calling export.csv you may want to input this data into your users' accounts and set up a task in your code to automatically unsubscribe the F results.

The following process should be repeated in order to monitor user list(s) and keep them up to date in respect to new subscribers, unsubscribes, and grade changes. This process should be used if you are setting up daily or weekly monitoring and remediation.

### Retrieve Changed Validation Results

Monitor the quality of email lists in your API Account by exporting only the addresses that have changed since a specific time stamp. If an email address have 'changed' This means that an address has a new Email Assurance Grade or newly appended Deliverability Codes since it’s last validation export by you.

#### Changed Results since specific Timestamp

To retrieve a list of changed members, send a GET request to the list/{list_slug}/export.csv endpoint and use the updated_since query parameter. The updated_since parameter is a url encoded ISO format date. If no members have a changed since the date specified, you will receive a 200 ok in your response header.

**To get results in the output:**

Sample Command:

~~~~
    curl -v -X GET \
    -H "Authorization: bearer {api_key}" \
    "https://api.datavalidation.com/1.0/list/{list_slug}/ \
    export.csv?updated_since=2015-09-29T20%3A43%3A47.300080Z"
~~~~

Sample Output:

~~~~

curl -v -X GET -H "Authorization: bearer {api_key}" \
"https://api.datavalidation.com/1.0/list/{list_slug}/ \
export.csv?updated_since=2015-09-29T20%3A43%3A47.300080Z"
elipsis(...)
> GET /1.0/list/{list_slug}/export.csv?updated_since=2015-09-29T20%3A43%3A47.300080Z HTTP/1.1
> User-Agent: curl/7.30.0
> Host: api.datavalidation.com
> Accept: */*
> Authorization: bearer {api_key}
>
< HTTP/1.1 200 Ok
< Content-Type: text/csv; charset=UTF-8
< Date: Fri, 11 Sep 2015 18:02:19 GMT
* Server nginx/1.9.2 is not blacklisted
< Server: nginx/1.9.2
< Content-Length: 0
< Connection: keep-alive
<
* Connection #0 to host api.datavalidation.com left intact

~~~~

If there are email addresses within your existing list that have changed deliverability information, you will see a response similar to the one below, including the slug_col, email address, Email Assurance Grade, and corresponding Deliverability Codes.

Sample Output:

~~~~
1,example@synapp.io,A,K0,R0,H4,O4,W4,T4,D4
10,johndoe@synapp.io,B,K0,R0,H4,O4,W4,T4,D4
100,janedoe@synapp.io.com,B,K0,R0,H4,O4,W4,T4,D4
10000,email@synapp.io,A,K0,R0,H4,O4,W4,T4,D4
~~~~

**To get results in a download URL**

If you would like to get a link to a downloadable .csv file of your 'changed' results, you can use the command listed below. This will be most easiest when attempting to sort your file for addresses you wish to unsubscribe from lists within your API Account. Add this to the end of your command line to get a downloaded .csv file: > new-results.csv

Sample Command:

~~~~
    curl -v -X GET \
    -H "Authorization: bearer {api_key}" \
    "https://api.datavalidation.com/1.0/list/{list_slug}/ \
    export.csv?updated_since=2015-09-29T20%3A43%3A47.300080Z" > new-results.csv
~~~~

Sample Output:

~~~~
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:--  0:00:01 --:--:--     0
100  262k    0  262k    0     0   5345      0 --:--:--  0:00:50 --:--:--  6558
~~~~

Once this has completed, there will be a new file in your Downloads called 'new-results.csv'

Once you have downloaded only the updated results, you'll want to remove any undeliverable addresses from the email list. Undeliverable email addresses will have an Email Assurance Grade of F. Filter the undeliverable addresses within your file so that you can upload this file to your existing list and unsubscribe these addresses.

#### Changed Results Since Last Validation

**Please Note: Restting the changed flag on addresses and exporting only changed results since your latest validation will be gone in the next version of DataValidation's API. We recommend maintaining the qulity of email lists by exporting changed results since specific timestamp.**

**Reset the Changed Flag**

First, you’ll want to reset the ‘changed’ flag on the members of your existing lists. This will need to be done before daily Email Assurance runs and your list is re-validated. 'Changed' indicates that the deliverability information on an address has not changed. The following command will set the ‘changed’ flag to ‘false’ for each member in a list. The output will provide the number of changed results.

To reset the ‘changed’ flag, use the endpoint: /list/{list_slug}/member/

Sample Command:

~~~~
    curl -X PATCH \
    -H "Authorization: bearer {api_key}" \
    -H "Content-Type: application/json" \
    "https://api/datavalidation.com/1.0/list/{list_slug}/member/" \
    -d '{"changed":false}'
~~~~

Sample Output:

~~~~
    {
        "updated": -1, \
        "unsubscribed": 0, \
        "subscribed": 0 \
    }
~~~~

After resetting the 'changed' flag, you'll need to wait for daily Assurance to run and re-analyze all subscribers within your existing list. Waiting for daily Assurance to run is equivilant to re-starting a validation job. Once Assurance has finished, you can download only the email addresses that have a changed status.

**Retrieve Changed Validation Results**

At this point, you only want to retrieve data for members that have changed. This means that an address has a new Email Assurance Grade or newly appended Deliverability Codes since it’s last validation export by you.

To retrieve a list of changed members, send a GET request to the list/{list_slug}/export.csv endpoint and use the changed query parameter. If no members have a changed status, you will recieve a 200 ok in your response header.

**To get results in the output**

Sample Command:

~~~~
    curl -v -X GET \
    -H "Authorization: bearer {api_key}" \
    "https://api.datavalidation.com/1.0/list/{list_slug}/ \
    export.csv?changed=true"
~~~~

Sample Output:

~~~~

curl -v -X GET -H "Authorization: bearer {api_key}" \
"https://api.datavalidation.com/1.0/list/{list_slug}/export.csv?changed=true"
elipsis(...)
> GET /1.0/list/{list_slug}/export.csv?changed=true HTTP/1.1
> User-Agent: curl/7.30.0
> Host: api.datavalidation.com
> Accept: */*
> Authorization: bearer {api_key}
>
< HTTP/1.1 200 Ok
< Content-Type: text/csv; charset=UTF-8
< Date: Fri, 11 Sep 2015 18:02:19 GMT
* Server nginx/1.9.2 is not blacklisted
< Server: nginx/1.9.2
< Content-Length: 0
< Connection: keep-alive
<
* Connection #0 to host api.datavalidation.com left intact

~~~~

If there are email addresses within your existing list that have changed deliverability information, you will see a response similar to the one below, including the slug_col, email address, Email Assurance Grade, and corresponding Deliverability Codes.

Sample Output:

~~~~
1,example@synapp.io,A,K0,R0,H4,O4,W4,T4,D4
10,johndoe@synapp.io,B,K0,R0,H4,O4,W4,T4,D4
100,janedoe@synapp.io.com,B,K0,R0,H4,O4,W4,T4,D4
10000,email@synapp.io,A,K0,R0,H4,O4,W4,T4,D4
~~~~

#### To get results in a download URL

If you would like to get a link to a downloadable .csv file of your 'changed' results, you can use the command listed below. This will be most easiest when attempting to sort your file for addresses you wish to unsubscribe from lists within your API Account. Add this to the end of your command line to get a downloaded .csv file: > new-results.csv

Sample Command:

~~~~
    curl -v -X GET \
    -H "Authorization: bearer {api_key}" \
    "https://api.datavalidation.com/1.0/list/{list_slug}/ \
    export.csv?changed=true" > new-results.csv
~~~~

Sample Output:

~~~~
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:--  0:00:01 --:--:--     0
100  262k    0  262k    0     0   5345      0 --:--:--  0:00:50 --:--:--  6558
~~~~

Once this has completed, there will be a new file in your Downloads called 'new-results.csv'

Once you have downloaded only the 'changed' results, you'll want to remove any undeliverable addresses from the email list. Undeliverable email addresses will have an Email Assurance Grade of F. Filter the undeliverable addresses within your file so that you can upload this file to your existing list and unsubscribe these addresses.

#### Remove subscribers from a List

Some ESPs may recommend that email marketers do not send to any email addresses unless they have an Email Assurance Grade of A+ and A (those known to be deliverable). These addresses can be removed as well. When instructing email marketers, we highly recommend following the best practices and compliance rules stated by your specific ESP. By using the DataValidation API, ESPs can set their own compliance standards and unsubscribe according to that.

DataValidation API provides two methods for unsubscribing members from a list.

#### Unsubscribing a Single Member from a List

This command will allow you to remove individual subscribers from email lists by using an address's member slug. To unsubscribe a single member from a list, send a DELETE request to the endpoint: /list/{list_slug}/member/{member_slug}/

Command:

~~~~
curl -X DELETE -H "Authorization: bearer {api_key}" "https://api.datavaliadtion.com/1.0/list \
/{list_slug}/member/{member_slug}"
~~~~

Sample output:

~~~~
Status code: 204 No Content
~~~~

#### Unsubscribe Multiple Members from a List:

This will allow you to remove multiple members from a user's list at once by POSTing a .csv of addresses that you'd like to unsubscribe. After validating a list, specify multiple members to be unsubscribed by passing a .csv list of members to: /{list_slug}/unsubscribe.csv

**Parameters:**

header (boolean): Specifies if there is a header row present in the .csv file

email_col (integer): Specifies which column the email address is found in? (0 = first column)

metadata (string): Specifies if metadata (non-email) is present in the .csv file (true or false)

slug_col (integer): Specifies if a unique identifier is available for the address. If this is omitted, a slug will be generated automatically for each address.

Sample Command:

    curl -X POST \
    -H "Content-Type: text/csv \
        Authorization: bearer {api_key}" \
        "https://api.datavalidation.com/1.0/list/{list_slug}/unsubscribe.csv \
        ?header=true&slug_col=2" \
    -d "email_address,first_name,ID, \
        oof@example.com,oof,005, \
        rab@example.com,rab,006, \
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

Once you've retrieved 'changed' results, and updated your email lists with any unsubscribes, you can continue to add any new subscribers to existing lists. New members can be added to an existing list by posting a .csv file OR by providing a URL link to the .csv file of new subscribers. This will be done exactly as documented in the Initial Validation section of this Cookbook.

**Please Note: To add members to an existing list via URL link, you MUST provide a slug_col within the specified parameters of the list import. If you ​*don't*​ include member slugs then we'll generate slugs for each of the members you import, since we assume you want to ​*replace*​ the members of the list.

Once a list has been updated with new subscribers, the next step is to either 1. Run the validation job or 2. Wait for daily Assurance to run. Imports MUST be 100% complete before starting a validation job (unless using the "validate": true parameter. Run the validation job the same way specified in the instructions mentioned previously. **Waiting for Assurance to run is equivilant to running a validation job, and is the best option for automated list maintenance.**

Using the ‘Changed’ flag when monitoring and continuously remediating existing lists is how users of the API can simulate automated list maintenance for their database. DataValidation will validate any new email data coming into the system on a daily basis (Email Assurance currently runs at 10pm EST) and any existing email data on a weekly basis.

Exporting only the changed results will ensure that you do not consume more API Remediation Tokens than necessary, and will provide you (the ESP) with the most recent deliverability information we have on the addresses within your lists.

ESPs should retrieve changed results as necessary for their users and compliance standards. Whether you want to retrieve results daily, weekly or monthly, DataValidation will maintain the deliverability status of the addresses in your emai lists as long as you keep them updated! (See information above on updating every 30 days)

#### API Token Consumption

DataValidation partners with Email Service Providers to provide a database monitoring and maintenance solution, and to enable an ESPs users to maintain list quality on an ongoing basis. All ESPs vary in terms of their platform, users, and compliance standandard. DataValidation aims to work directly with ESPs who wish to use the API, to provide a custom plan that fits the ESPs specific needs.

Please <a href="http://www.datavalidation.com/email-service-providers/">visit our ESP site</a> for more information.











