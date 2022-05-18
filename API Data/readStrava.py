##########################################################################
# Read Strava API (no OAuth2)
# This program will use your Strava app's client keys to obtain an active
# refresh token, then will pull all of your activity into a json file. 
# This only works for the account that owns the app

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

from pathlib import Path
import json
import requests
import dotenv 
import os

#------------- REFRESH ACCESS TOKEN ------------------
#Load API secrets from .env file. For this individual pull, the .env file only needs to contain these 3 variables from the strava app
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
refresh_token = os.getenv('REFRESH_TOKEN')

#Access token lasts for 6 hours, then you need to refresh 
#First action is to  get a valid access token by posting to the authentication API
params = {'client_id': client_id, 'client_secret': client_secret,'grant_type':'refresh_token', 'refresh_token': refresh_token}
url = 'https://www.strava.com/oauth/token'

refr = requests.post(url,params=params)
rjson = json.loads(refr.text) 

#TODO: Adding error handling would be good here

#Strava documentation says you need to save the new refresh token, although it appears to be a constant. Including to future-proof
new_refresh_token = rjson['refresh_token']
dotenv.set_key(dotenv_file, 'REFRESH_TOKEN', new_refresh_token)

#Pull the valid access token from the json response
token = rjson['access_token']

#--------------- CALL ACTIVITY API ------------------
headers = {'Authorization': 'Bearer ' + token}
url = 'https://www.strava.com/api/v3/athlete/activities'
page = 1
jlist = []

#Strava paginates the response but doesn't return the number of pages
while True:
    params = {'client_id': client_id, 'client_secret': client_secret,'per_page':50, 'page':page}
    r = requests.get(url, headers=headers, params=params)
    
    j = json.loads(r.text)
    
    #This isn't best practice, but this while loop is small and this is easier
    if (not j):
        break
    
    jlist.extend(j)
    page += 1

#Set absolute path from where python script is stored to API folder
path = Path(__file__).parent

#Dump json result to the activity file
with open(path / "Data/stravaActivity.json", "w") as f:
    json.dump(jlist,f)