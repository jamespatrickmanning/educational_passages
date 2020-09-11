# routine to make individual csv files for each boat in "drift_ep_all.csv"
# JiM wrote in March 2019 on Cassie's request so she can point to individual's data on the EP websites
# JiM modified in Sep 2020 to look in "/newfish_html/drifter" directory
import pandas as pd
#df=pd.read_csv('/net/pubweb_html/drifter/drift_ep_all.csv') # makes a dataframe of all the data
df=pd.read_csv('/newfish_html/drifter/drift_ep_all.csv') # makes a dataframe of all the data
df=df[df.ID!='ID'] # gets rid of all header lines except the first
ids=df.ID.unique() # finds unique ids
for k in ids:
  df1=df[df.ID==k] # makes a dataframe for just this unit
  df1=df1.drop_duplicates()
  df1.to_csv('/newfish_html/drifter/drift_'+str(k).lstrip()+'.csv')# writes a file and strips white space from id with "lstrip()"

