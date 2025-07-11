# Camp 100 BulletinPublishApp

Part of the Camp 100 Digital Bulletin System. 

## 'The Bulletin'
The bulletin is an announcement which is made 5 times per day set times. The idea being that it's the main way of getting news around the camp, for example: there's a bonus pea fair, some tofu has arrived, or Milo has lost his rain coat. 

## Technical & Process Overview
The data starts out life in a Google Form which plumbs automatically into a Google Sheet. When the Google Form is submitted - a Google AppsScript runs which sends a message to the Camp 100 Discord Server notifying people that there's a new entry to moderate. The 'Keepers of the Bulletin' then manually go into the Google Sheet and approve (by entering the number `1`, `2` or `3`) into the left-most column. Content not to be shown either because it's not appropriate, or because it's time for displaying is over is either deleted from the spreadsheet (by deleting it's row), or putting an `x` into the left-most column.

At 10-to the hours of publishing (i.e. 09:50 for the 10:00 bulletin), this script runs (BulletinPublishApp). It takes the Google Sheet and finds any records with either a 1, 2 or 3 in the left-most column. It sorts these so that all 1s are at the top, then 2s then 3s at the bottom; formats them into a WordPress post and bungs it onto the Camp 100 website. 

A reminder function also runs at 45-to the hour of publishing (i.e. 09:15 for the 10:00 bulletin), this is the sister script ([BulletinNotificationApp](https://github.com/ThomasBoxall/camp-100-bulletin-notification-app)) to this one. This simply sends a Discord message to the Keepers of the Bulletin reminding them what is currently approved for publication to remind them to approve/unapprove entries. 

The two main scripts (BulletinPublishApp and BulletinNotificationApp) run as Google Cloud Run Services which have a Google Cloud Scheduler Job triggering them to run. Both scripts log to the Google Cloud Logs, albeit in a massively obtuse & daft way (but it's too much effort to change). They do quite a lot of logging, as they run headlessly and it's nice to have something to help debugging when they break. Both scripts require a `config.yml` file to run, an example for which is provided in both repositories.  

### A quick aside on Discord Webhooks
Discord webhooks are the primary way of getting messages out to the Keepers of the Bulletin & coordination team etc. There are three webhooks used:
* **Admin** - used for admin notices. Things like error dumps, etc
* **General** - used for slightly more general notices, but still not public to everyone. For example - failure to publish. Also used by BulletinNewEntryApp and by BulletinNotificationApp.
* **Public** - used for announcing there's a new bulletin published. This could be the same as general if you didn't want to ping too many people all the time.

## Deployment Notes
Setting up spreadsheet of responses
* share with the service account's email address
* set spreadsheet ID in config.yaml
* set sheet name in config.yaml

Within WordPress
* set the default post category to be 'bulletin' - can't set this by code on create request
* disable comments on new posts - can't set this by code on create request 

Deploying to existing Google Cloud Environment
* `gcloud run deploy` command (not in this Repo) which creates a new revision of existing service
* Force run the relevant Cloud Scheduler job to test end-to-end functionality

Building New Google Cloud Environment
* `gcloud run deploy` command which will create the Cloud Run Service
* Open Google Cloud Run Console, add a Pub/Sub Trigger (Create new Topic, set the Region to europe-west2, give it a sensible name)
* Open Cloud Scheduler, add a new Job - set the TZ to GMT UTC+1 (so this won't work in winter, but we camp in the summer) and set the Execution Type to Pub/Sub pointing at the topic created on in the Run Console earlier.
* Force run the Cloud Scheduler Job to test End-To-End Functionality