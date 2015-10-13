
#libraries
import tkinter as tk
from tkinter import filedialog
import csv
import hashlib
import uuid 
from rdflib import URIRef, BNode, Literal, Namespace, plugin, Graph, ConjunctiveGraph
from rdflib.store import Store

def readCsv(inputfile):
    try:
          f=open(inputfile);
          rf=csv.reader(f,delimiter=',');
          return rf;
    except IOError as e:
         print ("I/O error({0}): {1}".format(e.errno, e.strerror))
         raise


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
        'trans': 'http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/Transporte#'}
    return prefixes
    
def bindingPrefixes(graphs,prefixes):
    for key in prefixes:
        graphs.bind(key, prefixes[key])
    return graphs
    
def createRDF(row):
      
    idencode=row[0].encode('utf-8')
    print (uuid.uuid5(naptan, idencode))
    # stopLon,stopLat=ConvertProj(row[4],row[5])
    stopLat,stopLong=row[4],row[5]   
    noAddress=""
    stopid = objectID
    stopGeometry = "POINT ("+stopLat+" "+stopLong+")"
    stopRoute = URIRef('http://data.linkedevents.org/transit/London/route/')
    stopGUID = uid 
    stopTitle = Literal(str(row[3]))
    stopAddress = Literal(noAddress)
    stopLocnAddress = Literal(noAddress)
    stopAddressLocality = Literal('London')
    stopAdminUnitL2 = Literal('London')
    stopPublisher = URIRef('https://tfl.gov.uk/modes/buses/')
    stopBusinessType = URIRef('http://data.linkedevents.org/kos/3cixty/busstop')
    stopLabel = Literal('Bus Stop -'+str(row[3]))
    
    lst = [stopid, stopLat, stopLong, stopGeometry, stopRoute, stopGUID, stopTitle, stopAddress, stopLocnAddress,\
           stopAddressLocality, stopAdminUnitL2, stopPublisher, stopBusinessType, stopLabel]
    return lst

#this creates a url of a single bus stop with the test id
def createBusStop(stopId):
    singleStop = URIRef("http://data.linkedevents.org/transit/Milano/stop/" + stopId)
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
    naptan = Namespace("http://transport.data.gov.uk/def/naptan/")
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

def main():
   # root = tk.Tk()
    #root.withdraw()
    #inFile = filedialog.askopenfilename()
    #inFile = "C:\\WinPython-64bit-3.4.3.4\\transport\\data\\bus-stops-10-06-15.csv"
    inFile = "small.csv"
  #  print (inFile)
    outFile="small.ttl"
    csv=readCsv(inFile)
    next(csv, None)  #FILE WITH HEADERS
     
    store = plugin.get('IOMemory', Store)()
    g = Graph(store)
    graph = ConjunctiveGraph(store)
    prefixes=definePrefixes()
    bindingPrefixes(graph,prefixes)

    for row in csv:
        lstData = createRDF(row)
        createGraph(lstData,g)
    createGraph(lstData,g).serialize(outFile,format='turtle')
    

if __name__ == "__main__":
    main();
