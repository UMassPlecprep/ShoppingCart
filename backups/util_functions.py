import datetime, json, os
from auto_corrector import advancedGuessing

def formatTime(t,reverse=False): #Takes xx:yy or x:yy, reverse takes xx:yy
    if reverse:
        hour = str(int(t[:t.find(':')]))
        return hour+':'+t[2:]
    hour = t[:t.find(':')]
    minute = t[t.find(':')+1:]
    if len(hour) == 1:
        hour = '0' + hour
    if len(minute) == 1:
        minute = '0' + minute

    return hour + ':' + minute

# Takes xx:yy PM/AM
# Outputs [xx,yy]
def milTimeConv(time,meridian,to_mil=True):
    time = formatTime(time)
    hour = time[:2]
    if to_mil:
        if meridian == 'PM' and int(hour) < 12:
            hour = str(int(hour) +12)
    else: # Only called when converting to human-friendly format
        hour = int(hour)
        if hour > 12:
            hour = str(hour - 12)
    return [str(hour),time[3:5]]

def time_from_list(l):
    return formatTime(l[0]+':'+l[1])

#Takes hour string ('1','2',etc.)
# Outputs '0'+hour (i.e.:'01','02',etc.)
def fixHourString(hour):
    if int(hour) < 10:
        hour = '0' + str(hour)
    return hour

def extractDemo(data):
    end = data.find('Physics') - 3
    return data[:end]

def extractProf(data):
    begin = data.find(' name: ') + 7
    end = data.find(' code: ')
    prof = data[begin:end]
    prof = nameCorrection(prof.capitalize()).lower()
    return prof

def extractCode(data):
    begin = data.find(' code: ') + 7
    end = data.find(' date: ')
    return data[begin:end]

def extractRoom(prof,code):
    data = json.load(open('config/prof-schedule.json'))
    return data[prof][code]['room']

# Takes request (" date: xx-yy"), professor, and class (code)
# Outputs %Y-%m-%dT%H:%M:00-5:00
#         of: start and end
#         and throws the date in form %Y-%m-%d
def extractDate(data,prof,code):
    begin = data.find(' date: ') + 7
    date = data[begin:].replace('/','-')
    date = date.replace(' ','').replace('\n','').replace('\t','')
    if len(date) == 5:
        month = date[:2]
        day = date[-2:]
    # format is now 08-22
    now = datetime.datetime.now()
    year = now.year
    #Case: prof requesting demo for next year (year issue)
    if now.month > int(month):
        year += 1
    date = str(year)+'-'+month+'-'+day
    shour, sminute, ehour, eminute = extractTime(prof,code)
    start = date+"T"+shour+':'+sminute+':00-05:00'
    end =   date+"T"+ehour+':'+eminute+':00-05:00'
    return start, end, date

# Takes professor and class
# Outputs tuple of starting/ending hours/mins
# e.g.: 08, 00, 09, 15 --> 08:00-09:15
def extractTime(prof ,code):
    data = json.load(open('config/prof-schedule.json'))
    shour = data[prof][code]['start'][0]
    sminute = data[prof][code]['start'][1]
    ehour = data[prof][code]['end'][0]
    eminute = data[prof][code]['end'][1]
    return shour, sminute, ehour, eminute

def nameCorrection(prof):
    with open('config/professors.txt') as f:
        list_of_people = [row[:-1] for row in f]
    return advancedGuessing(list_of_people, prof)

# Converts days to HUMAN format (i.e.: MO --> M, TU --> T, etc)
# MO/TU/WE/etc. format needed for Google Cal's 'BYDAY' recurrence
def clean_days(days):
    day_mappings = {'MO':'M','TU':"T",'WE':'W','TH':'Th','FR':'F'}
    x = ['MO','TU','WE','TH','FR']
    days_sort = sorted(days,key=x.index)
    cleaned = ""
    for day in days_sort[:-1]:
        cleaned += day_mappings[str(day)] + "-"
    cleaned += day_mappings[str(days_sort[-1])]
    return cleaned

#When passed %Y-%m-%dT%H:%M:%S-05:00
# Convert to YYYYmmddTHHMMSSZ (Google's second date format)
def date_only_numbers(date):
    #date = date[:-6]
    #date = date.replace('-','').replace(':','') + 'Z'
    #temp = int(date[4:6]) + 1
    #date = date[:4] + str(temp) + date[6:]
    #return str(date)
    date = date[:-6].replace('-','').replace(':','')
    # Make it so that the cutoff point on the last day is 23:59:00
    return str(date[:8]) + 'T235900Z'

def datetimeDateConv(start,days):
    day_mappings = ['MO','TU','WE','TH','FR','SA','SU']
    year = start[:4]
    month = start[5:7]
    updated_date_day = int(start[8:10]) #The day part of %Y-%m-%d...
    time = start[10:]
    dateS = datetime.date(int(year), int(month), updated_date_day)
    if day_mappings[dateS.weekday()] in days: # If the class meets on day 1
        return start
    else: # Otherwise, the start date will be the next day
        updated_date_day = updated_date_day + 1
        updated_date_day = fixHourString(updated_date_day) # Make the day in xx format
        return year+'-'+month+'-'+updated_date_day+time
