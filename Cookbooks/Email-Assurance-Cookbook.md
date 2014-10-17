Email Assurance for ESPs
=======================

This cookbook will discuss use cases and implementation of Email Assurance (Ongoing Monitoring and Remediation) using the DataValidation Batch API. Email Assurance for ESPs is only available at the subscription level. If you are on a pay-as-you-go plan, you will need to upgrade to a subscription prior to beginning this integration. The cost of a subscription is based on the total number of subscribers in your database and includes unlimited API calls and token usage. 

An email service provider can use these instructions to onboard new users, monitor existing users, and remediate lists daily/weekly. 

Overview of Email Assurance
-----------------

#### Email Assurance Report

[Go to API Documentation on retrieving reports.]()

This report is an overview of an email list’s quality. It includes the total number of subscribers in each grade category, A+, A, B, D, and F, and an overall grade for the list. This report does not provide data on specific email addresses. 

**Uses of this report:** 

*   **When onboarding a new user** - retrieve Email Assurance Reports on all of the lists a prospective/new user intends to use. These reports can be used to determine whether to accept the user as a trusted sender. If the user has several problematic lists, remediation can be recommended prior to deploying mail. If the user has highly questionable lists, it can be required that these lists be removed and not used in the ESP platform. 

*   **Prior to deploying email from a previously inactive user account** - after a user has not deployed email for at least 3 months, retrieve an Email Assurance Report on the list prior to allowing the email to be deployed. If the data is acceptable, the user can move forward without remediation. If not, the user can be recommended remediation prior to deploying the campaign. 

*   **When a current user imports a new list** - retrieve an Email Assurance Report prior to allowing email to be deployed. If the data is acceptable, the user can move forward without remediation. If not, the user can be recommended remediation prior to deploying the campaign. If the list is too risky, it can be disallowed altogether. 

*   **Embed the data to allow users to always see the Email Assurance Report** - users can always know the list quality so it is not a surprise if remediation is recommended.


#### Email Assurance Grade

[Go to API Documentation on retrieving grades.]()

This grade — A+, A, B, D, or F— indicates an emails likelihood to be deliverable. Additional deliverability data is provided with the grade. Email Assurance Grade data is provided with the usage of a remediation token, or subscription.  
     
   A+ indicates engagement history such as click or optin. 
   A indicates successful delivery history or a positive SMTP response. 
   B indicates an accepts all domain. 
   D indicates no response from a server, or temporary failure. 
   F indicates an undeliverable address due to history of bounces, or a negative SMTP response. 

**Uses of the grades:**

*   **Determine what grades a user can deploy email to** - A+ and A results are deliverable based on our most recent data. If a user is a trusted sender, perhaps B results can be allowed. D results should not be deployed email. F results should be unsubscribed.




Onboarding New Users
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

This is important:

>You **must PUT member updates on *all* the members in your database at least once every 30 days**. When an email address or list has not been touched in 30 days, we remove it from our database. If this happens, the email list and all members will need to be created in the API again. 
>
>This API does not currently support scheduling jobs. You should set up a periodic task in your code to create jobs in the API. These periodic tasks can be utilized to set up ongoing monitoring and ongoing remediation. 
>
>Because the grades are being updated daily in our system, you can retrieve the member level grades for all lists daily or weekly. Export.csv does not PUT updates to the members on a list.
>

This API does not currently support filtering members by grade. After calling export.csv you may want to input this data into your users' accounts and set up a task in your code to automatically unsubscribe the F results. 
