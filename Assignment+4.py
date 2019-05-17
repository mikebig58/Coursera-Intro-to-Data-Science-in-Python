
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}

#import os
#for subdir, dirs, files in os.walk('./'):
#    for file in files:
#      print(file)


# In[3]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    #Load the text file and strip out the return characters at the end of each line
    lineList = [line.rstrip('\n') for line in open('university_towns.txt')]
    sub = '[edit]'
    utowns = pd.DataFrame(columns=['State','RegionName'])

    for line in lineList:
        # First lets find the state lines 
        if sub in line:
            #remove the [edit] string from the line
            state = line.split('[')[0]
            #now get the dictionary key(abbreviation) from the dictionary basis the value(state)
            #state = list(states.keys())[list(states.values()).index(state)]
        else:
            # Next lets get the region names
            region = line.split(' (')[0]
            # Append the state and RegionName into the university towns dataframe
            utowns = utowns.append({'State': state, 'RegionName': region}, ignore_index=True)
    return utowns

get_list_of_university_towns()


# In[4]:


def get_recession_start():
    recession_start = None
    cols = [4,6]
    gdp = pd.read_excel('gdplev.xls', header=6, usecols=cols)
    gdp.columns = ['Quarter', 'GDP2009']
    #Drop rows before 2000 Q1
    gdp = gdp.iloc[212:]
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    #A recession is defined as starting with two consecutive quarters of GDP decline
    #iterate through the rows of the dataframe
    for qtr in range(2, len(gdp)):
        #check to see if the next two quarters are in decline
        if (gdp.iloc[qtr-2][1] > gdp.iloc[qtr-1][1]) and (gdp.iloc[qtr-1][1] > gdp.iloc[qtr][1]):
            #when found return the quarter
            recession_start = gdp.iloc[qtr-1][0]

            return  recession_start

#get_recession_start()


# In[5]:


def get_recession_end():
    
    recession_start = get_recession_start()
    recession_end = None
    cols = [4,6]
    gdp = pd.read_excel('gdplev.xls', header=6, usecols=cols)
    gdp.columns = ['Quarter', 'GDP2009']
    #Drop rows before start of the recession
    recession_start_index = gdp[gdp['Quarter'] == recession_start].index.item()
    gdp = gdp.iloc[recession_start_index:]
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    #A recession is defined as ending with two consecutive quarters of GDP growth.
    #iterate through the rows of the dataframe
    for qtr in range(2, len(gdp)):
        if (gdp.iloc[qtr-2][1] < gdp.iloc[qtr-1][1]) and (gdp.iloc[qtr-1][1] < gdp.iloc[qtr][1]):
            recession_end = gdp.iloc[qtr][0]
            break

    return  recession_end

#get_recession_end() 


# In[6]:


def get_recession_bottom():
    recession_start = get_recession_start()
    recession_end = get_recession_end()
    cols = [4,6]
    gdp = pd.read_excel('gdplev.xls', header=6, usecols=cols)
    gdp.columns = ['Quarter', 'GDP2009']
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    recession_start_index = gdp[gdp['Quarter'] == recession_start].index.item()
    recession_end_index = gdp[gdp['Quarter'] == recession_end].index.item()
    #Drop rows before start and after the end of the recession
    gdp = gdp.iloc[recession_start_index:recession_end_index]
    #find the minimum GDP
    bottom_GDP = gdp['GDP2009'].min()
    bottom_quarter = gdp.loc[gdp['GDP2009'] == bottom_GDP]['Quarter'].min()
   
    return bottom_quarter
             
get_recession_bottom()


# In[20]:


def convert_housing_data_to_quarters():
#    '''Converts the housing data to quarters and returns it as mean 
#    values in a dataframe. This dataframe should be a dataframe with
#    columns for 2000q1 through 2016q3, and should have a multi-index
#    in the shape of ["State","RegionName"].
#
#    Note: Quarters are defined in the assignment description, they are
#    not arbitrary three month periods.
#    
#    The resulting dataframe should have 67 columns, and 10,730 rows.

#    '''
    #Load the dataframe
    homes = pd.read_csv('City_Zhvi_AllHomes.csv')
    #now get the dictionary key(state abbreviation) from the dictionary basis the value(state)
    homes['State'] = homes['State'].map(states)
    #set index to State, RegionName
    homes.set_index(["State","RegionName"], inplace=True)
    #keep only data for 2000q1 through 2016q3
    homes = homes.filter(regex='^20', axis=1)
    #Calculates the average per quarter
    homes = homes.groupby(pd.PeriodIndex(homes.columns, freq='q'), axis=1).mean()
    #Set the quarter names to lower case to match the recession functions output
    homes.columns = homes.columns.strftime('%Yq%q')

    return homes

convert_housing_data_to_quarters()


# In[52]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    #get the recession start quarter
    start = get_recession_start()
    #get the recession end quarter
    end = get_recession_end()
    #get the recession bottom quarter
    bottom = get_recession_bottom()
    
    #get the converted zillow housing data 
    homes = convert_housing_data_to_quarters()
    #keep only the quarters between the start and bottom
    homes = homes.loc[:,start: bottom]
    #calculate the ratio of hous price change between the start and bottom of the recession
    homes['ratio'] =(homes[start]-homes[bottom])/homes[start]
    
    #get the list of university towns
    utowns = get_list_of_university_towns()
    #set the index of university towns to State and RegionName
    utowns.set_index(["State","RegionName"], inplace=True)
    #create a new column 'utown' to indicate a university town and set it to true 
    utowns['utown'] = 'Yes'
    
    #meger the converted zillow housing data with the university towns
    combined_towns = res = pd.merge(homes,utowns,how="left",left_index=True,right_index=True)
    #set the 'utown' column to 'No' for the non-university towns
    combined_towns['utown'] = combined_towns['utown'].fillna('No')
    
    #create a separate dataframe of just university towns
    u_towns = combined_towns[combined_towns.utown == 'Yes']
    #create a separate dataframe of just non-university towns
    nu_towns = combined_towns[combined_towns.utown == 'No']
    
    #run the ttest comparing ratio of the university towns with the non-university towns
    stats,pvalue = ttest_ind(u_towns['ratio'], nu_towns['ratio'], nan_policy = 'omit')
    significant = pvalue < 0.01  
    
    #determine the market loss
    lower = stats < 0
    
    #determine if the university town or the non-university town has the lower mean price ratio
    better = ["non-university town", "university town"]
    
    return significant, pvalue, better[lower]

run_ttest()

