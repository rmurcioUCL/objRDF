# coding=utf-8
__author__ = 'patrick'

__author__ = 'Wick 1'
__author__ = 'casa'
# -*- coding: utf-8 -*-
#libraries
#import tkinter as tk
#from tkinter import filedialog
import csv
import zipfile
import uuid
import pyproj
#import time
from rdflib import URIRef, Literal, Namespace, plugin, Graph, ConjunctiveGraph
from rdflib.store import Store

def readCsv(inputfile): #+TICKED
    try:
          f=open(inputfile,'rU');
          rf=csv.reader(f,delimiter=',');
          return rf;
    except IOError as e:
         print ("I/O error({0}): {1}".format(e.errno, e.strerror))
         raise

'''
def createZip(nzip,outFile):
    zf = zipfile.ZipFile(nzip, mode='w')
    try:
        print ('Creating zip file...')
        zf.write(outFile)
    finally:
        print ('Zip created')
        zf.close()
'''

def getUid(r0): #+TICKED
    naptan = Namespace("http://transport.data.gov.uk/def/naptan/") ##MAYBE CHANGE??##
    #objectID  = r1
    idencode=r0.encode('utf-8')
    uid=uuid.uuid5(naptan, idencode)
    return uid

def ConvertProj(lat,lon): #+TICKED
    Bng = pyproj.Proj(init='epsg:27700')
    Wgs84 = pyproj.Proj(init='epsg:4326')
    #print (lat+'-'+lon)
    wgsLon,wgsLat = pyproj.transform(Bng,Wgs84,lon, lat)
    return wgsLon,wgsLat

def definePrefixes():

#Vocabularies   -- THIS SHOULD BE A CONSTRUCTED BASED ON THE A DICTONARY DEFINITION
    prefixes = {'schema':'http://schema.org/',
        'naptan':'http://transport.data.gov.uk/def/naptan/',
        'owl':'http://www.w3.org/2002/07/owl#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'vcard': 'http://www.w3.org/2006/vcard/ns#',
        'locationOnt': 'http://data.linkedevents.org/def/location#',
        'geom': 'http://geovocab.org/geometry#',
        'unknown': 'http://data.linkedevents.org/def/unknown#',
        'geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
        'geosparql': 'http://www.opengis.net/ont/geosparql#',
        'sf': 'http://www.opengis.net/ont/sf#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'transit': 'http://vocab.org/transit/terms/',
        'dcterms': 'http://purl.org/dc/terms/',
        'dul': 'http://ontologydesignpatterns.org/ont/dul/DUL.owl#',
        'locn': 'http://www.w3.org/ns/locn#',
        'foaf': 'http://xmlns.com/foaf/0.1/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'trans': 'http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/Transporte#'}
    return prefixes

def bindingPrefixes(graphs,prefixes): #+TICKED
    for key in prefixes:
        graphs.bind(key, prefixes[key])
    return graphs

def getTrainData(row): #amended #+TICKED

    #naptan = Namespace("http://transport.data.gov.uk/def/naptan/")
    #uid=uuid.uuid5(naptan, idencode)
    #idencode=row[0].encode('utf-8')
    objectID  = row[1]
    uid=getUid(row[0])

    stationLat=''
    stationLong=''
    try:
        stationLat,stationLong=ConvertProj(row[6],row[7])
    except TypeError as e:
        print ("wrong lat, long -".format(e))

    #noAddress=""
    stationid = objectID
    stationGeometry = "POINT ("+str(stationLat) +" "+str(stationLong)+")"
    stationRoute = URIRef('http://data.linkedevents.org/transit/London/route/') #DOESNT NAME THE ROUTE YET- NEED TO BE SOURCED FROM ANOTHER FILE
    stationGUID = uid
    stationTitle = Literal(str(row[3]))
    #stopAddress = Literal(noAddress)
    #stopLocnAddress = Literal(noAddress)
    #stopAddressLocality = Literal('London')
    #stopAdminUnitL2 = Literal('London')
    stationPublisher = URIRef('https://tfl.gov.uk/modes/trains/') ##??IS THIS CORRECT??
    stationBusinessType = URIRef('http://data.linkedevents.org/kos/3cixty/trainstation')
    #stopLabel = Literal('Train Stop - '+str(row[3]))

    #lst = [stopid, stopLat, stopLong, stopGeometry, stopRoute, stopGUID, stopTitle, stopAddress, stopLocnAddress,\
    #       stopAddressLocality, stopAdminUnitL2, stopPublisher, stopBusinessType, stopLabel]
    lst = [stationid, stationLat, stationLong, stationGeometry, stationRoute, stationGUID, stationTitle, stationBusinessType, stationPublisher]
    return lst

'''
def getTrainLineData(row):

    trainRoute=row[0]
    trainRun  = row[1]
    trainId=getUid(trainRoute)
    trainWkt = row[3]
    trainLabel = row[2]
    lst = [trainId, trainWkt, trainRoute, trainRun, trainLabel]
    return lst
'''
'''
def getTrainCData(row):

    stop=row[0]
    stopID  = row[1]
    stopN=getUid(row[2])
    route = row[3]
    srun = row[4]
    seq =  row[5]
    service =  row[6]
    lst = [stop, stopID, stopN, route, srun, seq, service]
    return lst
'''
#this creates a url of a single train station with the test id
def createTrainStation(stationId): #update to train
    singleStation = URIRef("http://data.linkedevents.org/transit/London/station/" + stationId)
    return singleStation

#this creates geometry url
def createGeometry(stationId, stationGUID): #+TICKED
    singleGeometry = URIRef(('http://data.linkedevents.org/location/%s/geometry') % stationGUID)
    return singleGeometry

#this creates single address
def createAddress(stationId, stationGUID):
    singleAddress = URIRef(('http://data.linkedevents.org/location/%s/address') % stationGUID)
    return singleAddress

#-------- Trainlines
'''
#create line URL
def createLine(trainId):
    lineId = URIRef('http://data.linkedevents.org/transit/London/trainLine/' + trainId)
    return lineId


#create line geometry url
def createGeometryURL(trainId):
    geometryURL = URIRef('http://data.linkedevents.org/transit/London/trainLine/' + trainId + '/geometry')
    return geometryURL

#create geometry
#def createGeometry(trainWkt):
 #   routeGeometry = Literal(trainWkt)
  #  return routeGeometry


#create routeService or serviceId
def createRouteService(route, run):
    routeService = URIRef('http://data.linkedevents.org/transit/London/service/' + route + '_' + Literal(run))
    return routeService

#create route
def createRoute(route):
    trainRoute = URIRef('http://data.linkedevents.org/transit/London/route/' + route)
    return trainRoute


def createServiceStop(service, stopCode):
    serviceStopId = URIRef('http://data.linkedevents.org/transit/London/serviceStop/' + service + '/' + Literal(stopCode))
    return serviceStopId


#create service URL
def createService(service):
    serviceURL = URIRef('http://data.linkedevents.org/transit/London/service/' + service)
    return serviceURL


#create stop URL
def createStop(stopCode): #+TICKED
    stopURL = URIRef('http://data.linkedevents.org/transit/London/station/' + Literal(stopCode)) #amended
    return stopURL


def createTrainCGraph(arg,trainline_g): ##?
    transit = Namespace("http://vocab.org/transit/terms/")
    xsd = Namespace('http://www.w3.org/2001/XMLSchema#')
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    singleServiceStop=createServiceStop(arg[6], arg[1])
    singleService=createService(arg[6])
    singleStation=createStop(arg[1])

    trainline_g.add((singleServiceStop, rdf.type, transit.ServiceStop))
    trainline_g.add((singleServiceStop, transit.service, singleService))
    trainline_g.add((singleServiceStop, transit.sequence, Literal(arg[5], datatype=xsd.int)))
    trainline_g.add((singleServiceStop, transit.stop, singleStation))
    return trainline_g

def createTrainGraph(arg,trainline_g): #??

    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    sf = Namespace("http://www.opengis.net/ont/sf#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    transit = Namespace("http://vocab.org/transit/terms/")
    locn = Namespace("hƒttp://www.w3.org/ns/locn#")
    #geosparql = Namespace("http://www.opengis.net/ont/geosparql#")

    idb=arg[0].urn
    idb=idb[9:]
    singleLine=createLine(idb)
    singleGeometryURL=createGeometryURL(idb)
    singleService=createRouteService(arg[2], arg[3])

    trainline_g.add((singleLine, rdf.type, transit.trainRoute)) #trainroute to trainroute
    trainline_g.add((singleLine, geo.location, singleGeometryURL))
    trainline_g.add((singleLine, rdfs.label, Literal(arg[4])))
    trainline_g.add((singleLine, transit.routeService, singleService))
    trainline_g.add((singleLine, transit.route, createRoute(arg[2])))
    trainline_g.add((singleGeometryURL, rdf.type, sf.LineString))
    trainline_g.add((singleGeometryURL, locn.geometry, Literal(arg[1], datatype=geosparql.wktLiteral)))
    return trainline_g
'''

#creates graph of one train station
def createTrainGraph(arg,g): #+TICKED
    schema = Namespace("http://schema.org/")
    naptan = Namespace("http://transport.data.gov.uk/def/naptan/london")
  # owl = Namespace("http://www.w3.org/2002/07/owl#")
    xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
  # vcard = Namespace("http://www.w3.org/2006/vcard/ns#")
    locationOnt = Namespace("http://data.linkedevents.org/def/location#")
  # geom = Namespace("http://geovocab.org/geometry#")
  # unknown = Namespace("http://data.linkedevents.org/def/unknown#")
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    transit = Namespace("http://vocab.org/transit/terms/")
  # dcterms = Namespace("http://purl.org/dc/terms/")
    dul = Namespace("http://ontologydesignpatterns.org/ont/dul/DUL.owl#")
    locn = Namespace("http://www.w3.org/ns/locn#")
    stationRouteService = URIRef('http://data.linkedevents.org/transit/London/routeService/') ##NEW OBJECT##
  # foaf = Namespace("http://xmlns.com/foaf/0.1/")
    dc = Namespace("http://purl.org/dc/elements/1.1/")
  # trans = Namespace("http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/Transporte#")

    singleStation = createTrainStation(arg[0])
    singleAddress = createAddress(arg[0], arg[5]) ##check arg[5]#singleStation = self.createTrainStation(stationid)
    singleGeometry = createGeometry(arg[0], arg[5]) #check arg[5]#singleAddress = self.createAddress(stationGUID)

    g.add((singleStation, rdf.type, naptan.TrainStation))
    g.add((singleStation, rdf.type, dul.Place))
    g.add((singleStation, rdf.type, transit.Station))
    g.add((singleStation, dc.identifier, Literal(arg[0])))
    #g.add((singleStation, geom.geometry, singleGeometry))
    #g.add((singleStation, schema.geo, singleGeometry))
    #g.add((singleAddress, rdf.type, schema.PostalAddress))
    #g.add((singleAddress, rdf.type, dcterms.Location))
    #g.add((singleAddress, dcterms.title, arg[6]))
    #g.add((singleAddress, schema.streetAddress, arg[7]))
    #g.add((singleAddress, locn.address, arg[8]))
    #g.add((singleAddress, schema.addressLocality, arg[9]))
    #g.add((singleAddress, locn.adminUnitL12, arg[10]))
    g.add((singleGeometry, rdf.type, geo.Point))
    g.add((singleGeometry, geo.lat, Literal(arg[1], datatype=xsd.double)))
    g.add((singleGeometry, geo.long, Literal(arg[2], datatype=xsd.double)))
    g.add((singleGeometry, locn.geometry, Literal(arg[3], datatype=geosparql.wktLiteral)))
    g.add((singleStation, transit.route, arg[4]))
    g.add((singleStation, transit.routeService, stationRouteService)) ##NEW PREDICATE##
    g.add((singleStation, schema.name, singleAddress)) #NEW
    g.add((singleStation, geo.location, singleAddress)) #g.add((singleStation, schema.location, singleAddress))
    #g.add((singleStation, locn.address, singleAddress))
    g.add((singleStation, dc.publisher, arg[8]))
    g.add((singleStation, locationOnt.businessType, (arg[7])))
    g.add((singleStation, rdfs.label, Literal(arg[6])))  #g.add((singleStation, rdfs.label, arg[3]))
    return g

def main(): #+TICKED
    #root = tk.Tk()
    #root.withdraw()
    #inFile = filedialog.askopenfilename()
    pathf="/Users/patrick/3cixty/IN/openDataSources/"
    inFileB = pathf+"RailReferences_Naptan_151022.csv"
    outFileB=pathf+"train_stations.ttl"
    #inFileBR = pathf+"trainline_content.csv"
    #outFileBR=pathf+"trainR.ttl"
    #inFileBC = pathf+"traincorrespondence.csv"
    #outFileBC=pathf+"trainC.ttl"

    csvB=readCsv(inFileB)
    #csvBR=readCsv(inFileBR)
    #csvBC=readCsv(inFileBC)


    next(csvB, None)  #FILE WITH HEADERS
    #next(csvBR, None)  #FILE WITH HEADERS
    #next(csvBC, None)  #FILE WITH HEADERS

    store = plugin.get('IOMemory', Store)()
    g = Graph(store)
    graph = ConjunctiveGraph(store)
    #trainline_store = plugin.get('IOMemory', Store)()
    #trainline_g= Graph(trainline_store)
    #trainline_graph = ConjunctiveGraph(trainline_store)
    #trainC_store = plugin.get('IOMemory', Store)()
    #trainC_g= Graph(trainC_store)
    #trainC_graph = ConjunctiveGraph(trainC_store)


    prefixes=definePrefixes()
    print('Binding Prefixes')
    bindingPrefixes(graph,prefixes)
    #bindingPrefixes(trainline_graph,prefixes)
    #bindingPrefixes(trainC_graph,prefixes)

    print('Creating graph-Train...') #AMENDED
    for row in csvB:
        lstData = getTrainData(row)
        createTrainGraph(lstData,g)
    createTrainGraph(lstData,g).serialize(outFileB,format='turtle')

    #print('Creating graph-trainR...')
    #for row in csvBR:
    #    lstData = gettrainLineData(row)
    #    createtrainlineGraph(lstData,trainline_g)
    #createtrainlineGraph(lstData,trainline_g).serialize(outFileBR,format='turtle')

    #print('Creating graph-trainC...')
    #for row in csvBR:
    #    lstData = gettrainCData(row)
    #    createtrainCGraph(lstData,trainC_g)
    #createTrainCGraph(lstData,trainC_g).serialize(outFileBC,format='turtle')
    #nzip = pathf+time.strftime("%Y-%m-%d")+'.zip'
   # nzipB = pathf+outFileB+'.zip'
   # nzipBR = pathf+outFileBR+'.zip'
   # createZip(nzipB,outFileB)
   # createZip(nzipBR,outFileBR)

    print ('DONE!')

if __name__ == "__main__":
    main();
