#!/usr/bin/env python3
# roadlesstravelled.py
#
# Copyright 2018 Elad Alfassa <elad@fedoraproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
import googlemaps
import configparser
import telegram
from datetime import timedelta
from urllib.parse import quote_plus
from dateutil.parser import parse as parse_date

MESSAGE_TEMPLATE = """<b>Unusual traffic today</b> 🚗⚠️
----------------------------------
Depart at <b>{depart_at}</b> to arrive by <b>{arrive_by}</b>.

🛣️ Recommended:
{recommended} -     ⏰  <b>{duration}</b>

{warnings}

Other options:

{other_routes}

{maps_link}
"""


def send_message(text, config):
    """ Send a message via telegram """
    bot = telegram.Bot(config['lesstravelled']['telegram_token'])
    bot.send_message(config['lesstravelled']['telegram_user_id'], text,
                     parse_mode='HTML')


def sort_routes(routes, mode="duration_in_traffic"):
    """ Sort routes according to duration """
    return sorted(routes, key=lambda alternative: alternative['legs'][0][mode]['value'])


def build_url(origin, destination):
    """ Build a google maps URL """
    BASEURL = 'https://www.google.co.il/maps/dir/{0}/{1}'
    return BASEURL.format(quote_plus(origin), quote_plus(destination))


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    apikey = config['lesstravelled']['apikey']
    origin = config['lesstravelled']['origin']
    destination = config['lesstravelled']['destination']
    depart_at = parse_date(config['lesstravelled']['depart_at'])
    if 'usual_route' in config['lesstravelled']:
        usual_route = config['lesstravelled']['usual_route']
    else:
        usual_route = None

    gmaps = googlemaps.Client(apikey)

    directions_result = gmaps.directions(origin,
                                         destination,
                                         alternatives=True,
                                         departure_time=depart_at)

    sorted_routes = sort_routes(directions_result)

    if usual_route is None or usual_route.strip() == '':
        print("Usual route not defined. Possible routes: ")
        print([route['summary'] for route in sorted_routes])
        return

    if sorted_routes[0]['summary'] != usual_route.strip():
        # Unusual route!
        best_route = sorted_routes[0]
        # We use ['legs'][0] because a trip with only two points will
        # always have one leg.
        arrive_by = depart_at + timedelta(seconds=best_route['legs'][0]['duration_in_traffic']['value'])
        params = {'recommended': best_route['summary'],
                  'warnings': '⚠️' + ','.join(best_route['warnings']) if len(best_route['warnings']) > 0 else '',
                  'duration': best_route['legs'][0]['duration_in_traffic']['text'],
                  'depart_at': depart_at.strftime("%H:%M"),
                  'arrive_by': arrive_by.strftime("%H:%M"),
                  'maps_link': build_url(origin, destination)}

        # Build list of durations for other routes
        other_routes = []
        for route in sorted_routes[1:]:
            other_routes.append('{0} -     <b>{1}</b>'.format(route['summary'],
                                                          route['legs'][0]['duration_in_traffic']['text']))
        params['other_routes'] = '\n'.join(other_routes)

        message = MESSAGE_TEMPLATE.format(**params)

        send_message(message, config)


if __name__ == "__main__":
    main()
