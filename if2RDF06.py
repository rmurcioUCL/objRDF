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

def readCsv(inputfile):
    try:
          f=open(inputfile,'rU');
          rf=csv.reader(f,delimiter=',');
          return rf;
    except IOError as e:
         print ("I/O error({0}): {1}".format(e.errno, e.strerror))
         raise

def createZip(nzip,outFile):
    zf = zipfile.ZipFile(nzip, mode='w')
    try:
        print ('Creating zip file...')
        zf.write(outFile)
    finally:
        print ('Zip created')
        zf.close()

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



#Get data Tube stations
def getTubeSData(row):

    x = row[0]
    y = row[1]
    station = row[2]
    description = row[3]
    wkt = row[4]
    #stationLine = stationLine
    #lines = lines
    lst = [x, y, station, description, wkt]
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

def createTubeSGraph(arg,g):
    xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    locationOnt = Namespace("http://data.linkedevents.org/def/location#")
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    transit = Namespace("http://vocab.org/transit/terms/")
    dul = Namespace("http://ontologydesignpatterns.org/ont/dul/DUL.owl#")
    locn = Namespace("http://www.w3.org/ns/locn#")
    dc = Namespace("http://purl.org/dc/elements/1.1/")
    dcterms = Namespace("http://purl.org/dc/terms/")
    geosparql = Namespace("http://www.opengis.net/ont/geosparql#")

    
    tubelines = ['Bakerloo',
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
    tubes = createSubwayRoute(tubelines)
    singleStation = createStation(arg[2])
    singleGeometry = createStationGeom(arg[2])
    g.add((singleStation, rdf.type, transit.Station))
    g.add((singleStation, rdf.type, dul.Place))
    g.add((singleStation, rdfs.label, Literal(arg[2])))
    g.add((singleStation, dcterms.description, Literal(arg[3])))
    g.add((singleStation, geo.location, createStationGeom(arg[2])))
    g.add((singleStation, locationOnt.businessType, URIRef('http://data.linkedevents.org/kos/3cixty/subway')))
    g.add((singleStation, dc.publisher, URIRef('https://tfl.gov.uk')))
    g.add((singleGeometry, rdf.type, geo.Point))    
    g.add((singleGeometry, geo.lat, Literal(arg[1], datatype=xsd.double)))
    g.add((singleGeometry, geo.long, Literal(arg[2], datatype=xsd.double)))
    g.add((singleGeometry, locn.geometry, Literal(arg[4], datatype=geosparql.wktLiteral)))  
    
    for i in tubes:
        g.add((i, rdf.type, transit.SubwayRoute))
    #bindingPrefixes()
    return g   

def main():
   # root = tk.Tk()
    #root.withdraw()
    #inFile = filedialog.askopenfilename()
    pathf="/Users/Roberto/Documents/"
#    inFileB = pathf+"bus-stops-10-06-15.csv"
#    outFileB=pathf+"bus.ttl"
#    inFileBR = pathf+"busline_content.csv"
#    outFileBR=pathf+"busR.ttl"
#    inFileBC = pathf+"busCorrespondence.csv"
#    outFileBC=pathf+"busC.ttl"
    inFileTube = pathf+"stationsTube.csv"
    outFileTube=pathf+"stationsTube.ttl"
 
 
#    csvB=readCsv(inFileB)
#    csvBR=readCsv(inFileBR)
#    csvBC=readCsv(inFileBC) 
    csvTubeS=readCsv(inFileTube)
    
#    next(csvB, None)  #FILE WITH HEADERS
#    next(csvBR, None)  #FILE WITH HEADERS
#    next(csvBC, None)  #FILE WITH HEADERS
    next(csvTubeS, None)

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
    
    prefixes=definePrefixes()
    print('Binding Prefixes')
#    bindingPrefixes(graph,prefixes)
#    bindingPrefixes(busline_graph,prefixes)
#    bindingPrefixes(busC_graph,prefixes)
 
    bindingPrefixes(tubeS_graph,prefixes)
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
    for row in csvTubeS:
        lstData = getTubeSData(row)
        createTubeSGraph(lstData,tubeS_g)
    createTubeSGraph(lstData,tubeS_g).serialize(outFileTube,format='turtle')    
    
    
    #nzip = pathf+time.strftime("%Y-%m-%d")+'.zip'
   # nzipB = pathf+outFileB+'.zip'
   # nzipBR = pathf+outFileBR+'.zip'
   # createZip(nzipB,outFileB)
   # createZip(nzipBR,outFileBR)
    
    print ('DONE!')
    
if __name__ == "__main__":
    main();
