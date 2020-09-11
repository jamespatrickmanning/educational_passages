# -*- coding: utf-8 -*-
"""
routine to plot time series in, for example, "emolt_ap3_sensor_ep.dat" 
where this is the temperature collected on the RockStar, for example

Created on 22 August 2018
@author: JiM.
Modified on 26 April 2019 to handle case of Ashley Hall 
Modified on 12 June 2019 to include functions like "c2f" with the code
Modified on 23 July 2019 to read boatName as input argument
Still does not run in crontab for whatever reason... Is it permission related?



"""
import csv
import sys
#from utilities import lat2str, lon2str
from datetime import *
from matplotlib.dates import date2num,num2date
from matplotlib import pylab as plt
import numpy as np 
#from conversions import c2f
import pandas as pd

#hardcode######################################################################
path1='/net/data5/jmanning/drift/'
filedirection='/net/pubweb_html/drifter/' # directory to find input file
#filedirection='/net/webserver/htdocs/drifter/' # directory to find input file
infile='emolt_ap3_sensor_ep.dat'
#boatName='Spirit_of_Ashley_Hall'#'SV_Jamestown' #'Ginger_Judge' etc
boatName=sys.argv[1]
print boatName
schoolName='' #'Endicott_College'
if boatName=='Spirit_of_Ashley_Hall':
  start_time=datetime(2019,4,21,11,0,0)
elif boatName=='The_Perry':
  start_time=datetime(2019,6,27,0,30,0)
elif boatName=='Maverick_Jr':
  start_time=datetime(2019,7,18,21,0,0)
minilog_file='' #'/net/data5/jmanning/minilog/dat/SP01m56340101.dat' # for comparison with sensor packages (leave as '' if none)
################################################################################
def c2f(*c):
    """
    convert Celsius to Fahrenheit
    accepts multiple values
    """
    if not c:
        c = input ('Enter Celsius value:')
        f = 1.8 * c + 32
        return f
    else:
        f = [(i * 1.8 + 32) for i in c]
        return f

def read_codes_names(esn0,id0):
  inputfile1="codes_ap3.dat"
  f1=open('/net/data5/jmanning/drift/'+inputfile1,'r')# changed from "path1" to direct listing of directory
  for line in f1:
      esn=line.split()[0]
      if esn!="ESN": # case of the header line
        #print esn,esn0,id,id0
        id=line.split()[2]
        dep=line.split()[3]
        if (esn==esn0) and (id==id0):
          if (len(line.split())>3):# and (float(dep)==0.1):
            depth=line.split()[3]
            name=line.split()[4]
            lab=line.split()[5]
            #print name,lab,depth
          else:
            lab=''
            name=''
            depth=dep
  try: # 
     name
  except:
     name=''
     lab=''
     depth=999
  return name,lab,depth

#MAIN PROGRAM
fig=plt.figure()
ax=fig.add_subplot(111)

if len(minilog_file)>0: # if so then plot minilog temp
  variables=['Site','sn','cd','Date','yd','Temp','salt','Depth']
  df=pd.read_csv(minilog_file,names=variables)
  df['datet']=pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S.%f')
  #ax=df.plot(x='datet',y='Temp',color='r')
  ax.plot(df['datet'],df['Temp'],color='r',label='VEMCO (Minilog)')


ireader = csv.reader(open(filedirection + infile, "r"))

#raw data loaded
idss,esn,yeardays_all,lat_all,lon_all,day_all,mth_all,sst_all,airt_all,ph_all,o2_all=[],[],[],[],[],[],[],[],[],[],[]
# if the first line is comment line, skip
for line in (x for x in ireader if x[0][0] !='%'):
    #print line
    idss.append(line[0].split()[0])
    esn.append(line[0].split()[1])
    yeardays_all.append(line[0].split()[6])
    lat_all.append(line[0].split()[8])
    lon_all.append(line[0].split()[7])
    day_all.append(line[0].split()[3])
    mth_all.append(line[0].split()[2])
    if boatName=='Ginger_Judge':
      sst_all.append(line[0].split()[11])
      ph_all.append(line[0].split()[12])
      o2_all.append(line[0].split()[13])
    else:
      #if (boatName=='RockStar') or (boatName=='USF') or (boatName=='SV_Jamestown') or (boatName=='Spirit_of_Ashley_Hall') or (boatName=='The_Perry') or (boatName=='Maverick_Jr') :
      sst_all.append(line[0].split()[11])
      airt_all.append(line[0].split()[14])


# convert string to float
yeardays_all=[float(i)+1 for i in yeardays_all]# in python num2date(), less one day than matlab, so add 1 here
lat_all=[float(i) for i in lat_all]
lon_all=[float(i) for i in lon_all]

ids=list(set(idss))# unique deployment ids

for k in range(len(ids)):
  idesn=np.where(np.array(idss)==ids[k])[0]
  esnthis=esn[idesn[0]]
  info=read_codes_names(esnthis,ids[k])
  if info[0]==boatName:
    year=int('20'+ids[k][0:2])
    lat,lon,time,yeardays,depth,temp,sst,airt,ph,o2=[],[],[],[],[],[],[],[],[],[]
    for i in range(len(idss)):
        if idss[i]==ids[k]:
            lat.append(lat_all[i])
            lon.append(lon_all[i])
            yeardays.append(yeardays_all[i])            
            if len(yeardays)>1:            
              if yeardays[-1]<200 and yeardays[-2]>350: # triggers a new year
                #print 'new year triggered'
                #print yeardays[-1],yeardays[-1]
                year=year+1
            if (int(mth_all[i])==2) and (int(day_all[i])==29): # trouble with no accepting leap year date in Feb 2016
               day_all[i]=28
            time0=num2date(yeardays_all[i]).replace(year=year).replace(month=int(mth_all[i])).replace(day=int(day_all[i]))
            time.append(time0.replace(tzinfo=None))
            sst.append(c2f(float(sst_all[i]))[0])
            airt.append(c2f(float(airt_all[i]))[0])
    if len(sst)>0:
      df2=pd.DataFrame([time,airt,sst]).transpose()  
      df2=df2[df2[0]<datetime.now()] # this removes bogus dates in the future
      df2=df2[df2[0]>start_time]# where "start_time" is in the hardcode
      ax.plot(df2[0],df2[1],'-',color='b',linewidth=1,label='airt')
      ax.plot(df2[0],df2[2],color='r',linewidth=2,label='sst')
      ax.set_title(info[0])
      ax.set_ylabel('degF')
      ax.legend(loc='best')
      fig.autofmt_xdate()
      '''
      mint=float(min(sst))
      maxt=float(max(sst))
      ax2=ax1.twinx()
      ax2.set_ylabel('degF')
      ax2.set_ylim(mint*1.8+32,maxt*1.8+32)
      '''
      plt.savefig(filedirection+info[0]+'_time_series_plot.png')
      #plt.show()
