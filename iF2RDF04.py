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
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'transit': 'http://vocab.org/transit/terms/',
        'dcterms': 'http://purl.org/dc/terms/',
        'dul': 'http://ontologydesignpatterns.org/ont/dul/DUL.owl#',
        'locn': 'http://www.w3.org/ns/locn#',
        'foaf': 'http://xmlns.com/foaf/0.1/',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'trans': 'http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/Transporte#'
        'qb': 'http://purl.org/linked-data/cube#',
        'dct' : 'http://purl.org/dc/terms/'
        }
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
#----------- TUBE SAMPLE DATA
#tube_stations_rdf_ready.csv
tubeStation = [-0.280251, 51.5028, 'Acton Town Station', 'Acton Town Station, London Underground Ltd., Gunnersbury Lane, London, W3 8HN', 'POINT(-0.280251204967499 51.5027503967285)']
# an array
tubeLines = [
    'Bakerloo', 'Central', 'Circle', 'District', 'Hammersmith & City', 'Jubilee', 'Metropolitan', 'Northern', 'Piccadilly', 'Victoria', 'Waterloo & City'
]
#lines per station - sample data
#station_line.csv
stationLine = ['Action Town Station', 'Piccadilly', 'District', 'test space Central']

#------------------ Graph for Tube --------------------------------------------------------

#create station
def createStation(name):
    station = URIRef('http://data.linkedevents.org/transit/London/subwayStop/' + Literal(name).replace(" ", ""))
    return station

#create station geometry URL
def createStationGeometry(name):
    stationGeometry = URIRef('http://data.linkedevents.org/transit/London/subwayStop/' + Literal(name).replace(" ", "") + '/geometry')
    return stationGeometry

#create subway route - batch
def createSubwayRoute():
    tubes = []
    for i in tubeLines:
        tubeline = URIRef('http://data.linkedevents.org/transit/London/subwayRoute/' + Literal(i).replace(" ", ""))
        tubes.append(tubeline)
    return tubes

#create subway route for pairs station-line. station_line.csv is the input file
def createSingleLine(name):
    singleLine = URIRef('http://data.linkedevents.org/transit/London/subwayRoute/' + Literal(name).replace(" ", ""))
    return singleLine

#------------------------- The graph for Tube
#this creates 'store' variable for the final conjunctive graph
tstore = plugin.get('IOMemory', Store)()
tg = Graph(tstore)
tgraph = ConjunctiveGraph(tstore)

#creates graph
def createTubeStationGraph(arg):

    tubes = createSubwayRoute()

    tg.add((createStation(arg[2]), rdf.type, transit.Station))
    tg.add((createStation(arg[2]), rdf.type, dul.Place))
    tg.add((createStation(arg[2]), rdfs.label, Literal(arg[2])))
    tg.add((createStation(arg[2]), dct.description, Literal(arg[3])))
    tg.add((createStation(arg[2]), geo.location, createStationGeometry(arg[2])))
    tg.add((createStation(arg[2]), locationOnt.businessType, URIRef('http://data.linkedevents.org/kos/3cixty/subway')))
    tg.add((createStation(arg[2]), dc.publisher, URIRef('https://tfl.gov.uk')))

    tg.add((createStationGeometry(arg[2]), rdf.type, geo.Point))
    tg.add((createStationGeometry(arg[2]), geo.lat, Literal(arg[1], datatype=xsd.double)))
    tg.add((createStationGeometry(arg[2]), geo.long, Literal(arg[0], datatype=xsd.double)))
    tg.add((createStationGeometry(arg[2]), locn.geometry, Literal(arg[4], datatype=geosparql.wktLiteral)))
    def createLines():
        for i in tubes:
            tg.add(((i), rdf.type, transit.SubwayRoute))
        return tg
#this adds pairs station-line for a single record.
    def addStationLine(lines):
        for i in lines[1:]:
            tg.add((createStation(arg[2]), transit.route, createSingleLine(i)))
        return tg

    createLines()
    addStationLine(stationLine)
    return tg

#creates the tree of data
def createTubeStationTree(*args):
    for arg in args:
        createTubeStationGraph(arg)
    print(createTubeStationGraph(arg).serialize(format='turtle'))


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
