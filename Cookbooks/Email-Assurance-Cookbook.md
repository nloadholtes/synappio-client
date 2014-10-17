Email Assurance for ESPs
=======================

This cookbook will discuss use cases and implementation of Email Assurance (Ongoing Monitoring and Remediation) using the DataValidation Batch API. Email Assurance for ESPs is only available at the subscription level. If you are on a pay-as-you-go plan, you will need to upgrade to a subscription prior to beginning this integration. The cost of a subscription is based on the total number of subscribers in your database and includes unlimited API calls and token usage. 

An email service provider can use these instructions to onboard new users, monitor existing users, and remediate lists daily/weekly. 

Overview of Email Assurance
-----------------

During the onboarding process, this API allows you to retrieve list level data and quickly view the data quality on an email list. Every email address is scanned on a list and you are provided an Email Assurance Report. This report is an overview of an email list’s quality. It includes the total number of subscribers in each grade category, A+, A, B, D, and F, and an overall grade for the list. 

After viewing the Email Assurance Report, there are several possible scenarios:

*	Onboard a user without remediation 
*	Onboard a user and remediate select lists
*	Onboard a user and remediate all lists
*	Do not onboard a user 

As the ESP, you decide which grades you are going to allow your users to deploy email to. During the onboarding process, you may think about having stricter compliance thresholds around what grades you will allow a user to email. For example, we always recommend unsubscribing the F grades but maybe at onboarding you require the user to remove D grades as well. 

Once a user has been onboarded, we recommend creating a "Safe to Send" segment for A+ and A grades. This should not be a static segment, as every time you update the list members you will want the new A+ and A grades to auto-populate in the segment. This segment allows your users to quickly deploy mail to the deliverable email addresses. You may also want to create segments for B and D grades. A B result can be upgraded to an A+ if our system detects positive engagement, or downgraded to an F if it detects negative engagement. The same holds true with the D results. This data is not reliant on *your* users deploying mail to B and D results.

Ongoing monitoring allows you to retrieve an Email Assurance Report for a list at anytime. As the ESP you can keep this data internal, or maybe you want to build a widget in your user dashboard to display the Email Assurance Report data for users to see. If you choose to do this, we recommend displaying only the Email Assurance Grades rather than all of the deliverability data on the user dashboard. 

Ongoing remediation provides you with Email Assurance grades and deliverability data for each member on a list. This data can be added to the merge fields in a user's list. You may choose to update only one merge field with Email Assurance grades, or you may choose to update multiple merge fields with all of the deliverability data. If a user has a large number of merge fields already, you will only want to add the Email Assurance grade. We have found that most users only care about the grade. 

We run Email Assurance daily on all of the email addresses in our database. When you make an API call to retrieve a report or a member grade, we return the most recent data in our system. 

**This is important:**

You **must PUT member updates on *all* the members in your database at least once every 30 days**. When an email address or list has not been touched in 30 days, we remove it from our database. If this happens, the email list and all members will need to be created in the API again. 

This API does not currently support scheduling jobs. You should set up a periodic task in your code to create jobs in the API. These periodic tasks can be utilized to set up ongoing monitoring and ongoing remediation. 

Because the grades are being updated daily in our system, you can retrieve the member level grades for all lists daily or weekly. Export.csv does not PUT updates to the members on a list.

This API does not currently support filtering members by grade. After calling export.csv you may want to input this data into your users' accounts and set up a task in your code to automatically unsubscribe the F results. 


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
     
>A+ indicates Deliverable + Engagement History  
>A indicates Deliverable 
>B indicates Accepts-All 
>D indicates Indeterminate 
>F indicates Undeliverable

**Uses of the grades:**

*   Determine what grades a user can deploy email to - A+ and A results are deliverable based on our most recent data. If a user is a trusted sender, perhaps B results can be allowed. D results should not be deployed email. F results should be unsubscribed.

*	Emails graded with B or D cannot be confirmed deliverable or undeliverable unless mail is deployed to these codes. You may consider allowing these grades to remain on a user's list with the understanding that they cannot be mailed to *unless* the grade changes to an A+ or A. 


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



Onboarding New Users
-----------------
