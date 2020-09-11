# routine to make individual csv sensor data files for each boat in "emolt_ap3_sensor_ep.csv"
# JiM wrote in April 2019 on Cassie's request so she can point to individual's data on the EP websites
# modeled after "files_by_id.py" which separates the track files
import pandas as pd
df=pd.read_csv('/net/pubweb_html/drifter/emolt_ap3_sensor_ep.csv') # makes a dataframe of all the data
ids=list(df.index.unique()) # finds unique ids
for k in ids:
  df1=df[df.index==k] # makes a dataframe for just this unit
  df1.to_csv('/net/pubweb_html/drifter/drift_'+str(k).lstrip()+'_sensor.csv')# writes a file and strips white space from id with "lstrip()"

