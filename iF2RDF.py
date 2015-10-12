# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 11:22:17 2015

@author: roberto
"""

import tkinter as tk
from tkinter import filedialog
import csv
import hashlib

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

#Vocabularies   -- THIS SHOULD BE A CONSTRUCTED BASED ON THE DICTONARY DEFINITION BELOW
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
    return prefixes;

def bindingPrefixes(graphs,prefixes):
    for key in prefixes:
        graphs.bind(key, prefixes[key])
    return graphs

#this creates a url of a single bus stop with the test id
def createBusStop(stopId):
    singleStop = URIRef("http://data.linkedevents.org/transit/London/stop/" + stopId)
    return singleStop

#this creates geometry url
def createGeometry(stopsGUID):
    singleGeometry = URIRef(('http://data.linkedevents.org/location/%s/geometry') % stopsGUID)
    return singleGeometry

#this creates single address
def createAddress(stopsGUID):
    singleAddress = URIRef(('http://data.linkedevents.org/location/%s/address') % stopsGUID)
    return singleAddress
   
def Project(lon,lat):  
    # bng = pyproj.Proj(init='epsg:27700')
    # wgs84 = pyproj.Proj(init='epsg:4326')
    # lon,lat = pyproj.transform(bng,wgs84,lon,lat) 
     return lon,lat   

   
def createRDF(row,g,outputfile,nspaces):
    schema = Namespace(nspaces.get('schema'))
    rdf = Namespace(nspaces.get('rdf'))    
    naptan = Namespace(nspaces.get('naptan'))
    dc = Namespace(nspaces.get('dc'))
    geo = Namespace(nspaces.get('geo'))
    geosparql = Namespace(nspaces.get('geosparql'))
    geom = Namespace(nspaces.get('geom'))    
    xsd = Namespace(nspaces.get('xsd'))
    transit = Namespace(nspaces.get('transit'))
    dcterms = Namespace(nspaces.get('dcterms'))
    dul = Namespace(nspaces.get('dul'))
    locn = Namespace(nspaces.get('locn'))
    locationOnt = Namespace(nspaces.get('locationOnt'))
    rdfs = Namespace(nspaces.get('rdfs'))
   
    # trans = Namespace(nspaces.get(schema))
    # vcard = Namespace(nspaces.get(schema))
    #unknown = Namespace(nspaces.get(schema))
    #owl = Namespace(nspaces.get(schema))
    #foaf = Namespace(nspaces.get(schema))    

    objectID  = row[1]
    idencode=row[2].encode('utf-8')
    uid=hashlib.new('sha1')
    uid.update(idencode)
    #print(uid.hexdigest())
    uid=uid.hexdigest()
    # stopLon,stopLat=ConvertProj(row[4],row[5])
    objectLon,objectLat=row[4],row[5]        
    singleGeometry=createGeometry(uid)

    # ObjectDef
    singleStop=createBusStop(objectID)
    g.add((singleStop, rdf.type, naptan.BusStop))
    g.add((singleStop, rdf.type, dul.Place))
    g.add((singleStop, rdf.type, transit.Stop))
    g.add((singleStop, dc.identifier, Literal(objectID)))
    g.add((singleStop, geom.geometry, singleGeometry))
    g.add((singleStop, schema.geo, singleGeometry))

    #ObjectSpatialPosition
    singleAddress=createAddress(uid)
    g.add((singleAddress, rdf.type, schema.PostalAddress))
    g.add((singleAddress, rdf.type, dcterms.Location))
    g.add((singleAddress, dcterms.title, Literal(str(row[3])) ))
    g.add((singleAddress, schema.streetAddress,  Literal("")))
    g.add((singleAddress, locn.address, Literal("")))
    g.add((singleAddress, schema.addressLocality, Literal("London")))
    g.add((singleAddress, locn.adminUnitL12, Literal("London")))

    #ObjectGeometry
    stopGeometry = "POINT ("+objectLat+" "+objectLat+")"
    g.add((singleGeometry, rdf.type, geo.Point))
    g.add((singleGeometry, geo.long, Literal(objectLon, datatype=xsd.double)))
    g.add((singleGeometry, geo.lat, Literal(objectLat, datatype=xsd.double)))
    g.add((singleGeometry, locn.geometry, Literal(stopGeometry, datatype=geosparql.wktLiteral)))
 
   
    g.add((singleStop, geo.location, singleGeometry))
    g.add((singleStop, transit.route, Literal("")))
    g.add((singleStop, schema.location, singleAddress))
    g.add((singleStop, locn.address, singleAddress))
    g.add((singleStop, dc.publisher,  URIRef("https://tfl.gov.uk/modes/buses/")))
    g.add((singleStop, locationOnt.businessType, URIRef('http://data.linkedevents.org/kos/3cixty/busstop')))
    g.add((singleStop, rdfs.label,Literal("")))
    print(objectID+"\n")
    return g
    
def main():
    root = tk.Tk()
    root.withdraw()
    inFile = filedialog.askopenfilename()
    print (inFile)
    outFile=inFile+".ttl"
    csv=readCsv(inFile)
    
    nspaces=dict([('schema',  "http://schema.org/"), ('naptan',"http://transport.data.gov.uk/def/naptan/"), ('foaf', "http://xmlns.com/foaf/0.1/"), \
                    ('xsd', "http://www.w3.org/2001/XMLSchema#"), ('rdfs', "http://www.w3.org/2000/01/rdf-schema#"), ('vcard', "http://www.w3.org/2006/vcard/ns#"),  \
                    ('locationOnt', "http://data.linkedevents.org/def/location#"), ('geom', "http://geovocab.org/geometry#"), ('unknown', "http://data.linkedevents.org/def/unknown#"), \
                    ('geo', "http://www.w3.org/2003/01/geo/wgs84_pos#"), ('geosparql', "http://www.opengis.net/ont/geosparql#"), ('rdf', "http://www.w3.org/2000/01/rdf-schema#"), \
                    ('transit', "http://vocab.org/transit/terms/"), ('dcterms', "http://purl.org/dc/terms/"), ('dul', "http://ontologydesignpatterns.org/ont/dul/DUL.owl#"), \
                    ('locn', "http://www.w3.org/ns/locn#"),  ('trans', "http://vocab.linkeddata.es/datosabiertos/def/urbanismo-infraestructuras/Transporte#")]);
   # print (nspaces.values())
    
    store = plugin.get('IOMemory', Store)()
    g=Graph(store)
    graph = ConjunctiveGraph(store)

    prefixes=definePrefixes()
    g=bindingPrefixes(graph,prefixes)
    
    next(csv, None)  #FILE WITH HEADERS
    for row in csv:
        createRDF(row,g,outFile,nspaces)
  
    g.serialize(outFile,format='turtle')
  
        
if __name__ == "__main__":
    main();
