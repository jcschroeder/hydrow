##########################################################################
# Set up your initial read permissions (1 time)
# This program will use your Strava app's client keys to grant your app 
# activity:read_all permissions so you can get your data

# Copyright (C) 2022  Jeff Schroeder
##########################################################################
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/

import json
import requests
import dotenv 
import os

#------------- GET A REFRESH TOKEN THAT HAS ACTIVITY READ ACCESS ------------------
#Load API secrets from .env file.
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# MANUAL UPDATE REQUIRED: Follow the manual steps in the setup page
# Namely, paste this URL into a browser (update with your client ID) and copy the resulting "code" value into the code variable below
# https://www.strava.com/oauth/authorize?client_id=[INSERT YOUR CLIENT ID]]&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
code = '[YOUR ONE-TIME AUTH CODE]'

#Get a new refresh token for your app that has activity:read_all permission and update your .env file
params = {'client_id': client_id, 'client_secret': client_secret,'code': code, 'grant_type': 'authorization_code'}
url = 'https://www.strava.com/oauth/token'

refr = requests.post(url,params=params)

# TODO: error handling would also be nice here

rjson = json.loads(refr.text) 
new_refresh_token = rjson['refresh_token']
dotenv.set_key(dotenv_file, 'REFRESH_TOKEN', new_refresh_token)