# Synopsis

This is a DjangoLDP-Package for modelling Job-Offers (job postings), as they associate to the package DjangoLDP-Skill



# JobOffer Notifications

If you create a subscription on another server with:
* the target `/job-offers/`
* the inbox recipient of your `SITE_URL` (check settings) followed with the path `/job-offers/inbox/`
* `disable_automatic_notifications` checked (set to `True`)

When a JobOffer is created on that server, all users on this server will be sent a notificaiton provided that they have one or more skills matching the JobOffer.

JobOffer notifications will be sent to local users by default. You can disable this feature by setting (in `settings.yml`):
```yaml
ENABLE_JOBOFFER_NOTIFICATIONS: False
```
