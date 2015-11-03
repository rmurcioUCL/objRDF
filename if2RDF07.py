__author__ = 'casa'
# -*- coding: utf-8 -*-
#libraries

import csv
import zipfile
import uuid
import pyproj
#import time
import re
from rdflib import URIRef, Literal, Namespace, plugin, Graph, ConjunctiveGraph
from rdflib.store import Store

def readCsv(inputfile):
    try:
          f=open(inputfile,'rU');
          rf=csv.reader(f,delimiter=',');
          return rf;
    except IOError as e:
         print ("I/O error({0}): {1}".format(e.errno, e.strerror))
         raise


def getUid(r0):
    naptan = Namespace("http://transport.data.gov.uk/def/naptan/")
    #objectID  = r1
    idencode=r0.encode('utf-8')
    uid=uuid.uuid5(naptan, idencode)
    return uid

def ConvertProj(lat,lon):
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
        'qb': 'http://purl.org/linked-data/cube#',
        'travel': 'http://3cixty.com/ontology#',
        'trans': 'http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/Transporte#'}
    return prefixes

def bindingPrefixes(graphs,prefixes):
    for key in prefixes:
        graphs.bind(key, prefixes[key])
    return graphs

def getBusData(row):

    #naptan = Namespace("http://transport.data.gov.uk/def/naptan/")
    #uid=uuid.uuid5(naptan, idencode)
    #idencode=row[0].encode('utf-8')
    objectID  = row[1]    
    uid=getUid(row[0])

    stopLat=''
    stopLong=''
    try:
        stopLat,stopLong=ConvertProj(row[4],row[5])
    except TypeError as e:
        print ("wrong lat, long -".format(e))

    noAddress=""
    stopid = objectID
    stopGeometry = "POINT ("+str(stopLat) +" "+str(stopLong)+")"
    stopRoute = URIRef('http://data.linkedevents.org/transit/London/route/')
    stopGUID = uid
    stopTitle = Literal(str(row[3]))
    stopAddress = Literal(noAddress)
    stopLocnAddress = Literal(noAddress)
    stopAddressLocality = Literal('London')
    stopAdminUnitL2 = Literal('London')
    stopPublisher = URIRef('https://tfl.gov.uk/modes/buses/')
    stopBusinessType = URIRef('http://data.linkedevents.org/kos/3cixty/busstop')
    stopLabel = Literal('Bus Stop - '+str(row[3]))

    lst = [stopid, stopLat, stopLong, stopGeometry, stopRoute, stopGUID, stopTitle, stopAddress, stopLocnAddress,\
           stopAddressLocality, stopAdminUnitL2, stopPublisher, stopBusinessType, stopLabel]
    return lst

def getBusLineData(row):

    busRoute=row[0]
    busRun  = row[1]
    strg=str(busRoute)+str(busRun)   
    #print (strg)
    busId=getUid(strg)
    #print (busId)
    busWkt = row[3]
    busLabel = row[2]
    lst = [busRoute,busRun,busWkt,busLabel,busId]
    return lst

def getBusCData(row):

    stop=row[2]
    stopID  = row[1]    
    stopN=getUid(row[0])
    route = row[3]
    srun = row[4]
    seq =  row[5]
    service =  row[6]
    lst = [stop, stopID, stopN, route, srun, seq, service]
    return lst

#get station line
def validateCol(row):
    if row is not None:
        for index in range(0,len(row)):
            row[index]=re.sub('\r\t\t\t','',row[index])
    return row
    
def transfer(station,path):
    csv=readCsv(path+'station_line.csv')
    if csv is not None:
        # Skip the headers
        next(csv, None)
        for row in csv:
            row=validateCol(row)
            if row[0]==station:
                row=filter(None, row[1:len(row)])
                return row
        #print(station)        
        return []

#Get data Tube stations
def getTubeSData(row):

    x = row[0]
    y = row[1]
    station = row[2]
    description = row[3]
    wkt = row[4]
    businessType = 'http://data.linkedevents.org/kos/3cixty/subway'
    publisher = 'https://tfl.gov.uk'
    
    path = '/Users/Roberto/Documents/'
    stationLine = transfer(station,path)
   
    lines = ['Bakerloo',
                  'Central',
                  'Circle',
                  'District',
                  'Hammersmith & City',
                  'Jubilee',
                  'Metropolitan',
                  'Northern',
                  'Piccadilly',
                  'Victoria',
                  'Waterloo & City']
    lst = [x, y, station, description, wkt,businessType,publisher,lines,stationLine]
    return lst

#Get Tube Time
def getTubeTData(row,count):
    origin = row[0]
    dest   = row[1]
    time   = row[2]
    lst = [count, origin, dest, time]
    return lst 

#GetAreasData
def getAreasData(row):
    name = row[0]
    code = row[1]
    geom = row[2]
    lst = [name, code, geom]
    return lst

   
#---------------
    
#this creates a url of a single bus stop with the test id
def createBusStop(stopId):
    singleStop = URIRef("http://data.linkedevents.org/transit/London/stop/" + stopId)
    return singleStop

#this creates geometry url
def createGeometry(stopId, stopsGUID):
    singleGeometry = URIRef(('http://data.linkedevents.org/location/%s/geometry') % stopsGUID)
    return singleGeometry

#this creates single address
def createAddress(stopId, stopsGUID):
    singleAddress = URIRef(('http://data.linkedevents.org/location/%s/address') % stopsGUID)
    return singleAddress

#-------- Buslines    
#create line URL
def createLine(busId):
    lineId = URIRef('http://data.linkedevents.org/transit/London/busLine/' + busId)
    return lineId

#create line geometry url
def createGeometryURL(busId):
    geometryURL = URIRef('http://data.linkedevents.org/transit/London/busLine/' + Literal(busId) + '/geometry')
    return geometryURL

#create geometry
#def createGeometry(busWkt):
 #   routeGeometry = Literal(busWkt)
  #  return routeGeometry

#create routeService or serviceId
def createRouteService(route, run):
    routeService = URIRef('http://data.linkedevents.org/transit/London/service/' + Literal(route) + '_' + Literal(run))
    return routeService

#create route
def createRoute(route):
    busRoute = URIRef('http://data.linkedevents.org/transit/London/route/' + Literal(route))
    return busRoute

def createServiceStop(service, stopCode):
    serviceStopId = URIRef('http://data.linkedevents.org/transit/London/serviceStop/' + Literal(service) + '/' + Literal(stopCode))
    return serviceStopId
    
#create service URL
def createService(service):
    serviceURL = URIRef('http://data.linkedevents.org/transit/London/service/' + Literal(service))
    return serviceURL
#create stop URL
def createStop(stopCode):
    stopURL = URIRef('http://data.linkedevents.org/transit/London/stop/' + Literal(stopCode))
    return stopURL

def createSubwayRoute(tubelines):
    tubes = []
    for i in tubelines:
        tubeline = URIRef('http://data.linkedevents.org/transit/London/subwayRoute/' + Literal(i).replace(" ", ""))
        tubes.append(tubeline)
    return tubes

def createStation(station):
    stationName = URIRef('http://data.linkedevents.org/transit/London/subwayStop/' + Literal(station).replace(" ", ""))
    return stationName

def createStationGeom(station):
    stationGeom = URIRef(createStation(station) + '/geometry')
    return stationGeom

def addStationLine(g,lines,station):
    transit = Namespace("http://vocab.org/transit/terms/")
    for i in lines[1:]:
        singleLine = URIRef('http://data.linkedevents.org/transit/London/subwayRoute/' + Literal(i).replace(" ", ""))
        g.add((createStation(station), transit.route, singleLine))
    return g

def createArea(code):
    area = URIRef('http://data.linkedevents.org/transit/London/area/' + Literal(code))
    return area

def createAreaGeom(code):
    areaGeom = URIRef(createArea(code) + '/geometry')
    return areaGeom
    
def createTimeBetween(id):
    timeBetween = URIRef('http://data.linkedevents.org/travel/London/timeBetween#' + Literal(id))
    return timeBetween    

#-----Graphs
def createBusCGraph(arg,busline_g):
    transit = Namespace("http://vocab.org/transit/terms/")
    xsd = Namespace('http://www.w3.org/2001/XMLSchema#')
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    singleServiceStop=createServiceStop(arg[6], arg[1])
    singleService=createService(arg[6])
    singleStop=createStop(arg[1])
    
    busline_g.add((singleServiceStop, rdf.type, transit.ServiceStop))
    busline_g.add((singleServiceStop, transit.service, singleService))
    busline_g.add((singleServiceStop, transit.sequence, Literal(arg[5], datatype=xsd.int)))
    busline_g.add((singleServiceStop, transit.stop, singleStop))
    return busline_g

def createBuslineGraph(arg,busline_g):

    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    sf = Namespace("http://www.opengis.net/ont/sf#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    transit = Namespace("http://vocab.org/transit/terms/")
    locn = Namespace("http://www.w3.org/ns/locn#")
   # geom = Namespace("http://geovocab.org/geometry#")
    geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
       
    idb=arg[4].urn
    idb=idb[9:]
    singleLine=createLine(idb)
    singleGeometryURL=createGeometryURL(idb)
    singleService=createRouteService(arg[0], arg[1])
    
    busline_g.add((singleLine, rdf.type, transit.BusRoute))
    busline_g.add((singleLine, geo.location, singleGeometryURL))
    busline_g.add((singleLine, rdfs.label, Literal(arg[3])))
    busline_g.add((singleLine, transit.routeService, singleService))
    busline_g.add((singleLine, transit.route, createRoute(arg[0])))
    busline_g.add((singleGeometryURL, rdf.type, sf.LineString))
    busline_g.add((singleGeometryURL, locn.geometry, Literal(arg[2], datatype=geosparql.wktLiteral)))
    #busline_g.add((singleGeometryURL, locn.geometry, Literal(arg[2])))
    return busline_g
        
#creates graph of one bus stop
def createBusGraph(arg,g):
    schema = Namespace("http://schema.org/")
    naptan = Namespace("http://transport.data.gov.uk/def/naptan/london")
  #  owl = Namespace("http://www.w3.org/2002/07/owl#")
    xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
   # vcard = Namespace("http://www.w3.org/2006/vcard/ns#")
    locationOnt = Namespace("http://data.linkedevents.org/def/location#")
    geom = Namespace("http://geovocab.org/geometry#")
    #unknown = Namespace("http://data.linkedevents.org/def/unknown#")
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    #geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    transit = Namespace("http://vocab.org/transit/terms/")
    dcterms = Namespace("http://purl.org/dc/terms/")
    dul = Namespace("http://ontologydesignpatterns.org/ont/dul/DUL.owl#")
    locn = Namespace("http://www.w3.org/ns/locn#")
    #foaf = Namespace("http://xmlns.com/foaf/0.1/")
    dc = Namespace("http://purl.org/dc/elements/1.1/")
    #trans = Namespace("http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/Transporte#")

    singleStop = createBusStop(arg[0])
    singleAddress = createAddress(arg[0], arg[5])
    singleGeometry = createGeometry(arg[0], arg[5])
    
    g.add((singleStop, rdf.type, naptan.BusStop))
    g.add((singleStop, rdf.type, dul.Place))
    g.add((singleStop, rdf.type, transit.Stop))
    g.add((singleStop, dc.identifier, Literal(arg[0])))
    g.add((singleStop, geom.geometry, singleGeometry))
    g.add((singleStop, schema.geo, singleGeometry))
    g.add((singleAddress, rdf.type, schema.PostalAddress))
    g.add((singleAddress, rdf.type, dcterms.Location))
    g.add((singleAddress, dcterms.title, arg[6]))
    g.add((singleAddress, schema.streetAddress, arg[7]))
    g.add((singleAddress, locn.address, arg[8]))
    g.add((singleAddress, schema.addressLocality, arg[9]))
    g.add((singleAddress, locn.adminUnitL12, arg[10]))
    g.add((singleGeometry, rdf.type, geo.Point))
    g.add((singleGeometry, geo.lat, Literal(arg[1], datatype=xsd.double)))
    g.add((singleGeometry, geo.long, Literal(arg[2], datatype=xsd.double)))
    #g.add((singleGeometry, locn.geometry, Literal(arg[3], datatype=geosparql.wktLiteral)))
    g.add((singleStop, geo.location, singleGeometry))
    g.add((singleStop, transit.route, arg[4]))
    g.add((singleStop, schema.location, singleAddress))
    g.add((singleStop, locn.address, singleAddress))
    g.add((singleStop, dc.publisher, arg[11]))
    g.add((singleStop, locationOnt.businessType, arg[12]))
    g.add((singleStop, rdfs.label, arg[13]))
    return g

def createTubeSGraph(arg,g,flag):
    xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    locationOnt = Namespace("http://data.linkedevents.org/def/location#")
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    transit = Namespace("http://vocab.org/transit/terms/")
    dul = Namespace("http://ontologydesignpatterns.org/ont/dul/DUL.owl#")
    locn = Namespace("http://www.w3.org/ns/locn#")
    dc = Namespace("http://purl.org/dc/elements/1.1/")
    geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
    dct = Namespace('http://purl.org/dc/terms/')
    
    
    singleStation = createStation(str(arg[2]).strip())
    singleGeometry = createStationGeom(str(arg[2]).strip())
    
    g.add((singleStation, rdf.type, transit.Station))
    g.add((singleStation, rdf.type, dul.Place))
    g.add((singleStation, rdfs.label, Literal(str(arg[2]).strip())))
    g.add((singleStation, dct.description, Literal(str(arg[3]).strip())))
    g.add((singleStation, geo.location, createStationGeom(arg[2]))) 
    g.add((singleStation, locationOnt.businessType, URIRef("http://data.linkedevents.org/kos/3cixty/subway")))
    g.add((singleStation, dc.publisher, URIRef("https://tfl.gov.uk")))
    g.add((singleGeometry, rdf.type, geo.Point))    
    g.add((singleGeometry, geo.lat, Literal(arg[0], datatype=xsd.double)))
    g.add((singleGeometry, geo.long, Literal(arg[1], datatype=xsd.double)))
    g.add((singleGeometry, locn.geometry, Literal(arg[4], datatype=geosparql.wktLiteral)))  
    
    addStationLine(g,arg[8],arg[2])
    
    if flag:
        #for i in arg[7]:
            #g.add((i, rdf.type, transit.SubwayRoute))
        createSubwayRoute(arg[7])
    #bindingPrefixes()
    return g   

def createTubeTGraph(arg,g):
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    qb = Namespace('http://purl.org/linked-data/cube#')
    travel = Namespace('http://3cixty.com/ontology#')
    xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

    singleTime = createTimeBetween(arg[0])
    g.add((singleTime, rdf.type, qb.Observation))
    g.add((singleTime, travel.origin, createStation(arg[1])))
    g.add((singleTime, travel.destination, createStation(arg[2])))
    g.add((singleTime, travel.travelTime, Literal(arg[3], datatype=xsd.int)))
    return g
    
def createAreasGraph(arg,g):
    schema = Namespace("http://schema.org/")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    dct = Namespace('http://purl.org/dc/terms/')
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#") 
    locn = Namespace("http://www.w3.org/ns/locn#")
    
    singleArea = createArea(arg[1])
    singleAreaGeom = createAreaGeom(arg[1])
    g.add((singleArea, rdf.type, schema.AdministrativeArea))
    g.add((singleArea, rdfs.label, Literal(str(arg[0]).title())))
    g.add((singleArea, dct.identifier, Literal(arg[1])))
    g.add((singleArea, geo.location, singleAreaGeom))
    g.add((singleAreaGeom, locn.geometry, Literal(arg[2])))
    return g


def main():

    pathf="/Users/Roberto/Documents/"
#    inFileB = pathf+"bus-stops-10-06-15.csv"
#    outFileB=pathf+"bus.ttl"
#    inFileBR = pathf+"busline_content.csv"
#    outFileBR=pathf+"busR.ttl"
#    inFileBC = pathf+"busCorrespondence.csv"
#    outFileBC=pathf+"busC.ttl"
    inFileTube = pathf+"stationsTube.csv"
    outFileTube=pathf+"stationsTube.ttl"
#    inFileTube = pathf+"boroughs_coma.csv"
#    outFileTube=pathf+"boroughs_coma.ttl"
#    inFileTube = pathf+"time_between.csv"
#    outFileTube=pathf+"TubeSegmentedTime.ttl" 
 
#    csvB=readCsv(inFileB)
#    csvBR=readCsv(inFileBR)
#    csvBC=readCsv(inFileBC) 
    csvTubeS=readCsv(inFileTube)
#    csvAreas=readCsv(inFileTube)
#    csvTubeT=readCsv(inFileTube)

#    next(csvB, None)  #FILE WITH HEADERS
#    next(csvBR, None)  #FILE WITH HEADERS
#    next(csvBC, None)  #FILE WITH HEADERS
    next(csvTubeS, None)
#    next(csvAreas, None)
#    next(csvTubeT, None)
#    store = plugin.get('IOMemory', Store)()
#    g = Graph(store)
#    graph = ConjunctiveGraph(store)

#    busline_store = plugin.get('IOMemory', Store)()
#    busline_g= Graph(busline_store)
#    busline_graph = ConjunctiveGraph(busline_store)

#    busC_store = plugin.get('IOMemory', Store)()
#    busC_g= Graph(busC_store)
#    busC_graph = ConjunctiveGraph(busC_store)
    
    tubeS_store = plugin.get('IOMemory', Store)()
    tubeS_g= Graph(tubeS_store)
    tubeS_graph = ConjunctiveGraph(tubeS_store)
    
#    Areas_store = plugin.get('IOMemory', Store)()
#    Areas_g= Graph(Areas_store)
#    Areas_graph = ConjunctiveGraph(Areas_store)    

#    tubeT_store = plugin.get('IOMemory', Store)()
#    tubeT_g= Graph(tubeT_store)
#    tubeT_graph = ConjunctiveGraph(tubeT_store)    

 
    prefixes=definePrefixes()
    
    print('Binding Prefixes')
#    bindingPrefixes(graph,prefixes)
#    bindingPrefixes(busline_graph,prefixes)
#    bindingPrefixes(busC_graph,prefixes)
    bindingPrefixes(tubeS_graph,prefixes)
#    bindingPrefixes(tubeT_graph,prefixes)

#    print('Creating graph-Bus...')
#    for row in csvB:
#        lstData = getBusData(row)
#        createBusGraph(lstData,g)
#    createBusGraph(lstData,g).serialize(outFileB,format='turtle')
    
#    print('Creating graph-BusR...')
#    for row in csvBR:
#        lstData = getBusLineData(row)
#        createBuslineGraph(lstData,busline_g)
#    createBuslineGraph(lstData,busline_g).serialize(outFileBR,format='turtle')    
    
#    print('Creating graph-BusC...')
#    for row in csvBC:
#        lstData = getBusCData(row)
#        createBusCGraph(lstData,busC_g)
#    createBusCGraph(lstData,busC_g).serialize(outFileBC,format='turtle')   

    print('Creating graph-TubeS...')
    flag=1
    for row in csvTubeS:
        lstData = getTubeSData(row)
        createTubeSGraph(lstData,tubeS_g,flag)
        flag=0
    createTubeSGraph(lstData,tubeS_g,flag).serialize(outFileTube,format='turtle')    
    
#    print('Creating graph-Areas...')
#        lstData = getAreasData(row)
#    for row in csvAreas:
#        createAreasGraph(lstData,Areas_g)
#    createAreasGraph(lstData,Areas_g).serialize(outFileTube,format='turtle')    
 
#    print('Creating graph-TubeT...')
    
#    count=1
#    for row in csvTubeT:
#        lstData = getTubeTData(row,count)
#        count=count+1
#        createTubeTGraph(lstData,tubeT_g)
#    createTubeTGraph(lstData,tubeT_g).serialize(outFileTube,format='turtle')  

    
    print ('DONE!')
    
if __name__ == "__main__":
    main();
