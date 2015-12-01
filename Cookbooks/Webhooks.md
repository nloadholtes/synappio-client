Webhooks
========

Webhooks are an easy way for API Users to retrieve notifications. These are similar to our API endpoints, but instead of making a call to the API, you'll define a calback URL and we'll provide PUSH notifications as events happen within your API Account.

DataValidation's API allows you to validate email addresses in real-time or in batch, and also provides a way to fully automate list maintenance. API users can create Lists, Imports and Validation Jobs, and then export results through the API. Our Webhooks notify users upon completion of these real-time and batch events. Webhooks allow users to know when an email address has validated in real-time, an Import has completed, and a Validation Job is complete.

To test our Webhooks before setting up scripts, the <a href="http://requestb.in/" target="_blank">RequestBin</a> tool will help you see data come across as various events happen in our system. Configuration is simple: Enter a valid url for us to contact, then select the events and event sources (see below for descriptions) you want to have sent to you.

You will receive a HTTP POST containing JSON for event notification, and these POSTs will be sent to the URL you have defined. For example, include **put -d '{"href":"http://requestb.in/abcdefg"}'** in your Webhook. Webhooks may be sent up to 60s after the event they're tracking during normal operation, and this is subject to change

### Webhook Events
We support the following events [hook_type] with our Webhooks implimentation. Use the path: /hook/{hook_type}/ for reteiving notification for specific events.

*   (realtime) Receive a notification when an email address has been validated in real-time.
*   (batch) Receive notifications when batch events have completed.

### List Existing Webhooks

Use this request to list all of the Webhooks you currently have set up for your API Account.

Request:

~~~~
curl -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/webhook/?pretty=true"
~~~~

Response:

~~~~
{
    "status": {
        "status": 200,
        "message": "Everything's cool!",
        "developerMessage": "There are no problems with this request.",
        "code": 200
    },
    "meta": {
        "href": "http://core-hook/hook/1.0/hook/"
    },
    "data": {
        "items": [
            {
                "meta": {
                    "href": "http://core-hook/hook/1.0/hook/realtime/"
                },
                "data": {
                    "href": "http://requestb.in/abcdefg",
                    "type": "realtime",
                    "created": "2015-10-06T14:53:48.434000Z"
                }
            }
        ],
        "paging": {
            "skip": 0,
            "total": 1,
            "limit": 0
        }
    }
~~~~

### Real-time Notifications

Using this Webhook, you can see when email addresses get validated in real-time. Each time an address gets validated with the real-time, you'll receive a notification to the URL you have defined.

Request:

~~~~
curl -X PUT -d '{"href":"http://requestb.in/abcdefg"}' -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/webhook/realtime/"
~~~~

Response:
When the Webhook has been successfully setup, you'll see a response similar to the one below.

~~~~
{"status": {"status": 200, "message": "Everything's cool!", "developerMessage": "There are no problems with this request.", \
"code": 200}, "meta": {"href": "http://core-hook/hook/1.0/hook/realtime/"}, "data": {"href": "http://requestb.in/abcdefg", \
"type": "realtime", "created": "2015-12-01T17:01:57.010650Z"}}
~~~~

### Batch Notifications

List Imports within your API Account should be 100% complete before starting a Validation Job. Validation Jobs will be 100% complete before results will be available for export. Batch notifications will send an event notification to the desired URL when batch imports and jobs have completed, so you can start the next step of the validation process immediatly.

Request:

~~~~
curl -X PUT -d '{"href":"http://requestb.in/abcdefg"}' -H "Authorization: bearer {api_key}" \
"https://api.datavalidation.com/1.0/webhook/batch/"
~~~~

Response:
When the Webhook has been successfully setup, you'll see a response similar to the one below.

~~~~
{"status": {"status": 200, "message": "Everything's cool!", "developerMessage": \
"There are no problems with this request.", "code": 200}, "meta": {"href": "http://core-hook/hook/1.0/hook/batch/"}, \
"data": {"href": "http://requestb.in/17b73g01", "type": "batch", "created": "2015-12-01T18:56:27.534737Z"}}
~~~~

#### Import Complete

Imports must be 100% complete prior to creating a Validation Job. Using the Batch Notififcation Webhook, you'll see a notification similar to the one below when a list Import is complete.

~~~~
{"subject": "import.complete", "type": "batch", "slug": "{list_slug}", "ts": "2015-12-01T19:23:31.090000Z", \
"detail": {"status": "Complete", "list_slug": "{list_slug}", "account_id": "{account_id}", "tags": [], \
"created": "2015-12-01T19:23:28.358000Z", "mapping": {"header_row": false, "email_col": 0, \
"include_metadata": false}, "note": "Changed Results Test", "href": \
"https://www.dropbox.com/s/kshfkjdfkjhas/Test-List.csv?dl=1", "validate": false, \
"total_imported": 5347, "slug": "{import_slug}"}}
~~~~

#### Validation Job Complete

Validation Jobs must be 100% complete before results can be exported. Using the Batch Notification Webhook, you'll see a notfication similar to the one below when a Validation Job is complete.

~~~~

{"subject": "job.complete", "type": "batch", "slug": "{list_slug}", "ts": "2015-12-01T19:57:12.533000Z", \
"detail": {"stats_only": false, "status": "Ready", "list_slug": "__assurance__", "stats": {"optout": \
[{"count": 343574693, "name": "O4"}], "grade": [{"count": 158965414, "name": "A"}, {"count": 26792972, \
"name": "A+"}, {"count": 67511213, "name": "B"}, {"count": 47398587, "name": "D"}, {"count": 42906507, \
"name": "F"}], "hard": [{"count": 115225, "name": "H3"}, {"count": 343459468, "name": "H4"}], "click": \
[{"count": 261777857, "name": "K0"}, {"count": 77926837, "name": "K1"}, {"count": 1362009, "name": \
"K2"}, {"count": 405075, "name": "K3"}, {"count": 2102915, "name": "K4"}], "trap": [{"count": 5193413, \
"name": "T1"}, {"count": 338381280, "name": "T4"}], "open": [{"count": 260876503, "name": "R0"}, \
{"count": 66001344, "name": "R1"}, {"count": 4474422, "name": "R2"}, {"count": 2103798, "name": "R3"}, \
{"count": 10118626, "name": "R4"}], "complain": [{"count": 9439, "name": "W3"}, {"count": 343565254, \
"name": "W4"}], "deceased": [{"count": 289180, "name": "D1"}, {"count": 343285513, "name": "D4"}]}, \
"account_id": "jazimba", "created": "2015-11-22T02:00:52.259000Z", \
"skip_dha": false, "priority": {"mu": -1000, "sigma": 500}, "analyze_only": false, \
"pct_complete": 100, "slug": "{job_slug}"}}

~~~~

### Delete a Webhook

Delete a webhook from your account using the request below. Specify which Webhook you'd like to DELETE by listing the hook-type (realtime or batch).

Request:

~~~~
curl -X DELETE -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/webhook/hook-type/"
~~~~

Response:

You will receive back an empty response when deleting a Webhook, as the Webhook will be no longer available.

### Events API

This is a way for API Users to see all of the events recorded that would have been sent as a notification via a Webhook. See all of the events with the command listed below.

Command:

~~~~
curl -H "Authorization: bearer {api_key}" "https://api.datavalidation.com/1.0/event/?pretty=true"
~~~~

Response:

~~~~
{
    "status": {
        "status": 200,
        "message": "Everything's cool!",
        "developerMessage": "There are no problems with this request.",
        "code": 200
    },
    "meta": {
        "href": "http://core-hook/hook/1.0/event/"
    },
    "data": {
        "items": [
            {
                "meta": {
                    "href": "http://core-hook/hook/1.0/event/SroyIv5Q27uWKMhc/"
                },
                "data": {
                    "responses": [
                        {
                            "error_detail": "",
                            "response_headers": {
                                "content-length": "2",
                                "via": "1.1 vegur",
                                "server": "gunicorn/19.3.0",
                                "sponsored-by": "https://www.runscope.com",
                                "connection": "keep-alive",
                                "date": "Tue, 01 Dec 2015 19:57:47 GMT",
                                "content-type": "text/html; charset=utf-8"
                            },
                            "response_status": 200,
                            "ts": "2015-12-01T19:57:47.830000Z",
                            "response_body": "ok",
                            "hook_href": "http://requestb.in/17b73g01"
                        }
                    ],
                    "detail": {
                        "stats_only": false,
                        "status": "Ready",
                        "list_slug": "__assurance__",
                        "stats": {
                            "optout": [
                                {
                                    "count": 372212536,
                                    "name": "O4"
                                }
                            ],
                            "grade": [
                                {
                                    "count": 172251224,
                                    "name": "A"
                                },
                                {
                                    "count": 25487695,
                                    "name": "A+"
                                },
                                {
                                    "count": 67912477,
                                    "name": "B"
                                },
                                {
                                    "count": 56070084,
                                    "name": "D"
                                },
                                {
                                    "count": 50491056,
                                    "name": "F"
                                }
                            ],
                            "hard": [
                                {
                                    "count": 109412,
                                    "name": "H3"
                                },
                                {
                                    "count": 372103124,
                                    "name": "H4"
                                }
                            ],
                            "complain": [
                                {
                                    "count": 9711,
                                    "name": "W3"
                                },
                                {
                                    "count": 372202825,
                                    "name": "W4"
                                }
                            ],
                            "trap": [
                                {
                                    "count": 5282590,
                                    "name": "T1"
                                },
                                {
                                    "count": 366929946,
                                    "name": "T4"
                                }
                            ],
                            "open": [
                                {
                                    "count": 291581401,
                                    "name": "R0"
                                },
                                {
                                    "count": 64776667,
                                    "name": "R1"
                                },
                                {
                                    "count": 4254392,
                                    "name": "R2"
                                },
                                {
                                    "count": 2018929,
                                    "name": "R3"
                                },
                                {
                                    "count": 9581147,
                                    "name": "R4"
                                }
                            ],
                            "click": [
                                {
                                    "count": 292420161,
                                    "name": "K0"
                                },
                                {
                                    "count": 76169832,
                                    "name": "K1"
                                },
                                {
                                    "count": 1254246,
                                    "name": "K2"
                                },
                                {
                                    "count": 386466,
                                    "name": "K3"
                                },
                                {
                                    "count": 1981831,
                                    "name": "K4"
                                }
                            ],
                            "deceased": [
                                {
                                    "count": 307449,
                                    "name": "D1"
                                },
                                {
                                    "count": 371905087,
                                    "name": "D4"
                                }
                            ]
                        },

~~~~


