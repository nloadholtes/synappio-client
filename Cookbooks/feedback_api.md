Feedback API for Email Service Providers
========================================

### The Feedback API by DataValidation

Datavalidation works with email service providers to help onboard, monitor, and remediate user email data on an ongoing basis. Email Assurance, DataValidation's list maintenance solution, analyzes any new data from ESPs on a daily basis and any existing data on a weekly basis - allowing ESPs to keep their database of addresses up-to-date with most recent deliverability information.

To determine whether email data is deliverable or not, DataValidation looks at the entire deliverability history of an email address, including: A history of hard bounces, complaints, unsubscribes, spam trap information, and whether or not an the owner of an address has a history of being deceased. In addition to this deliverability history, we look to see whether or not an address has a recent history of opening or clicking within email campaigns. This campaign history is provided by Partner ESPs and allows us to determine that an address is deliverable, or that it's deliverable with recent engagement.

By using the Feedback API, ESPs not only benefit from their own campaign history but from that of all Partner ESPs who choose participate - making deliverability reporting even more accurate and up-to-date.

**What is the Feedback API?**

DataValidation's Feedback API allows Email Service Providers to feed campaign history back to into our system - immediatly impacting the deliverability information we provide on an ESPs database. ESPs can import campaign history including: campaigns delivered, opens, clicks, hard bounces, complaints, and unsubscribes. The campaign history submitted is specifically related to user campaigns being sent through the ESP platform.

Email Service Providers taking advantage of DataValidation's Feedback API can benefit from more accurate and up-to-date deliverability reporting by providing us with campaign history. This API is available only to Partner ESPs, and the information we recieve is for the benefit of all ESPs taking advantage of the Feedback API.

Currently, the feedback API is only available for Email Service Providers. ESP Partners will go through a vetting process to be considered, and any data received through the Feedback API will be closely monitored to prevent bad data from entering the system. See below for details on how to submit campaign history.

### Submit a CSV File containing Campaign History

When using the Feedback API, ESPs should submit .csv files containing email addresses and corresponding campaign history. These files should specifically contain columns within the .csv file for the following parameters:

- Timestamp: What time did the event occure?

- Email Address: Which address are you providing campaign history for? Only one per row.

- Event Type: Event types include sent, open, click, hard, abuse, and unsubscribed.


Listed below is an example of actual .csv data. **Addresses with numerous event types should be listed on individual rows of the .csv file.** If an address has open history, click history and unsubscribed history, the address would need to be listed 3 times on 3 different rows within the .csv file.

~~~~
ts,email,type
1440528585,test@example.com,sent
1440528585,test@example.com,hard
1440528585,test@example.com,open
1440528585,test@example.com,click
1440528585,test@example.com,abuse
1440528585,test@example.com,unsubscribed
~~~~

DataValidation accepts campaign history for specific events. These events will improve the deliverability results given for an ESPs database. Please note that the only **event types** currently supported are as follows. Please include the following data in your .csv file. All other event types will be ignored.

- `sent`: email was sent and successfully delivered to this address
- `open`: email was opened by the recipient
- `click`: a link was clicked by the recipient
- `hard`: a hard bounce was recorded
- `abuse`: abuse was reported by this email address
- `unsubscribed`: this email address was unsubscribed by the recipient

Once feedback data is formatted correctly, ESPs can import .csv files by either submitting the file via downloadable URL or by importing the .csv directly into the body of the POST. See below for details.

### Create New Feedback Import via Download URL

To import feedback data via downloadable URL, you must provide mapping data in the URL parameters for the email list. Note: If you use a Dropbox link as you list_url, be sure to use dl=1 at the end of the link so that we can access the actual data within the .csv file.

**Parameters:**

* header (boolean): Specifies if there is a header row present in the .csv file

* timestamp (query): Which column contains the timestamp? (UTC seconds since the epoch) defaltValue: 0

* email address (query): Which column contains the email address? Only one address per row. defaultValue: 1

* event type (query): Which column contains event type? defaultValue: 2

To import the list via download URL, use the endpoint: POST "/campaign-event/" Save the "import_slug" to check the status and get details of your import.

Sample Command:

~~~~
curl -X POST -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/campaign-event/" -d '{
    "href": "{list_url}",
    "mapping": {
        "header_row": true,
        "email_col": 0,
        "ts_col": 1,
        "type_col": 2
        }
    }'
~~~~

Sample Output:

~~~~
{"status": {"status": 200, "message": "Everything's cool!", "developerMessage": "There are no problems with this request.", "code": 200}, "meta": {"href": "https://api.datavalidation.com/1.0/campaign-event/j7PdptJC74SOxMWp/", "etag": "BjRAWI8t"}, "data": {"status": "processing", "import_slug": "j7PdptJC74SOxMWp", "rows_imported": 0, "mapping": {"email_col": 0, "type_col": 2, "header_row": true, "ts_col": 1}, "status_detail": ""}}
~~~~

### Import Feedback Data from a CSV body POST

If you import .csv data directly into the body of the POST, you must include all mapping data in the command line. Please note that if you use curl to upload a .csv, you must make sure that the data you're uploading contains newline (\n) characters. Otherwise, the API will interpret your upload as a single (very long!) row. Save the "import_slug" to check the status and get details of your import.

**Parameters:**

* header (boolean): Specifies if there is a header row present in the .csv file

* timestamp "ts_row" (query): Which column contains the timestamp? (UTC seconds since the epoch) defaltValue: 0

* email address "email_col" (query): Which column contains the email address? Only one address per row. defaultValue: 1

* event type "type_col" (query): Which column contains event type? defaultValue: 2

Below is an example of actual .csv data from an import.

~~~~
defaultValue: |
  ts,email,type
  1440528585,test@example.com,sent
  1440528585,test@example.com,hard
  1440528585,test@example.com,open
  1440528585,test@example.com,click
  1440528585,test@example.com,abuse
  1440528585,test@example.com,unsubscribed
~~~~

To import data directly into the POST body, use the endpoint: POST "/campaign-event/_/data.csv"
Sample Command:

~~~~
curl -X POST \
-H "Content-Type: text/csv" \
-H "Authorization: bearer {api_key}" \
"https://api.datavalidation.com/1.0/campaign-event/_/ \
data.csv?header_row=true&ts_col=0&email_col=1&type_col=2" \
-d "ts,email,type
1440528585,test@example.com,sent
1440528585,test@example.com,hard
1440528585,test@example.com,open
1440528585,test@example.com,click
1440528585,test@example.com,abuse
1440528585,test@example.com,unsubscribed"
~~~~

Sample Output:

~~~~
{"status": 200, "message": "Everything's cool!", "developerMessage": "There are no problems with this request.", "code": 200}
~~~~

#### See Individual Import Details

Use your "import_slug" to check the status of your import. Checking import details will tell you whether or not there were problems with the import, what mapping you included for the .csv file, and what the import status is. If an import has finished, you'll find "status": "complete" within the details. To get import details, use the endpoint: GET "/campaign-event/{import_slug}/"

Sample Command:

~~~~
curl -L -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/campaign-event/{import_slug}/"
~~~~

Sample Output:

~~~~
{"status": {"status": 200, "message": "Everything's cool!", "developerMessage": "There are no problems with this request.", "code": 200}, "meta": {"href": "https://api.datavalidation.com/1.0/campaign-event/j7PdptJC74SOxMWp/", "etag": "BjRAWI8t"}, "data": {"status": "complete", "import_slug": "j7PdptJC74SOxMWp", "rows_imported": 0, "mapping": {"email_col": 0, "type_col": 2, "header_row": true, "ts_col": 1}, "status_detail": ""}}
~~~~

### See Which Imports Are In Progress & Complete

Check the progress of imports within your API Account. Using the "campaign-details" endpoint will automatically give you the imports that are currently in progress. Lists showing here will have the defaltValue of "status=processing". To see a list of imports that have completed, include "status=complete" at the end of your command line.

**Parameters:**

* api key: What is the Authorization Key?

* paging skip (query): Number of results to skip before returning first result?

* paging limit (query): "Total number of results to return?

* status (query): Is the file processing, complete, or returning an error?

Sample Command:

~~~~
curl -L -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/campaign-event/?status=complete"
~~~~

Sample Response:

~~~~
{"status": {"status": 200, "message": "Everything's cool!", "developerMessage": "There are no problems with this request.", "code": 200}, "meta": {"href": "https://api.datavalidation.com/1.0/campaign-event/"}, "data": {"items": [{"meta": {"href": "https://api.datavalidation.com/1.0/campaign-event/j7PdptJC74SOxMWp/", "etag": "BjRAWI8t"}, "data": {"status": "complete", "import_slug": "j7PdptJC74SOxMWp", "rows_imported": 0, "mapping": {"email_col": 0, "type_col": 2, "header_row": true, "ts_col": 1}, "status_detail": ""}}], "paging": {"skip": 0, "total": 1, "limit": 0}
~~~~

For more information on the deliverability data provided by DataValidation, please visit our <a href="http://www.datavalidation.com/kb/">Knowledge Base</a>.

