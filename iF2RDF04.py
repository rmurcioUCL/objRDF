__author__ = 'casa'

#libraries
#import tkinter as tk
#from tkinter import filedialog
import csv
import zipfile
import uuid
import pyproj
import time
from rdflib import URIRef, Literal, Namespace, plugin, Graph, ConjunctiveGraph
from rdflib.store import Store

def readCsv(inputfile):
    try:
          f=open(inputfile);
          rf=csv.reader(f,delimiter=',');
          return rf;
    except IOError as e:
         print ("I/O error({0}): {1}".format(e.errno, e.strerror))
         raise

def getUid(n,s):
    uid=uuid.uuid5(n,s)
    return uid

def ConvertProj(lon,lat):
    Bng = pyproj.Proj(init='epsg:27700')
    Wgs84 = pyproj.Proj(init='epsg:4326')
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
        'sf' :'http://www.opengis.net/ont/sf#',
        'dct' : 'http://purl.org/dc/terms/',
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

def createRDF(row):

    naptan = Namespace("http://transport.data.gov.uk/def/naptan/")
    objectID  = row[1]
    #uid=getUid(row[0],naptan)
    idencode=row[0].encode('utf-8')
    uid=uuid.uuid5(naptan, idencode)
    stopLat,stopLong=ConvertProj(row[4],row[5])

    #stopLat,stopLong=row[4],row[5]
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
    geometryURL = URIRef('http://data.linkedevents.org/transit/Milano/busLine/' + busId + '/geometry')
    return geometryURL

#create geometry
def createGeometry(busWkt):
    routeGeometry = Literal(busWkt)
    return routeGeometry

#create routeService or serviceId
def createRouteService(route, run):
    routeService = URIRef('http://data.linkedevents.org/transit/London/service/' + route + '_' + Literal(run))
    return routeService

#create route
def createRoute(route):
    busRoute = URIRef('http://data.linkedevents.org/transit/Milano/route/' + route)
    return busRoute

#----------------------------------- Create graph ----------------------------
#creates graph of one bus stop
def createGraph(arg,g):
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
    geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
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
    g.add((singleGeometry, locn.geometry, Literal(arg[3], datatype=geosparql.wktLiteral)))
    g.add((singleStop, geo.location, singleGeometry))
    g.add((singleStop, transit.route, arg[4]))
    g.add((singleStop, schema.location, singleAddress))
    g.add((singleStop, locn.address, singleAddress))
    g.add((singleStop, dc.publisher, arg[11]))
    g.add((singleStop, locationOnt.businessType, arg[12]))
    g.add((singleStop, rdfs.label, arg[13]))
    return g
#------------- Buslines -----------    
#this creates 'store' variable for the final busline conjunctive graph
busline_store = plugin.get('IOMemory', Store)()
busline_g= Graph(busline_store)
busline_graph = ConjunctiveGraph(busline_store)

#Expected input for busline graph
#busId = UUID()
#busWkt = "LINESTRING (9.140993697015464 45.531513894876362 9.150993697015464 45.331513894876362)" 
#busRoute = '256D'
#busRun = 1
#busLabel = 'NEW OXFORD STREET - CANADA WATER BUS STATION <> #'

#busline1 = [busId, busWkt, busRoute, busRun, busLabel]

def createBuslineGraph(arg):
    #schema = Namespace("http://schema.org/")
    #naptan = Namespace("http://transport.data.gov.uk/def/naptan/")
    #owl = Namespace("http://www.w3.org/2002/07/owl#")
    #xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
    rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    #vcard = Namespace("http://www.w3.org/2006/vcard/ns#")
    #locationOnt = Namespace("http://data.linkedevents.org/def/location#")
    #geom = Namespace("http://geovocab.org/geometry#")
    #unknown = Namespace("http://data.linkedevents.org/def/unknown#")
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    #geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
    sf = Namespace("http://www.opengis.net/ont/sf#")
    dct = Namespace("http://purl.org/dc/terms/")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    transit = Namespace("http://vocab.org/transit/terms/")
    #dcterms = Namespace("http://purl.org/dc/terms/")
    #dul = Namespace("http://ontologydesignpatterns.org/ont/dul/DUL.owl#")
    locn = Namespace("http://www.w3.org/ns/locn#")
    #foaf = Namespace("http://xmlns.com/foaf/0.1/")
    #dc = Namespace("http://purl.org/dc/elements/1.1/")
    #trans = Namespace("http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/Transporte#")

#creates graph of one bus stop
    busline_g.add((createLine(arg[0]), rdf.type, transit.BusRoute))
    busline_g.add((createLine(arg[0]), geo.location, createGeometryURL(arg[0])))
    busline_g.add((createLine(arg[0]), rdfs.label, Literal(arg[4])))
    busline_g.add((createLine(arg[0]), transit.routeService, createRouteService(arg[2], arg[3])))
    busline_g.add((createLine(arg[0]), transit.route, createRoute(arg[2])))
    busline_g.add((createGeometryURL(arg[0]), rdf.type, sf.LineString))
    busline_g.add((createGeometryURL(arg[0]), locn.geometry, Literal(arg[1])))
    return busline_g

#creates graph of stops
def createBuslineTree(*args):
    for arg in args:
        createBuslineGraph(arg)
    print(createBuslineGraph(arg).serialize(format='turtle'))
#----------------------- End of buslines code -------------    

#--------------------- Bus correspondence graph -----------
#data record as in bus correspondence table
#[stop code lbsl, bus stop code, naptan atco, route, run, sequence, service]
#busCorr = ['27472', 74198, '490010288N', '256D', 1, 1, '256D_1']

#create service stop URL
def createServiceStop(service, stopCode):
    serviceStopId = URIRef('http://data.linkedevents.org/transit/London/serviceStop/' + service + '/' + Literal(stopCode))
    return serviceStopId

#create service URL
def createService(service):
    serviceURL = URIRef('http://data.linkedevents.org/transit/London/service/' + service)
    return serviceURL

#create stop URL
def createStop(stopCode):
    stopURL = URIRef('http://data.linkedevents.org/transit/London/stop/' + Literal(stopCode))
    return stopURL

#this creates 'store' variable for the final conjunctive graph
corr_store = plugin.get('IOMemory', Store)()
corr_g= Graph(corr_store)
corr_graph = ConjunctiveGraph(corr_store)

#creates graph of one bus correspondence relationship
def createBusCorrGraph(arg):
    geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
    foaf = Namespace("http://xmlns.com/foaf/0.1/")
    geom = Namespace("http://geovocab.org/geometry#")
    unknown = Namespace("http://data.linkedevents.org/def/unknown#")
    transit = Namespace("http://vocab.org/transit/terms/")
    locn = Namespace("http://www.w3.org/ns/locn#")
    vcard = Namespace('http://www.w3.org/2006/vcard/ns#')
    dcterms = Namespace("http://purl.org/dc/terms/")
    schema = Namespace('http://schema.org/')
    geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
    rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
    naptan = Namespace('http://transport.data.gov.uk/def/naptan/')
    xsd = Namespace('http://www.w3.org/2001/XMLSchema#')
    owl = Namespace('http://www.w3.org/2002/07/owl#')
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    locationOnt = Namespace("http://data.linkedevents.org/def/location#")

    corr_g.add((createServiceStop(arg[6], arg[1]), rdf.type, transit.ServiceStop))
    corr_g.add((createServiceStop(arg[6], arg[1]), transit.service, createService(arg[6])))
    corr_g.add((createServiceStop(arg[6], arg[1]), transit.sequence, Literal(arg[5], datatype=xsd.int)))
    corr_g.add((createServiceStop(arg[6], arg[1]), transit.stop, createStop(arg[1])))
    return corr_g
    
#creates graph of stops
def createBusCorrTree(*args):
    for arg in args:
        createBusCorrGraph(arg)
    print(createBusCorrGraph(arg).serialize(format='turtle'))
#----------------------------------------- end of bus correspondence code

def main():
   # root = tk.Tk()
    #root.withdraw()
    #inFile = filedialog.askopenfilename()
    pathf="/Users/patrick/3cixty/IN/RM/"
    inFile = pathf+"bus-stops-10-06-15.csv"
    outFile=pathf+"bus.ttl"
    csv=readCsv(inFile)
    next(csv, None)  #FILE WITH HEADERS

    store = plugin.get('IOMemory', Store)()
    g = Graph(store)
    graph = ConjunctiveGraph(store)
    prefixes=definePrefixes()
    print('Binding Prefixes')
    bindingPrefixes(graph,prefixes)
    print('Creating graph...')

    for row in csv:
        lstData = createRDF(row)
        createGraph(lstData,g)
    createGraph(lstData,g).serialize(outFile,format='turtle')
    nzip = pathf+time.strftime("%Y-%m-%d")+'.zip'
    zf = zipfile.ZipFile(nzip, mode='w')
    try:
        print ('Creating zip file...')
        zf.write(outFile)
    finally:
        zf.close()
        print ('DONE!')
