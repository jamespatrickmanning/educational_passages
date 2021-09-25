# -*- coding: utf-8 -*-
"""
Created on 12 Oct 2016 
Accesses files in backup directory and looks for sensor data
@author: JiM using Huanxin's previous "getap3.py" routine
Modified 31 May 2018 to rid non-numeric characters from USF conductivity
Modified 24 Sep 2018 to more easily add sensor packages
Modified 27 Dec 2018 to add Monmouth Academy boat
Modified 26 Feb 2019 to upgrade a few boats to 2019 IDs
"""
from matplotlib.dates import date2num
import time
import os
import sys
import subprocess
from dateutil import parser
import glob
import json
import datetime
import numpy as np
import re
from datetime import *
import pytz

## HARDCODES  ###
#school=[                ,                 ,                 ,'Ashley_Hall','Monmouth_Academy','Catholic',        'JD',          'Maverick',        'The_Perry','SV_Titantanic']
esnep=['300234065111640','300234065610530','300234065617710','300234065610430','300234065714260','300234065803940','300234065413020','300234065517700','300234065614750','300234065313290','300234065614730','300234063371590']
id_idn1ep=[193410683,185421251,182410681,193320801,203400681,193350711,192410681,193401255,193331211,190351433,190430701,199410701] # upgraded some of these to 2019 on 26 Feb 2019 and 2020 in Mar 2020
os.chdir('/home/jmanning/py/')
files=sorted(glob.glob('backup/*.json'))
path1='/net/data5/jmanning/drift/'
f_output_sensor=open('/net/pubweb_html/drifter/emolt_ap3_sensor_usf.dat','w') # special case with extra sensors
f_output_sensor2=open('/net/pubweb_html/drifter/emolt_ap3_sensor_ep.dat','w') 
f_output_sensor2_csv=open('/net/pubweb_html/drifter/emolt_ap3_sensor_ep.csv','w')
f_output_sensor2_csv.write('id,esn,mth,day,hr_gmt,min,yearday,lon,lat,depth,mean_air_temp,min_airt,max_airt,mean_sst,min_sst,max_sst,year\n')
###################

################################################################################

def read_codes_names(esn0,id0):
  # given esn and deployment_id, returns name, lab, and depth
  inputfile1="codes_ap3.dat"
  f1=open(path1+inputfile1,'r')
  for line in f1:
      esn=line.split()[0]
      if esn!="ESN": # case of the header line
        id=line.split()[2]
        #print esn,esn0,id,id0
        depth=line.split()[3]
        if (esn==esn0) and (id==id0):
            name=line.split()[4]
            lab=line.split()[5]
            st=parser.parse(line.split()[8])# start time
            et=parser.parse(line.split()[9])# end time
  try: # 
     name
  except:
     name=''
     lab=''
     depth=999
     st=datetime(2010,1,1,0,0,0)
     et=datetime(2030,1,1,0,0,0)
  return name,lab,depth,st,et

# MAIN PROGRAM STARTS HERE ##########
esn,date,lat,lon,battery,data_send,meandepth,rangedepth,timelen,meantemp,sdeviatemp=[],[],[],[],[],[],[],[],[],[],[],
c=0
date_all=[];addfiles=[]
for i in files:
    #try:
    if (i!='backup/20181108.000124.json') and (i!='backup/20190224.000040.json') and (i!='backup/20190920*.json'): # added 20190920*.json on 10 March 2020
      with open(i) as data_file:  # LOOP THROUGH ALL THE FILES NOW THAT THEY HAVE ALREADY BEEN PUT THERE BY AN EARLIER PROGRAM LIKE GETAP3.PY  
                       data = json.load(data_file)
                       addfiles.append(i)
                       esn=data['momentForward'][0]['Device']['esn']

                       # NOTE THAT THE PROCESSING DEPENDS ON WHAT SENSORS ARE ADDED AND HOW THEY ARE SENT TO THE SATELLITE
                       if (esn=='300234063371599'):#change last number to "0" to get rockstar original but I changed this to be part of the standard EP in Sep 2019
                          id_idn1=160410701
                          depth_idn1=0.1
                          try:
                            print data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex']
                            ph_ind=2
                          except:
                            ph_ind=1
                          if len(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'])>35:
                            if (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21]!='000') and (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21]!=''):        
                              meanairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21])/10.-30.
                              minairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][21:24])/10.-30.
                              maxairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][24:27])/10.-30.
                              meanseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][27:30])/10.-30.
                              minseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][30:33])/10.-30.
                              maxseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][33:37])/10.-30.
                              try:
                                 lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lat'] #
                                 dd=parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date'])
                                 yr1=dd.year
                                 mth1=dd.month
                                 day1=dd.day
                                 hr1=dd.hour
                                 mn1=dd.minute
                                 yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))
                                 lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lon']
                                 f_output_sensor.write(str(id_idn1).rjust(10)+" "+str(esn[-4:]).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
                                   str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                                 f_output_sensor.write(("%10.7f") %(yd1))
                                 f_output_sensor.write(" "+("%10.5f") %(lon)+' '+("%10.5f") %(lat)+' '+str(float(depth_idn1)).rjust(4)+ " "
                                    +str(np.nan))
                                 f_output_sensor.write(" "+str(meanairtemp).rjust(10)+' '+str(minairtemp).rjust(10)+' '+str(maxairtemp).rjust(10)+  " " +("%6.2f") %(meanseatemp)+ " "
                                   +("%6.2f") %(minseatemp)+("%6.2f") %(maxseatemp)+("%6.0f") %(yr1)+'\n')
                              except:
                                 print 'no PointLoc'
                       elif (esn=='300234063378570'):#for the case of USF
                          id_idn1=192270801 #JiM changed this on 14 Feb 2019
                          #id_idn1=181270821
                          depth_idn1=0.1
                          try:
                            print data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex']
                            ph_ind=2
                          except:
                            ph_ind=1
                          if len(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'])>35:
                            if (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21]!='000') and (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21]!='00a') and (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21]!=''):        
                              try:
                                 meanairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21])/10.-30.
                                 minairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][21:24])/10.-30.
                                 maxairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][24:27])/10.-30.
                                 meanseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][27:30])/10.-30.
                                 minseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][30:33])/10.-30.
                                 maxseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][33:36])/10.-30.
                                 cond=float(re.sub("[^0-9]", "",data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][36:40]))# removes non-numeric characters
                                 #cond= float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][36:40])
                                 lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lat'] #
                                 dd=parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date'])
                                 yr1=dd.year
                                 mth1=dd.month
                                 day1=dd.day
                                 hr1=dd.hour
                                 mn1=dd.minute
                                 yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))
                                 lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lon']
                                 f_output_sensor.write(str(id_idn1).rjust(10)+" "+str(esn[-4:]).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
                                   str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                                 f_output_sensor.write(("%10.7f") %(yd1))
                                 f_output_sensor.write(" "+("%10.5f") %(lon)+' '+("%10.5f") %(lat)+' '+str(float(depth_idn1)).rjust(4)+ " "
                                    +str(np.nan))
                                 f_output_sensor.write(" "+str(meanairtemp).rjust(10)+' '+str(minairtemp).rjust(10)+' '+str(maxairtemp).rjust(10)+  " " +("%6.1f") %(meanseatemp)+ " "
                                   +("%6.1f") %(minseatemp)+" "+("%6.1f") %(maxseatemp)+" "+("%6.0f") %(cond)+("%6.0f") %(yr1)+'\n')
                              except:
                                 print 'no PointLoc or bad sensor data where the characters can not be converted to float'
                       elif (esn=='300234011858209'):#change last number to "0" to get ginger
                          id_idn1=172400701
                          depth_idn1=0.1
                          if len(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'])>18:
                            if (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][18:21]!='000') and (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][18:21]!='dea') and (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][18:21]!='bee') and (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][18:19]!='d'):
                              #print data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex']
                              #sens_data=str(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'])
                              airt=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][18:22])/100.
                              ph=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][22:26])/100.
                              o2=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][26:30])/100.
                              #meanseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][27:30])/10.-30.
                              #minseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][30:33])/10.-30.
                              #maxseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'][33:37])/10.-30.
                              try:
                                 dd=parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date'])
                                 yr1=dd.year
                                 mth1=dd.month
                                 day1=dd.day
                                 hr1=dd.hour
                                 mn1=dd.minute
                                 yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))
                                 if yd1>51.5: # the yearday Ginger hit the water
                                   lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lat'] #
                                   lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lon']
                                   f_output_sensor.write(str(id_idn1).rjust(10)+" "+str(esn[-4:]).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
                                     str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                                   f_output_sensor.write(("%10.7f") %(yd1))
                                   f_output_sensor.write(" "+("%10.5f") %(lon)+' '+("%10.5f") %(lat)+' '+str(float(depth_idn1)).rjust(4)+ " "
                                    +str(np.nan))
                                   f_output_sensor.write(("%6.2f") %(airt)+ " " +("%6.2f") %(ph)+("%6.2f") %(o2)+("%6.0f") %(yr1)+'\n')
                              except:
                                 print 'no PointLoc'
                       elif (esn=='300234063373519'):#robby change last number to "0" to get Robby's
                              id_idn1=174400711
                              depth_idn1=0.1
                              sens_data=str(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex'])
                              print sens_data
                              try:
                                 dd=parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date'])
                                 yr1=dd.year
                                 mth1=dd.month
                                 day1=dd.day
                                 hr1=dd.hour
                                 mn1=dd.minute
                                 yd1=date2num(datetime.datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime.datetime(yr1,1,1,0,0))
                                 print yd1
                                 if (yd1>51.5) & (yd1<242.0): # the yearday Robby hit the water
                                   lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lat'] #
                                   lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][4]['PointLoc']['Lon']
                                   f_output_sensor.write(str(id_idn1).rjust(10)+" "+str(esn[-4:]).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
                                     str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                                   f_output_sensor.write(("%10.7f") %(yd1))
                                   f_output_sensor.write(" "+("%10.5f") %(lon)+' '+("%10.5f") %(lat)+' '+str(float(depth_idn1)).rjust(4))
                                   # +str(np.nan))
                                   f_output_sensor.write(sens_data+' 2017\n')
                                   #f_output_sensor.write(("%6.2f") %(airt)+ " " +("%6.2f") %(ph)+("%6.2f") %(o2)+("%6.0f") %(yr1)+'\n'+' 2017')
                              except:
                                 print 'no PointLoc'
                       else:
                         # this is the most common case of EP sensor packages
                         for k in range(len(esnep)): # loop through all the standard Ep sensor packages
                            if esn==esnep[k]:
                              try:
                                hex=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][2]['PointHex']['hex']
                                ph_ind=2 # this "point hex index" apparently varies with transmitter
                              except:
                                if (esn=='300234065617710') or (esn=='300234065413020'): # Jamestown
                                  ph_ind=2
                                else:
                                  ph_ind=1
                              try: # added this try except on 8 Aug 2019 when AL changed the format on some transmitters
                                hex=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex']
                              except:
                                ph_ind=3
                                hex=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex']
                              if len(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'])>35:
                                if (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21]!='000') and (data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][18:21]!=''): # checks for bad data       
                                  try:
                                    meanairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][-18:-15])/10.-30.
                                    minairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][-15:-12])/10.-30.
                                    maxairtemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][-12:-9])/10.-30.
                                    meanseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][-9:-6])/10.-30.
                                    minseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][-6:-3])/10.-30.
                                    maxseatemp=float(data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][ph_ind]['PointHex']['hex'][-3:])/10.-30.
                                    try:
                                      lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][5]['PointLoc']['Lat'] #
                                    except:
                                      lat=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][6]['PointLoc']['Lat'] # added this option 8 Aug 2019
                                    dd=parser.parse(data['momentForward'][0]['Device']['moments'][0]['Moment']['date'])
                                    [boatName,schoolName,depth,st,et]=read_codes_names(esn[-6:],str(id_idn1ep[k]))                                   
                                    if dd>st.replace(tzinfo=pytz.UTC): # only output to file when after deployment date
                                      yr1=dd.year
                                      mth1=dd.month
                                      day1=dd.day
                                      hr1=dd.hour
                                      mn1=dd.minute
                                      yd1=date2num(datetime(yr1,mth1,day1,hr1,mn1))-date2num(datetime(yr1,1,1,0,0))
                                      try:
                                        lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][5]['PointLoc']['Lon']
                                      except:
                                        lon=data['momentForward'][0]['Device']['moments'][0]['Moment']['points'][6]['PointLoc']['Lon']
                                      f_output_sensor2.write(str(id_idn1ep[k]).rjust(10)+" "+str(esn[-6:]).rjust(7)+ " "+str(mth1).rjust(2)+ " " +
                                       str(day1).rjust(2)+" " +str(hr1).rjust(3)+ " " +str(mn1).rjust(3)+ " " )
                                      f_output_sensor2.write(("%10.7f") %(yd1))
                                      f_output_sensor2.write(" "+("%10.5f") %(lon)+' '+("%10.5f") %(lat)+' '+str(float(depth_idn1)).rjust(4)+ " "
                                       +str(np.nan))
                                      f_output_sensor2.write(" "+str(meanairtemp).rjust(5)+' '+str(minairtemp).rjust(5)+' '+str(maxairtemp).rjust(5)+'   '+
                                       ("%7.1f") %(meanseatemp)+("%7.1f") %(minseatemp)+("%7.1f") %(maxseatemp)+("%6.0f") %(yr1)+'\n')

                                      f_output_sensor2_csv.write(str(id_idn1ep[k]).rjust(10)+","+str(esn[-6:]).rjust(7)+ ","+str(mth1).rjust(2)+ "," +
                                       str(day1).rjust(2)+"," +str(hr1).rjust(3)+ "," +str(mn1).rjust(3)+ "," )
                                      f_output_sensor2_csv.write(("%10.7f") %(yd1))
                                      f_output_sensor2_csv.write(","+("%10.5f") %(lon)+','+("%10.5f") %(lat)+','+str(float(depth_idn1)).rjust(4)+ ","
                                       +str(np.nan))
                                      f_output_sensor2_csv.write(","+str(meanairtemp).rjust(5)+','+str(minairtemp).rjust(5)+','+str(maxairtemp).rjust(5)+','+
                                       ("%7.1f") %(meanseatemp)+(",%7.1f") %(minseatemp)+(",%7.1f") %(maxseatemp)+(",%6.0f") %(yr1)+'\n')
                                    
                                  except:
                                    print 'no PointLoc'                       

f_output_sensor.close()
f_output_sensor2.close()
f_output_sensor2_csv.close()
#pipe50= subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/home/jmanning/py/files_by_id_sensors.py'])    # added this Apr 16, 2019
#pipe5= subprocess.Popen(['/home/jmanning/anaconda2/bin/python','/net/home3/ocn/jmanning/py/plot_sensor_time_series.py'])    # added this May 21, 2019  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
