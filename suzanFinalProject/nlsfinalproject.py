#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 13:51:46 2020

@author: nilou
"""
import pandas as pd
import numpy as np
#import data file, split data file, take only what columns i need, make nnew file
#check data, time, lat long, make sure all are in correct format
datafile = pd.read_csv('finalProj_hourly_so2_2020.csv', low_memory = False)
#subsampled of just the stuff I want, no column names changed
Ssub = datafile[['County Code','Site Num', 'Latitude', 'Longitude', 'Date Local',
                 'Time Local', 'Sample Measurement', 'Units of Measure','State Name', 
                 'County Name', 'Method Name']]
#(there WAS a bug here): I cannot figure out why I have to rename a column of Ssub and 
#then call it ressub for the subsequent conversion/filter line to work. something about how it 
#cannot be a copy of a slice from the original df "(A value is trying 
#to be set on a copy of a slice from a DataFrame.)" fixed it by using .loc (didnt fix)

#made new column same as time local called it morning T
Ssub.loc[:,('MorningT')] = Ssub.loc[:,('Time Local')].copy()
#split MorningT so it is just a number, convert to numeric so I can filter
Ssub.loc[:,('MorningT')]= pd.to_numeric(Ssub['MorningT'].str.split(':',expand = True)[0])
#filter for morning rush hour times 6 to 9am, and only uv flu method, made new df
ressub = Ssub[((Ssub['MorningT'] <= 9) &(Ssub['MorningT'] >= 6)&(Ssub['Method Name'] == 
               'INSTRUMENTAL - ULTRAVIOLET FLUORESCENCE'))]
#make new df (not in ressub because it wont be the same length) average of 
#every month 6-9am at every unique location 
##first, split date local into just the value of the month make new column
ressub.loc[:,('Month num')] = Ssub.loc[:,('Date Local')].copy()
ressub.loc[:,('Month num')] = pd.to_numeric(ressub['Month num'].str.split('/',
           expand = True)[0])
#make new df of just stuff I am going to be filtering for (month, specific site)
#how many sites will I be analyzing for? 
#just found out that not all the sites have the same amount of date data 
 

        
#check how many different sites 
    #there are PROBLEM there are more lat longs than counties, 
    #and there are more coutnies than site numbers
    #to solve this I am going to make a dict that matches a site number to a lat long
    
#print(len(pd.unique(ressub['County Code'])))
#print(len(pd.unique(ressub['Site Num'])))
#print(len(pd.unique(ressub['Latitude'])))
#put all the unique site numbers in a variable
sitenums = ressub['Site Num'].unique()


# i am trying to sort by site number and month, so that I can take the average 
#of the sample measurements per site number per month, but I cannot isolate them (ok i did it!)

#JAN VALUES FOR ALL SITE NUMBERS
meanvalsjan = []
for i in sitenums: 
    temp = ressub[(ressub['Site Num'] == i)&(ressub['Month num'] == 1)]
    meanvalsjan.append(temp['Sample Measurement'].mean())

#FEB VALUES FOR ALL SITE NUMBERS
meanvalsfeb = []
for i in sitenums:
    temp = ressub[(ressub['Site Num'] == i)&(ressub['Month num'] == 2)]
    meanvalsfeb.append(temp['Sample Measurement'].mean())
#MARCH VALUES FOR ALL SITE NUMBERS
meanvalsmar = []
for i in sitenums:
    temp = ressub[(ressub['Site Num'] == i)&(ressub['Month num'] == 3)]
    meanvalsmar.append(temp['Sample Measurement'].mean())
#APRIL VALUES FOR ALL SITE NUMBERS
meanvalsapr = []
for i in sitenums:
    temp = ressub[(ressub['Site Num'] == i)&(ressub['Month num'] == 4)]
    meanvalsapr.append(temp['Sample Measurement'].mean())    
 
#ok I have averages of all the months, i want to now make a data frame that is
    #sites on the y axis and months on the x axis 

#first, concatonate all the arrays together into a 4x59 dataframe
    #at some point I need to add column and row names
meanvalsall = pd.DataFrame(zip(sitenums,meanvalsjan,meanvalsfeb,
                               meanvalsmar,meanvalsapr))
#now that its one dataframe, I want to add the location data into it 
#find the latitude and longitude for each specific site, store in own dictionary
    #there is a problem here - some site numbers have multiple county codes but solution below
    #because there are multiple latitudes for each site num, im just going to pick the first one
print(len(alldataDF['Mean Values April'].dropna()))
latdata = []
for i in sitenums:
    temp = ressub[(ressub['Site Num'] == i)]
    temp2 = pd.unique(temp['Latitude'])
    #print(temp2[0])
    latdata.append(temp2[0])
    
longdata = []
for i in sitenums:
    temp = ressub[(ressub['Site Num'] == i)]
    temp2 = pd.unique(temp['Longitude'])
    longdata.append(temp2[0])

locationdata = dict()
locationdatamean = {'site number': sitenums, 'lats': latdata, 'longs': longdata,
                'Mean Values Jan': meanvalsjan, 'Mean Values Feb': meanvalsfeb,
                'Mean Values March': meanvalsmar, 'Mean Values April': meanvalsapr}

#next step is to arrange all the pertinent data into one data frame 
alldataDF = pd.DataFrame.from_dict(locationdatamean)

#now I want to add a value that converts the mean values into a converted greyscale,
    #add that as a column in the data frame

import pygmt
fig = pygmt.Figure()
#i want all of america because i have a bunch of states as seen here
statename = pd.unique(ressub['State Name'])

fig.coast(
    region=[-115, -70, 25, 45],
    projection='M4i',
    shorelines=True,
    water='lightblue',
    land='white',
    frame=True,
)

#JAN VALUES

jancolor = []
for i in alldataDF['Mean Values Jan']:
    jancolor.append(str(i*255/10))

#need to define the coords in a new variable
coordscolorjan = list(zip(longdata,latdata,jancolor,sitenums))

for clong,clat,col,sitnm in coordscolorjan:  
    fig.plot(
        x=clong,
        y=clat,
        style='c0.1i',
        color= col,
        pen='black',
        label= sitnm
    )

fig.show()
fig.text(text = 'January 2020', x = -90, y = 28 )

########################
#FEB VALUES
fig2 = pygmt.Figure()

fig2.coast(
    region=[-115, -70, 25, 45],
    projection='M4i',
    shorelines=True,
    water='lightblue',
    land='white',
    frame=True,
)


#### there is a bug here that wasn't here in jan, feb has many nan values, 
#### need to get rid of them because otherwise the string conversion to greyscale
#### wont work. would like to preferably remove the nan and its corresponding
#### lat long values, but that is proving difficult. cant turn it into a 0 because 
#### that is an actual greyscale value. need to actually remove it from the whole DF if it is nan


febcolor = []
for i in alldataDF['Mean Values Feb']:
    febcolor.append(str(i*255/10))

#need to define the coords in a new variable
coordscolorfeb = pd.DataFrame(list(zip(longdata,latdata,febcolor,meanvalsfeb)))
#had to clean up data set so that if it was nan or 0, i converted it to 0 
#and then removed it from the set
coordscolorfeb = coordscolorfeb.fillna(0)
coordscolorfeb = coordscolorfeb[(coordscolorfeb != 0).all(1)]
#ok so I had to change it from a list to a DF to remove nan and 0, can't call the dataframe 
#in the for loop so i need to change it back to a list smh
longdatafeb,latdatafeb = coordscolorfeb[0], coordscolorfeb[1]
febcolordata,febmeandata = coordscolorfeb[2],coordscolorfeb[3]
#zip them all together and then make them a list again 
cleaneddatafeb = list(zip(longdatafeb, latdatafeb, febcolordata))
#now I get to make the figure 
    
for clong,clat,col in cleaneddatafeb:  
    fig2.plot(
        x=clong,
        y=clat,
        style='c0.1i',
        color= col,
        pen='black',
        legend = 'blank'
    )

fig2.text(text = 'Feburary 2020', x = -90, y = 28 )
fig2.show()

#
#######
#march!!
fig3 = pygmt.Figure()

fig3.coast(
    region=[-115, -70, 25, 45],
    projection='M4i',
    shorelines=True,
    water='lightblue',
    land='white',
    frame=True,
)


#### there is a bug here that wasn't here in jan, feb has many nan values, 
#### need to get rid of them because otherwise the string conversion to greyscale
#### wont work. would like to preferably remove the nan and its corresponding
#### lat long values, but that is proving difficult. cant turn it into a 0 because 
#### that is an actual greyscale value. need to actually remove it from the whole DF if it is nan


marcolor = []
for i in alldataDF['Mean Values March']:
    marcolor.append(str(i*255/10))

#need to define the coords in a new variable
coordscolormar = pd.DataFrame(list(zip(longdata,latdata,marcolor,meanvalsmar)))
#had to clean up data set so that if it was nan or 0, i converted it to 0 
#and then removed it from the set
coordscolormar = coordscolormar.fillna(0)
coordscolormar = coordscolormar[(coordscolormar != 0).all(1)]
#ok so I had to change it from a list to a DF to remove nan and 0, can't call the dataframe 
#in the for loop so i need to change it back to a list smh
longdatamar,latdatamar = coordscolormar[0], coordscolormar[1]
marcolordata,marmeandata = coordscolormar[2],coordscolormar[3]
#zip them all together and then make them a list again 
cleaneddatamar = list(zip(longdatamar, latdatamar, marcolordata))
#now I get to make the figure 
    
for clong,clat,col in cleaneddatamar:  
    fig3.plot(
        x=clong,
        y=clat,
        style='c0.1i',
        color= col,
        pen='black',
        legend = 'blank'
    )

fig3.text(text = 'March 2020', x = -90, y = 28 )
fig3.show()

########
#april!!
fig4 = pygmt.Figure()

fig4.coast(
    region=[-115, -70, 25, 45],
    projection='M4i',
    shorelines=True,
    water='lightblue',
    land='white',
    frame=True,
)


#### there is a bug here that wasn't here in jan, feb has many nan values, 
#### need to get rid of them because otherwise the string conversion to greyscale
#### wont work. would like to preferably remove the nan and its corresponding
#### lat long values, but that is proving difficult. cant turn it into a 0 because 
#### that is an actual greyscale value. need to actually remove it from the whole DF if it is nan


aprcolor = []
for i in alldataDF['Mean Values April']:
    aprcolor.append(str(i*255/10))

#need to define the coords in a new variable
coordscolorapr = pd.DataFrame(list(zip(longdata,latdata,aprcolor,meanvalsapr)))
#had to clean up data set so that if it was nan or 0, i converted it to 0 
#and then removed it from the set
coordscolorapr = coordscolorapr.fillna(0)
coordscolorapr = coordscolorapr[(coordscolorapr != 0).all(1)]
#ok so I had to change it from a list to a DF to remove nan and 0, can't call the dataframe 
#in the for loop so i need to change it back to a list smh
longdataapr,latdataapr = coordscolorapr[0], coordscolorapr[1]
aprcolordata,aprmeandata = coordscolorapr[2],coordscolorapr[3]
#zip them all together and then make them a list again 
cleaneddataapr = list(zip(longdataapr, latdataapr, aprcolordata))
#now I get to make the figure 
    
for clong,clat,col in cleaneddataapr:  
    fig4.plot(
        x=clong,
        y=clat,
        style='c0.1i',
        color= col,
        pen='black',
    )
fig4.text(text = 'April 2020', x = -90, y = 28 )
fig4.show()
help(fig.plot)

fig.show(method='external')
fig2.show(method='external')
fig3.show(method='external')
fig4.show(method='external')






