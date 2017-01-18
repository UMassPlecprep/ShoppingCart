from flask import Flask,request,redirect, json, render_template, url_for
import os, sys, datetime
import util_functions as util
from googleEvent import addEvent, createSchedule

# Constants
app = Flask(__name__)
baseURL = '/home/ubuntu/plecprepShoppingCart/'
days = ['MO','TU','WE','TH','FR']
config = json.load(open('config/config.json'))
rooms = config['rooms']
classes = config['classes']
times = config['times']

# Intercept incoming request
@app.route('/',methods=['GET','POST'])
def shopping_cart():
    data = request.data
    if data.find('Physics') >= 0:
        demo = util.extractDemo(data)
        prof = util.extractProf(data)
        code = util.extractCode(data)
        start, end, date = util.extractDate(data,prof,code)
        room = util.extractRoom(prof,code)
    print ("Demo:  " + demo)
    print ("Name:  " + prof)
    print ("Date:  " + date)
    print ("Code:  " + code)
    print ("Start:  "+ start)
    print ("End:  "  + end)
    print ("\n\n\n\n\n")
    #data_handler(demo, prof, room+'  '+code,code, start, end, date)
    return 'OK'

def data_handler(demo, prof, room, code, start, end,date):
    # Setup path variables
    pathToFile = baseURL + 'demorequests/' + prof + '/' + date + '.txt'
    demos = ""
    # If professor's directory doesn't exist, make it
    # Needed else python IOError thrown
    if not os.path.exists('demorequests/' + prof):
        os.system('mkdir demorequests/' + prof)
    # Open the [date].txt file and record demo
    with open(pathToFile,'a+') as f:
        f.write(demo + '\n')
    with open(pathToFile) as f:
        for row in f:
            demos += row.replace('\n',', ')
    isAstroClass = code[0] == 'A'
    addEvent(prof.capitalize(),room,date,demos,start,end,isAstroClass)
    return

@app.route('/updateProfList',methods=['GET','POST'])
def updateProfList():
    global times
    with open('config/professors.txt') as f:
        profs = [prof[:-1] for prof in f]
    profs.sort()
    # Format classes for user in format:
    # [class] [Prof] [start]-[end] [room]
    active_classes = json.load(open('config/prof-schedule.json'))
    for prof in active_classes:
        for c in active_classes[prof]:
            temp = active_classes[prof][c]
            start = temp['start'][0] + ':' + temp['start'][1]
            end   = temp['end'][0] + ':' + temp['end'][1]
            active_classes[prof][c]['days'] = util.clean_days(temp['days'])
            # Clean up days, convert mil time to AM/PM times
            #active_classes[prof][c]["days"] = util.clean_days(temp['days'])
            active_classes[prof][c]["start"]= util.milTimeConv(start,'none',to_mil=False)
            active_classes[prof][c]["end"]= util.milTimeConv(end,'none',to_mil=False)
    # profs = list of professors that have classes
    # days = list of days in 2 letter format (i.e.: MO, TU, etc.)
    # times = list of active times (xx:yy-zz:aa AM/PM format)
    # classes = List of possible classes (P131, A100, etc.(
    # active = the prof-schedule.json file with some cleaning
    #       start/end in xx:yy format, days in normal format
    return render_template("edit_prof_list.html",profs=profs,
                           days=days,times=times,
                           classes=classes,rooms=rooms,
                           active=active_classes)

@app.route('/removeProf', methods=['POST'])
def removeProf():
    prof = request.form['professor']
    with open('config/professors.txt') as f:
        updated_list = [p for p in f if p[:-1] != prof]
    with open('config/professors.txt','w+') as f:
        for key in updated_list:
            f.write(key)
    return redirect('/updateProfList')

@app.route('/addProf',methods=['POST'])
def addProf():
    prof = request.form['professor'].capitalize()
    with open('config/professors.txt','a') as f:
        f.write('\n'+prof)
    return redirect('/updateProfList')

@app.route('/removeSchedule',methods=['POST'])
def removeSchedule():
    data = json.loads(request.form['data']) #data = { [prof name] : list([class names]) }
    json_data = json.load(open('config/prof-schedule.json'))
    for prof in data: # For every request, remove from prof-schedule.json
        for c in data[prof]:
            json_data[prof].pop(c,None)
            if len(json_data[prof]) == 0:# If prof has no classes, pop
                json_data.pop(prof)
    json.dump(json_data,open('config/prof-schedule.json','w'))
    return updateProfList()

@app.route('/addSchedule',methods=['POST'])
def addSchedule():
    global days
    data = request.form
    keys = data.keys()
    # Runs down all keys until only days are left
    c    = data[keys.pop(keys.index('class'))]
    room = data[keys.pop(keys.index('room'))]
    time = data[keys.pop(keys.index('time'))]
    prof = data[keys.pop(keys.index('professor'))].lower()
    sect = data[keys.pop(keys.index('section'))]
    # Sort keys by weekday and set that list to day
    d = sorted(keys,key=days.index)
    hyphen_pos = time.find('-')
    meridian = time[-2:]
    start = time[:hyphen_pos]
    start = util.milTimeConv(start,meridian)
    end = time[hyphen_pos+1:-3]
    end = util.milTimeConv(end,meridian)
    data = json.load(open('config/prof-schedule.json'))
    if sect != "":
        c += '-' + sect
    try:
        data[prof][c] = {"start": start, "end": end, "room": room,"days":d}
    except KeyError:
        data[prof] = {c: {"start":start,"end":end,"room":room,"days":d}}
    json.dump(data,open('config/prof-schedule.json','w'))
    return redirect('/updateProfList')

@app.route('/purgeSchedule',methods=['POST'])
def purgeSchedule():
    json.dump({},open('config/prof-schedule.json','w'))
    return redirect('/updateProfList')

@app.route('/addRoom', methods=['POST'])
def addRoom():
    global rooms,config
    room = request.form['room']
    try:
        rooms.index(room)
        return redirect('/updateProfList')
    except ValueError:
        rooms.append(room)
        config['rooms'] = rooms
        json.dump(config,open('config/config.json','w+'))
    return redirect('/updateProfList')

@app.route('/removeRoom',methods=['POST'])
def removeRoom():
    global rooms,config
    room = request.form['room']
    rooms.remove(room)
    config['rooms'] = rooms
    json.dump(config,open('config/config.json','w+'))
    return redirect('/updateProfList')

@app.route('/addClass', methods=['POST'])
def addClass():
    global classes,config
    c = request.form['class']
    try:
        classes.index(c)
        return redirect('/updateProfList')
    except ValueError:
        classes.append(c)
        config['classes'] = classes
        json.dump(config,open('config/config.json','w+'))
    return redirect('/updateProfList')

@app.route('/removeClass',methods=['POST'])
def removeClass():
    global classes,config
    c = request.form['class']
    classes.remove(c)
    config['classes'] = classes
    json.dump(config,open('config/config.json','w+'))
    return redirect('/updateProfList')

@app.route('/addTime',methods=['POST'])
def addTime():
    global times, config
    data = request.form
    sHour = data['start_hour']
    sMin  = data['start_min']
    eHour = data['end_hour']
    eMin  = data['end_min']
    meridian = data['meridian']
    timeSort(sHour,sMin,eHour,eMin,meridian) # Adds new time in sorted slot
    config['times'] = times
    json.dump(config,open('config/config.json','w'))
    return redirect('/updateProfList')

def timeSort(sHour,sMin,eHour,eMin,meridian):
    global times
    start = sHour + ':' + sMin
    end = eHour + ':' + eMin
    mil_convertable_start = util.formatTime(start)
    cleaned_start = util.time_from_list(util.milTimeConv(mil_convertable_start,meridian))
    updated_times = []
    to_add = util.formatTime(start,True)+'-'+util.formatTime(end,True)+' '+meridian
    for time in times:# Assume time to add > times element
        t = util.time_from_list(util.milTimeConv(time[:5],time[-2:]))
        if cleaned_start < t: # Check if the starting time < the times element starting time
            i = times.index(time)
            updated_times += times[:i] + [to_add] + times[i:]
            times = updated_times
            return
    # If time to add > all elements in times, append it
    times += [to_add]
    return
            

@app.route('/removeTime',methods=['POST'])
def removeTime():
    global times,config
    data = request.form['time']
    times.remove(data)
    config['times']=times
    json.dump(config,open('config/config.json','w'))
    return redirect('/updateProfList')

def datePadding(date):
    if len(date) < 2:
        return '0'+date
    return date

@app.route('/addGoogleSched',methods=['POST'])
def addGoogleSched():
    #TODO create his google cal schedule
    data = request.form
    sMonth = datePadding( data['start_month'] )
    eMonth = datePadding( data['end_month'] )
    sDay = datePadding( data['start_day'] )
    eDay = datePadding( data['end_day'] )
    start = sMonth + '-' + sDay
    end = eMonth + '-' + eDay
    year = datetime.datetime.now()
    # %YYYY-%mm-%dd = Google Cal date format
    start_date = str(year) +'-' + start
    end_date = str(year) +'-' + end
    createSchedule(start,end)
    return redirect("https://calendar.google.com")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)
