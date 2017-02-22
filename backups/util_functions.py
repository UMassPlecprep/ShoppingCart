"""
These functions are all helper funcitons to the main server.py file.

server.py imports them as "util".
"""

cal_id="certl@umass.edu"
from auto_corrector import advancedGuessing

def formatTime(t,pad_zero=False): #Takes xx:yy or x:yy, pad_zero takes xx:yy
    """
    When passed a time, this function deals with zero-padding times.
    t is a string with the form [int]:[int]
    Based on "pad_zero", this function is used to...
    -pad_zero=True
        strip away any non-essential zeroes from the hour (human-friendly)
    -pad_zero=False
        Pad the hour/minute with zeroes if necessary

    ex: 
        formatTime( '8:00', pad_zero=True ) ====>  '08:00'
        formatTime( '08:00', pad_zero=False ) ====> '8:00'

    Reverse=True is generally used when a human will be reading the output (displayed on webpage)

    pad_zero=False is used for computation (legacy software)
"""
    colon_pos = t.find(':')
    hour = t[:colon_pos]
    if pad_zero:
        hour = str(int(hour))
        return hour + t[colon_pos:]

    minute = t[colon_pos + 1:]
    hour = padZero(hour)
    minute = padZero(minute)
    return hour + ':' + minute

def milTimeConv(time,meridian,to_mil=True):
    """
    Funciton used to convert 12-hour times to 24-hour times
        -time is a string of form [int]:[int]
        -meridian is either 'AM'/'PM'
        -to_mil denotes whether to convert to 12-hour (False) or 24-hour (True)
    The output is a list of length 2; the first item is the hour (string) and the second item is the minute (string)
    """
    time = formatTime(time)
    hour = int(time[:2])
    if to_mil:
        if meridian == 'PM' and hour < 12:
            hour = hour + 12
    else:
        if hour > 12:
            hour = hour - 12
    return [str(hour),time[3:5]]

def time_from_list(l):
    """
    Converts times in list form to string form
    Mainly used to convert the output of milTimeConv to a string
    """
    return formatTime(l[0]+':'+l[1])

def padZero(string):
    """
    Similar to formatTime except a single integer cast as a string is taken as the input.
    ex: padZero('9') ====> '09'
    """
    if len(string) < 2:
        string = '0' + string
    return string

"""
Extract suite

Collection of functions used to extract info from the request sent from the front-end
"""
def extractDemo(data):
    """
    Returns the demo requested
    """
    end = data.find('Physics')
    return data[:end]

def extractProf(data):
    """
    Returns the professor
    """
    begin = data.find(' name: ') + 7
    end = data.find(' code: ')
    prof = data[begin:end]
    prof = nameCorrection(prof.capitalize()).lower()
    print "Requested by:  ", prof
    return prof

def extractCode(data):
    """
    Returns whether Physics or Astronomy
    """
    begin = data.find(' code: ') + 7
    end = data.find(' date: ')
    return data[begin:end]

def extractRoom(prof,code):
    """
    Returns where the class meets
    """
    data = json.load(open('config/prof-schedule.json'))
    return data[prof][code]['room']

# Takes request (" date: xx-yy"), professor, and class (code)
# Outputs %Y-%m-%dT%H:%M:00-5:00
#         of: start and end
#         and throws the date in form %Y-%m-%d

def extractDate(data,prof,code):
    """
    Returns the date of the request, the starting time, and the ending time
    
    start and end are in %Y-%m-%dT%H:%M:%S format
    date is in %y-%m-%d format
    """
    begin = data.find(' date: ') + 7
    date = data[begin:].replace('/','-')
    date = date.replace(' ','').replace('\n','').replace('\t','')
    month = date[:2]
    day = date[-2:]
    month = padZero( month.replace('-','') )
    day = padZero( day.replace('-',''))
    now = datetime.datetime.now()
    year = now.year

    #Case: prof requesting demo for next year (year issue)
    if now.month > int(month):
        year += 1
    date = str(year)+'-'+month+'-'+day
    shour, sminute, ehour, eminute = extractTime(prof,code)
    start = googlizeDate(shour, sminute, date=date)
    end = googlizeDate(ehour, eminute, date=date)
    return start, end, date

# Takes professor and class
# Outputs tuple of starting/ending hours/mins
# e.g.: 08, 00, 09, 15 --> 08:00-09:15
def extractTime(prof, code):
    """
    Returns hours and minutes of a classes starting times as individual strings
    Pulled from config/prof-schedule.json
    """
    data = json.load(open('config/prof-schedule.json'))
    shour = data[prof][code]['start'][0]
    sminute = data[prof][code]['start'][1]
    ehour = data[prof][code]['end'][0]
    eminute = data[prof][code]['end'][1]
    return shour, sminute, ehour, eminute

"""
End extraction suite
"""

def nameCorrection(prof):
    """
    Returns corrected name
    """
    with open('config/names.txt') as f:
        list_of_people = [row.strip('\n') for row in f]
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
    """
    Returns googlizeDate but with only numbers (i.e. YYYYmmddTHHMMSSZ)
    HHMMSS is set to the last minute (i.e. 23:59:59) for a day
    """
    date = date[:-6].replace('-','').replace(':','')
    # Make it so that the cutoff point on the last day is 23:59:00
    return str(date[:8]) + 'T235900Z'

def datetimeDateConv(start,days):
    """
    
    """
    day_mappings = ['MO','TU','WE','TH','FR','SA','SU']
    year = start[:4]
    month = start[5:7]
    updated_date_day = int(start[8:10]) #The day part of %Y-%m-%d...
    time = start[10:]
    print "Month: ", month, "\nStart: ",start
    dateS = datetime.date(int(year), int(month), updated_date_day)
    if day_mappings[dateS.weekday()] in days: # If the class meets on day 1 of the semester
        return start
    else: # Otherwise, the start date will be the next day
        updated_date_day = updated_date_day + 1
        updated_date_day = padZero(str(updated_date_day)) # Make the day in xx format
        return year+'-'+month+'-'+updated_date_day+time

def googlizeDate(hour, minute, date=None, month=None, day=None, year=None):
    time = formatTime(hour+':'+minute)
    if date is not None:
        return date + 'T' + time + ':00-05:00'
    else:
        return googlizeDate(hour, minute, date=padZero(month) + '-' + padZero(day) + '-' + padZero(year))

