road_less_travelled
===================

This tiny script sends me a Telegram message when there's abnormal traffic conditions (ie. when Google Maps recommends a route that is not my usual route).

(It only uses Telegram because that's the easiest / cheapest way to get push notification to my phone without bothering with a custom app).

Usage / Configuration
---------------------
Use the example config.ini and fill in the blanks.

`telegram_id` is your own ID on Telegram (It's not your phone number or username, it's a number).

To find your telegram ID, send your bot a message and then visit this URL
`https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
and copy the ID from there.

If you're not sure how Google Maps describes your usual route, leave this field blank and the script will print out possible routes to pick.

Once you verify it works correctly (hint: set the usual route to something else just to see if it sends a message), you can set a cronjob
to run the script when you need it to run.
