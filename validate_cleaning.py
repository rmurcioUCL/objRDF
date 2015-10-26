__author__ = '3cixty team'

import csv
import os
import re


def validateStopCode(StopCode):
    if not StopCode or StopCode =='NaN' or StopCode =='NONE':
        return 2
    else:
        return 0


def validateBusStop(BusStop):
    if not BusStop or BusStop =='NaN' or BusStop =='NONE':
        return 1
    else:
        return 0


def validateNaptan(Naptan):
    if not Naptan or Naptan =='NaN' or Naptan =='NONE':
        return 1
    else:
        if(Naptan.find('E')!=-1 and Naptan.find('.')!=-1):
            return 1
        else:
            naptanlen=len(Naptan)
            if(naptanlen>9):
                if (Naptan[(naptanlen-2)].isdigit() and Naptan[(naptanlen-1)].isdigit()):
                    return 1
                else:
                    return 0
            else:
                return 1


def validateHeading(Heading):
    if not Heading or Heading =='NaN' or Heading =='NONE':
        return 1
    else:
        return 0


def validateStopArea(Stoparea):
    if not Stoparea or Stoparea =='NaN' or Stoparea =='NONE':
        return 1
    else:
        return 0

def validateVirtualBusStop(VirtualBusStop):
    if not VirtualBusStop or VirtualBusStop =='NaN' or VirtualBusStop =='NONE':
        return 1
    else:
        return 0

def validateLonLatNum(Lon,Lat):
    if not Lon.isdigit() and not Lat.isdigit():
        return 2
    else:
        return 0

def validateLonLatNaN(Lon,Lat):
    if (not Lon or Lon=='NaN' or Lon=='NONE' ) and (not Lat or Lat=='NaN' or Lat=='NONE'):
        return 1
    else:
        return 0

def writeCsv(output,row):
    #print row
    row=[(str.strip()) for str in row]
    if os.path.exists(output):
        f = open(output, 'a')
        spamwriter = csv.writer(f,lineterminator='\n')
        spamwriter.writerow(row)
    else:
        f = open(output, 'w+')
        spamwriter = csv.writer(f,lineterminator='\n')
        spamwriter.writerow(row)
        f.close()

def writeLogP(status,row):

    if status==1:
        row.append('P1')
        writeCsv('P.csv',row)
        return 1
    elif status==2:
        row.append('P2')
        writeCsv('P.csv',row)
        return 2


def writeCleaned(row):
    writeCsv('cleaned.csv',row)
    return 0


def cleanSpecialCharacter(row):
    for index in range(0,len(row)):
        cleaned=re.sub('[<>#]','',row[index])
        row[index]=re.sub('[/]','-',cleaned)
    return row


if __name__ == "__main__":

    inputfile='bus-stops-10-06-15.csv'

    f =open(inputfile)

    busData=list(csv.reader(f,delimiter=','))

    print  'The file is validating and cleaning....'

    for index in range(1,len(busData)):

        # Clean special character for all columns
        busData[index]=cleanSpecialCharacter(busData[index])

        # Validate data
        status0=validateStopCode(busData[index][0])
        status1=validateBusStop(busData[index][1])
        status2=validateNaptan(busData[index][2])
        status3=validateLonLatNum(busData[index][4],busData[index][5])
        status4=validateLonLatNaN(busData[index][4],busData[index][5])
        status5=validateHeading(busData[index][6])
        status6=validateStopArea(busData[index][7])
        status7=validateVirtualBusStop(busData[index][8])

        if status0==0 and status1==0 and status2==0 and status3==0 and status4==0 and status5==0 and status6==0 and status7==0:
            writeCleaned(busData[index])
            continue

        if status0!=0:
            writeLogP(status0,busData[index])
        elif status1!=0:
            writeLogP(status1,busData[index])
        elif status2!=0:
            writeLogP(status2,busData[index])
        elif status3!=0:
            writeLogP(status3,busData[index])
        elif status4!=0:
            writeLogP(status4,busData[index])
        elif status5!=0:
            writeLogP(status5,busData[index])
        elif status6!=0:
            writeLogP(status6,busData[index])
        elif status7!=0:
            writeLogP(status7,busData[index])


