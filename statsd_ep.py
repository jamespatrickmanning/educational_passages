# Routine to calculate realtime drifter statistics
# originally written by JiM in circa 2010
# modified to include miniboats by name in 2017
# modified to a) calculate stats on specifically miniboats in "drift_ep_all.csv" file and b) use Python 3 in Sep 2019
import sys
import calendar
import os
import numpy
#pydir='/net/home3/ocn/jmanning/py/mygit/modules/'
#sys.path.append(pydir)
from conversions import distance,ll2uv
import matplotlib.mlab as ml
import pandas as pd
import __future__
#import sets
def read_codes_names(id0):
  # get id,depth from /data5/jmanning/drift/codes.dat
  inputfile1="codes.dat"
  path1="/net/data5/jmanning/drift/"
  f1=open(path1+inputfile1,'r')
  name=''
  lab=''
  depth=999
  for line in f1:
    id=line.split()[1]
    dep=line.split()[2]
    if (int(id)==id0):
      if (len(line.split())>3):# and (float(dep)==0.1):
        depth=line.split()[2]
        name=line.split()[3]
        lab=line.split()[4]
        print(name,lab,depth)
      else:
        lab=''
        name=''
        depth=dep
  f1.close()
  '''try: # if it is not in "codes.dat", it should be in "codes_ap3.dat"
    name
  except NameError:'''
  if len(name)==0: # hopefully it is a AP3
    inputfile1="codes_ap3.dat"
    f1=open(path1+inputfile1,'r')
    for line in f1:
      esn=line.split()[0]
      if esn!="ESN": # case of the header line
        id=line.split()[2]
        dep=line.split()[3]
        if (int(id)==id0):
          #print esn,id,id0
          if (len(line.split())>3):# and (float(dep)==0.1):
            depth=line.split()[3]
            name=line.split()[4]
            lab=line.split()[5]
            #print name,lab,depth
          else:
            lab=''
            name=''
            depth=dep
  return name,lab,depth

def read_drift(filename):
  #d=ml.load(filename,comments='%')
  header_row=["deployment_ID", "drifter_ID", "month", "day", "hour", "sec", "frac_yr", "lon", "lat", "depth (m)", "temp"]
  d=pd.read_csv(filename,names=header_row)#,delimiter=r"\s+")
  d=d[d['deployment_ID']!='ID']# gets rid of all the extra header lines
  d=d.drop_duplicates()        # gets rid of repeats
  d['lat']=pd.to_numeric(d['lat'])# convert str to float
  d['lon']=pd.to_numeric(d['lon'])
  d['deployment_ID']=pd.to_numeric(d['deployment_ID'])
  
  #In this loading,we skip the first row,"jd" means yearday.
  id= d['deployment_ID'].values
  lat=d['lat'].values
  lon=d['lon'].values
  jd_matlab=d['frac_yr'].values
  y=[]
  jd=[]
  for i in range(len(jd_matlab)):
      jd.append(float(jd_matlab[i])+1)# JiM added "float" in Sep 2019
      y.append(0)
  return jd,lat,lon,id,y

# MAIN CODE
inpdir='/net/pubweb_html/drifter/'    
#[jd,lat,lon,id,y]=read_drift(inpdir+'drift_X.dat')
[jd,lat,lon,id,y]=read_drift(inpdir+'drift_ep_all.csv')
#Open "*.html" and write the title
f=open(inpdir+'statsd_ep.html','w');
f.write('<html><center><h1>Miniboat Statistics</h1>');
f.write('<center><h2>Ordered by "deployment_id"</h2>');
f.write('<h3><i>(Note: Speeds not accurate for those units ahsore.)</h3><table border="1">');
f.write('<b><tr><td align="left"><b>lab/school</td><td align="right"><b>PI/miniboat</td><td align="right"><b>depth<br>(m)</td><td align="right"><b>deployment_id</td><td><b>totaldist<br>(km)</td>'
        '<td><b>lineardist<br>(km)</td><td><b>#days</td>'
        '<td><b>#pts</td><td><b>east<br>(cm/s)</td><td><b>north<br>(cm/s)</td>'
        '<td><b>mean speed<br>(cm/s)</td></tr></b>');
#to get total totaldistance ,totaldays in loop
totaldistance=0
totaldays=0
#make the same ids together
totaldistance=0
totaldays=0
id_list=sorted(list(set(id)))
id_strattle_new_year=[] # keep track of the number of times one unit strattles the new year
for i in range(len(id_list)):
   
    lat_id=[]
    lon_id=[]
    jd_id=[]
    for m in range(len(lat)):
        if id[m]==id_list[i]:
            lat_id.append(lat[m])
            lon_id.append(lon[m])
            #jd_id.append(jd[m]+1)
            jd_id.append(jd[m])# made this change in Nov 2020 when I realized it was already done in read_csv function
    num_times_strattle_new_year=len(numpy.where(numpy.diff(jd_id)<-10)[0])# changed this from "<0" to "<10" to account for occassional data problems like occurred in LesterBells case
    if id_list[i]==169347601:
      print 'Lester_Bell strattles '+str(num_times_strattle_new_year)+' years!'
      print numpy.where(numpy.diff(jd_id)<0)[0]
      print jd_id[numpy.where(numpy.diff(jd_id)<0)[0][-1]]
            
    #if jd(yearday) is same, delete it

    index=list(range(len(jd_id)))#reverse the index of jd where "list" was added for Python 3
    index.reverse()
    
    for k in index:# if jd[i]==jd[i-1], delete the same values
            if jd_id[k]==jd_id[k-1]:
                 del jd_id[k]
                 del lat_id[k]
                 del lon_id[k]


    
   #get the pts,days
    pts=len(lat_id)-1
    
    #if jd_id: # only does the following when jd_id is non-empty
    if len(jd_id)!=0: # only does the following when jd_id is non-empty
      if num_times_strattle_new_year==0:
          days=jd_id[-1]-jd_id[0]
      elif num_times_strattle_new_year==1:
          if calendar.isleap(int(str(id[i])[0:2]))==False:
            days=jd_id[-1]+365-jd_id[0]
          else:      
            days=jd_id[-1]+366-jd_id[0]
      elif num_times_strattle_new_year==2:
          days=jd_id[-1]+365+(365-jd_id[0])
      elif num_times_strattle_new_year==3:# added this case when Lester Bell strattled the new year 3 times!!!
          days=jd_id[-1]+365+365+(365-jd_id[0])
      totaldays+=days
    
      # get name of school and teacher
      [PI,lab,depth]=read_codes_names(id_list[i]) # gets name, lab/school, and depth from codes.dat
  
      #get the totdist
      distkm,bear=[],[]
      for n in range(1,len(lat_id)):
        #d,b = dist(lat_id[n-1], lon_id[n-1], lat_id[n], lon_id[n])
        d,b = distance((lat_id[n-1], lon_id[n-1]), (lat_id[n], lon_id[n]))
        distkm.append(d)
        bear.append(b)
      totdist=sum(distkm)
      totaldistance+=totdist
      #get the s2end
      #s2end,bear2=dist(lat_id[0],lon_id[0],lat_id[-1],lon_id[-1])
      s2end,bear2=distance((lat_id[0],lon_id[0]),(lat_id[-1],lon_id[-1]))
      #get the u,v,spd
      u,v,spd,jdn = ll2uv(jd_id,lat_id,lon_id)
      # maybe we should be using a different time here 

      #get the meanu,meanv,meanspd
      meanu = numpy.mean(u)
      meanv = numpy.mean(v)
      meanspd = numpy.mean(spd)
    
      #write the data to *.html
      if id_list[i]==170320171:
         lab='Westbrook_North_Uist_Amadeu_Gaudancio_Dom_Fuas_Roupinho'#shorter name
      if depth!='0.1':
        f.write('<tr><td align="left">%s'%lab+'</td></b><b><td align="right">%s'%PI+'</td></b><b><td align="right">%s'%depth+'</td></b>'
               '<b><td align="right"> %10.0f'%int(id_list[i])+'</td></b><b><td align="right"> %7.1f'%totdist+'</td></b>'
               '<b><td align="right"> %7.1f'%s2end+'</td></b><b><td align="right"> %5.1f'%days+'</td></b><b><td align="right"> %7.0f'%pts+'</td></b>'
               '<b><td align="right"> %7.1f'%meanu+'</td></b><b><td align="right"> %7.1f'%meanv+'</td></b><b><td align="right">%7.1f'%meanspd+'</td></b>'
               '</tr>\n')
      else: # for the case of minboats, make the boat name bold
        f.write('<tr><td align="left">%s'%lab+'</td></b><b><td align="right"><b>%s'%PI+'</b></td></b><b><td align="right">%s'%depth+'</td></b>'
               '<b><td align="right"> %10.0f'%int(id_list[i])+'</td></b><b><td align="right"> %7.1f'%totdist+'</td></b>'
               '<b><td align="right"> %7.1f'%s2end+'</td></b><b><td align="right"> %5.1f'%days+'</td></b><b><td align="right"> %7.0f'%pts+'</td></b>'
               '<b><td align="right"> %7.1f'%meanu+'</td></b><b><td align="right"> %7.1f'%meanv+'</td></b><b><td align="right">%7.1f'%meanspd+'</td></b>'
               '</tr>\n')# JiM added int beofre id_list[i] in sep 2019


f.write('<tr><td align="left"><b> ''The totals''</b></td><td></td><td></td><td></td><td align="right"><b>%7.0f'%totaldistance+'</b></td>'
               '<td></td><td align="right"><b>%5.0f'%totaldays+'</b></td></tr>\n')           
f.close()

