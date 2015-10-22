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

def writeLog(status,row):

    if status!=0:
        if status==1:
            row.append('P1')
            writeCsv('P.csv',row)
            return
        elif status==2:
            row.append('P2')
            writeCsv('P.csv',row)
            return
    else:
        writeCsv('cleaned.csv',row)
        return row

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
        status=validateStopCode(busData[index][0])
        writeLog(status,busData[index])

        if(status==0):
            status=validateBusStop(busData[index][1])
            writeLog(status,busData[index])

        if(status==0):
            status=validateNaptan(busData[index][2])
            writeLog(status,busData[index])

        if(status==0):
            status=validateLonLatNum(busData[index][4],busData[index][5])
            writeLog(status,busData[index])

        if(status==0):
            status=validateLonLatNaN(busData[index][4],busData[index][5])
            writeLog(status,busData[index])

        if(status==0):
            status=validateHeading(busData[index][6])
            writeLog(status,busData[index])

        if(status==0):
            status=validateStopArea(busData[index][7])
            writeLog(status,busData[index])

        if(status==0):
            status=validateVirtualBusStop(busData[index][8])
            writeLog(status,busData[index])
