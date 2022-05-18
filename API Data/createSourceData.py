##########################################################################
# Create JSON data for Dashboard
# This program reads raw activity data (json) from the Strava API and 
# transforms it into multiple json files for use as the source data for 
# a dashboard on a static webpage / localhost

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
import datetime
import pandas as pd
import numpy as np

#---------INITIAL DATAFRAME BUILD------------------
#This is the base dataset used for all the charts
#Set absolute path from where python script is stored to API folder
path = Path(__file__).parent

#JSON file loaded to data var
strava = path / "Data/stravaActivity.json"
with strava.open() as f:
  data = json.load(f) #Data is a list of dictionaries

#Make dictionary into a dataframe
df = pd.DataFrame(data)

#----------USER CHANGE REQUIRED------------------
#This takes my Strava data -7 hours to Pacific Time. Adjust as necessary so your dates are correct
#-------------------------------------------------
df['start_date'] = pd.to_datetime(df['start_date']) - datetime.timedelta(hours=7)

#Add a column that categorizes the row by week number (added year to avoid issues when we hit the next year)
week = df['start_date'].dt.isocalendar().week
year = df['start_date'].dt.isocalendar().year
df = df.assign(yrweek=100*year+week)

#Need to sort by date, otherwise most of the charts will be backward
df.set_index('start_date', drop=True, append=False, inplace=True, verify_integrity=False)
df = df.sort_index()
df = df.reset_index()


#----------------------CURRENT PROGRESS CHART--------------------
#For chartweeks.json, I need a json file that has:
#Week: starting at 0
#TotalActual: distance column, calculated by summing all distance for a given week; cumulative
#Total36 and Total32: hardcoded values that were my original predictions; these have been removed from the chart for now
#TrendEx: 2nd order polynomial predicted finish based on all past weeks performance (ignores current week)
#TrendLin: linear regression predicted finish based on all past weeks performance (ignores current week)
Total32 = [15,30,50,70,90,114,144,174,204,234,264,296.5,329,361.5,394,426.5,459,491.5,524,556.5,591.5,626.5,661.5,699,736.5,774,811.5,849,886.5,924,962,1000,None,None,None,None]
Total36 = [15,30,50,70,90,115,140,165,190,220,250,280,310,340,370,400,430,460,490,520,550,580,610,640,670,700,730,760,790,820,850,880,910,940,970,1000]
Week = list(range(1,len(Total36)+1)) #X values for the chart

#Set up the currentweek df with hardcoded columns. These are kept just as a lazy way to set the length to 36
cw = pd.DataFrame({'Week':Week,'Total32':Total32,'Total36':Total36})

#This will do the sums and group into a DF with yrweek as the index and a single unlabeled column of distance sums (thousands of m)
distance = df.groupby('yrweek', as_index= False)['distance'].sum()/1000 #as_index false used so cw is a dataframe instead of series
distance = distance.cumsum() #cumulative total distance instead of weekly distance

#Add the distance column and rename to "TotalActuals"
cw = pd.concat([cw, distance], axis=1)
cw.drop('yrweek', axis=1, inplace=True) #Can do these two things together, but making it more readable
cw.rename(columns = {'distance':'TotalActual'}, inplace = True)

#Projected Finish with numpy
y_data = cw['TotalActual'].dropna().iloc[:-1] #Keep current week out of calculation since it's partial
x_data = cw['Week'].iloc[:len(y_data)] #Use only the corresponding X values where y data exists
a,b,c = np.poly1d(np.polyfit(x_data, y_data, 2)) #2nd degree polynomial variables
slope, intercept = np.polyfit(x_data, y_data, 1) #linear regression variables

#2nd degree polynomial projection
x_data = cw['Week'] #back to full list of x values for trendline
x_data.rename('TrendEx', inplace = True) #So we don't have 2 "Week" columns
trendEx = round((a*(x_data**2) + b*x_data + c),1) #Calculate y values (within dataframe) based on x values (week number)
trendEx[trendEx > 1000] = np.nan #Cut out anything >1M, replace with NaN (so chart range is intact)

#Linear regression
x_data.rename('TrendLin', inplace = True) #So we don't have 2 "Week" columns
trendlin = round((x_data*slope + intercept),1) #Calculate y values

cw = pd.concat([cw,trendEx, trendlin], axis=1)

#Add zeros row at the top for Week 0
cw.loc[-1] = [0,0,0,0,0,0]
cw.index = cw.index + 1
cw.sort_index(inplace=True) 

#Write result to a json file 
with open(path / "Data/chartweeks.json", "w") as cwf:
    json = cw.to_json(orient='records')
    cwf.write(json)

#-------------------- POWER/SPI CHARTS --------------------
#For chartworkoutdays, need:
#Days starting at 1
#AvgWatts: average power for each workout 10 min+
#MaxWatts: max power for each workout 10 min+
#Trend: linear trendline for Power chart
#SPI: average watts/strokes per min

#Filter original df to only the power columns
pw = df.filter(items=['elapsed_time','start_date','average_watts','max_watts','average_cadence', 'name'])

#Filter out all cool downs and warm ups (some are 10 min)
cdwu = pw['name'].str.contains("Cool-Down|Warm-Up")
pw = pw[~cdwu]

#Filter out everything under 10 min
pw = pw[(pw['elapsed_time']>=600) & (pw['average_watts']>0) & (pw['max_watts']>0)].reset_index()

spi = pd.DataFrame(pw['average_watts']/pw['average_cadence'], columns=['SPI'])

#add a "Days" column for x values
days = pd.DataFrame({'Day':list(range(1,len(pw)+1))})
pw = pd.concat([days,pw,spi], axis=1)
pw.drop(['index','elapsed_time', 'start_date','average_cadence','name'], axis=1, inplace=True) #Drop extra columns
pw.rename(columns = {'average_watts':'AvgWatts','max_watts':'MaxWatts'}, inplace = True) #name as needed for json file

#Power Trend Line (linear regression)
x_data = pw['Day']
y_data = pw['AvgWatts']
slope, intercept = np.polyfit(x_data, y_data, 1) 

x_data.rename('Trend', inplace = True) #So we don't have 2 "Day" columns
trend = round((x_data*slope + intercept),1)
pw = pd.concat([pw,trend], axis=1)

#Write result to a file 
with open(path / "Data/chartworkoutdays.json", "w") as pwf:
    json = pw.to_json(orient='records')
    pwf.write(json)

#-------------- INDIVIDUAL METRICS ------------------------------
#For chartmetrics, need:
#Week: current week, Monday - based (go from 202212 and count)
#PercentComplete: totalM / 1M, percentage
#RowDays: number of row workouts
#OTMDays: number of OTM workouts
#AvgMperDay: per workout day, doesn't count empty days
#CurrentTotalM: max value from distance column

CurrentTotalM = cw['TotalActual'].loc[cw['TotalActual'].idxmax()] #Max value from cumulative total distance
PercentComplete = str(round((CurrentTotalM / 10),1))+'%' #since it's in thousands of meters already, this is divided by 1M and showing as a %
Week = cw['TotalActual'].idxmax() #uses index from total actual, which matches Week since we have a 0 row

#Rowing Days
rdf = df.where(df['type'] == 'Rowing') #only Rowing rows
rdf = pd.DataFrame(rdf.groupby(pd.Grouper(key='start_date',axis=0,freq='D'))['type'].count()) #count by date so we only count each workout day once
rdf = rdf.loc[(rdf!=0).any(axis=1)] #only take rows with a count >0
RowDays = len(rdf)

#OTM Days
odf = df.where(df['type'] != 'Rowing')
odf = pd.DataFrame(odf.groupby(pd.Grouper(key='start_date',axis=0,freq='D'))['type'].count())
odf = odf.loc[(odf!=0).any(axis=1)]
OTMDays = len(odf)

AvgMperDay = int(round((CurrentTotalM*1000 / RowDays),0)) #Basic math

CurrentTotalM = int(round(CurrentTotalM))#Round to int after it's used for all operations

#Make a dataframe of these individual metrics just to use the same file dump method
met = pd.DataFrame({'Week':Week,'PercentComplete':PercentComplete,'RowDays':RowDays, 'OTM Days': OTMDays, 'AvgMperDay': AvgMperDay, 'CurrentTotalM':CurrentTotalM}, index=[0])

#Write result to a file 
with open(path / "Data/chartmetrics.json", "w") as mpf:
    json = met.to_json(orient='records')
    mpf.write(json)


#---------------------- COPY FILES ---------------------
#Temporary copy paste from API folder to Site folder; can restructure to just write to the Dashboard folder above if desired.
import shutil
files = [path / "Data/chartweeks.json", path / "Data/chartworkoutdays.json", path / "Data/chartmetrics.json", ]
for f in files: 
    shutil.copy(f,path.parent / "Dashboard/data")