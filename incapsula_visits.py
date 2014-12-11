import pycurl
import cStringIO
import json
import base64
import sys
import re
import time
from pprint import pprint
from calendar import timegm
import datetime
from datetime import date, timedelta, tzinfo, datetime, time
 


def get_curl(api,params_string):
        buf = cStringIO.StringIO()
        api_id="ID" #base64 encoded api_id
        api_key="KEY" #base64 encoded api_key
        url="https://my.incapsula.com"

        curl = pycurl.Curl()
        curl.setopt(pycurl.URL,"%s/%s" % (url,api))
        if not params_string:
                curl.setopt(pycurl.POSTFIELDS, "api_id=%s&api_key=%s" % (api_id.decode('base64'),api_key.decode('base64')) )
        else:
                #print "api_id=%s&api_key=%s&%s" % (api_id.decode('base64'),api_key.decode('base64'),params_string) #debug
                curl.setopt(pycurl.POSTFIELDS, "api_id=%s&api_key=%s&%s" % (api_id.decode('base64'),api_key.decode('base64'),params_string) )
        curl.setopt(pycurl.WRITEFUNCTION, buf.write)
        curl.perform()
        json_result = buf.getvalue()
        #print json_result #debug
        return json.loads(json_result)


def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6 - (10 * 60 * 60)


def main():
        site_id_api="api/prov/v1/sites/list"
        domain_name_api="api/prov/v1/sites/status"
        visits_api="api/visits/v1"

        # get yesterday and today in epoch unix timestamp and add millisconds to it
        yesterdayMidnight =  "%s" % ((str( totimestamp(datetime.combine((date.today() - timedelta(days=1)), time.min)) ))).split('.')[0] + "000"
        todayMidnight = "%s" % ((str( totimestamp(datetime.combine(date.today(), time.min)) ))) .split('.')[0] + "000"

        #yesterdayMidnight =  "%s" % ((str( totimestamp(datetime.combine((date.today() - timedelta(days=2)), time.min)) ))).split('.')[0] + "000" # day before yesterday
        #todayMidnight = "%s" % ((str( totimestamp(datetime.combine((date.today() - timedelta(days=1)), time.min)) ))) .split('.')[0] + "000" # day before yesterday

        data = get_curl(site_id_api , "")
        #print json.dumps(data, indent=4, separators=(',', ': ')) #debug
        sites_num=len(data['sites'])
        site_id_array = [None] * sites_num

        for x in range(0,sites_num):
            site_id_array[x] = data['sites'][x]['site_id']

        page_size=100 #max the api will return :'(


        site_dict={} 
        #collect domain name from site_id numbers
        for site_id_num in site_id_array:
            data=get_curl(domain_name_api, "site_id=%s" % site_id_num)
            #print json.dumps(data, indent=4, separators=(',', ': ')) #debug
            site_dict[site_id_num]=data['domain']

        #get stats for each site

        for key in site_dict:
            page_num=0
            visit_num_total = 0
            while True:
                site=key
                data=get_curl( visits_api, "site_id=%s&time_range=custom&start=%s&end=%s&page_size=%s&page_num=%s&security=&country=&ip=&visit_id=&list_live_visits=" % (key, yesterdayMidnight, todayMidnight, page_size, page_num))
                if (len(data["visits"]) == 0):
                    break
                page_num= page_num + 1
                    
                visits_num=len(data['visits'])
                for visit in range(0, visits_num):
                    visit_num_total = visit_num_total + 1
                    
                    #visits = json.dumps(data["visits"][visit], sort_keys=True, indent=1, separators=(',', ': '))
                    visits = json.dumps(data["visits"][visit], sort_keys=True, separators=(',', ': '))
                    #visits = ""
                    json_string="{\"_time_range\":\"%s\",\"site\":\"%s\",\"site_id\":\"%s\",\"visit_num\":\"%s\",\"visit\":\"%s\"}" % ( yesterdayMidnight + ":" + todayMidnight ,site_dict[site],site, visit_num_total, visits)
                    print json_string

if __name__ == '__main__':
    main()

