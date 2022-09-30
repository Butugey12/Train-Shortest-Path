#converts a string time into a integer value.
#"08:32" -> 832
def timeToNumber(time):
    time=time.strip()
    if len(time)==4:
        time="0"+time
    hours=time[:2]
    minutes=time[3:]
    return int(hours + minutes)

#converts a integer value into a string time.
#832 -> "08:32"
def numberToTime(time):
    timeStr=str(time)
    if len(timeStr) > 3:
        hours=timeStr[:2]
        minutes=timeStr[2:]
    elif len(timeStr) > 2:
        hours="0"+timeStr[:1]
        minutes=timeStr[1:]
    elif len(timeStr) > 1:
        hours="00"
        minutes=timeStr[0:]
    elif len(timeStr) > 0:
        hours="00"
        minutes="0"+timeStr[0:]
    else:
        hours="00"
        minutes="00"
    return hours + ":" +minutes