# coding=utf-8
__author__ = 'patrick'
__author__ = 'Wick 1'
__author__ = 'casa'
# -*- coding: utf-8 -*-
#libraries
#import tkinter as tk
#from tkinter import filedialog
import csv
import uuid
import pyproj
from rdflib import URIRef, Literal, Namespace, plugin, Graph, ConjunctiveGraph
from rdflib.store import Store

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


class RDF:
    def __init__(self):
        self.schema = Namespace("http://schema.org/")
        self.naptan = Namespace("http://transport.data.gov.uk/def/naptan/")
        self.xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
        self.dfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
        self.locationOnt = Namespace("http://data.linkedevents.org/def/location#")
        self.geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
        self.geosparql = Namespace("http://www.opengis.net/ont/geosparql#")
        self.rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.transit = Namespace("http://vocab.org/transit/terms/")
        self.dul = Namespace("http://ontologydesignpatterns.org/ont/dul/DUL.owl#")
        self.locn = Namespace("http://www.w3.org/ns/locn#")
        self.dc = Namespace("http://purl.org/dc/elements/1.1/")
        self.rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

        self.store = plugin.get('IOMemory', Store)()
        self.g = Graph(self.store)
        self.graph = ConjunctiveGraph(self.store)


class Train(RDF):
    def __init__(self, stationId, stationLat, stationLong, stationGeometry, route, title,
           stationBusinessType, stationPublisher, trainId, trainWkt, stationGUID):

        RDF.__init__(self)
        self.stationId=stationId
        self.stationLat=stationLat
        self.stationLong=stationLong
        self.stationGeometry=stationGeometry
        self.route=route
        self.title=title
        self.stationBusinessType=stationBusinessType
        self.stationPublisher=stationPublisher
        self.trainId=trainId
        self.trainWkt=trainWkt
        self.stationGUID=stationGUID

        self.store = plugin.get('IOMemory', Store)()
        self.g = Graph(self.store)


    def bindingPrefixes(self): #+TICKED
        for key in prefixes:
            self.g.bind(key, prefixes[key])

    #this creates a url of a single train station with the test id
    def createTrainStation(self):
        singleStation = URIRef("http://data.linkedevents.org/transit/London/station/" + Literal(self.title))
        return singleStation

    def createTransitRoute(self):
        transitRoute = URIRef("http://data.linkedevents.org/transit/London/railwayRoute/%s") % self.route.replace(" ", "-").lower()
        return transitRoute

    def createLine(self):
        stationId = URIRef('http://data.linkedevents.org/transit/London/trainLine/' + self.stationId)
        return stationId

    def createRoute(self):
        route = URIRef('http://data.linkedevents.org/transit/London/route/' + self.route)
        return route

    def createTrainGraph(self):
        singleStation = self.createTrainStation() #"http://data.linkedevents.org/transit/London/station/" + Literal(stationTitle)
        transitRoute =  self.createTransitRoute()
        singleGeometry= URIRef("http://data.linkedevents.org/location/" + "%s" + "/geometry") % self.title
        #singleGeometry = createGeometry(arg[5]) #"http://data.linkedevents.org/location/" + Literal(stationId) + "/geometry"

        self.g.add(singleStation, self.rdf.type, self.naptan.RailwayStation)
        self.g.add(singleStation, self.rdf.type, self.dul.Place)
        self.g.add(singleStation, self.rdf.type, self.transit.Stop)
        self.g.add(singleStation, self.dc.identifier, Literal(self.stationId))
        self.g.add(singleStation, self.rdfs.label, Literal(self.title)) #g.add((singleStation, rdfs.label, arg[3]))

        self.g.add(singleGeometry, self.rdf.type, geo.Point)
        self.g.add(singleGeometry, self.geo.lat, Literal(self.stationLat, datatype=xsd.double))
        self.g.add(singleGeometry, self.geo.long, Literal(self.stationLong, datatype=xsd.double))
        self.g.add(singleGeometry, self.locn.geometry, Literal(self.stationGeometry, datatype=geosparql.wktLiteral))
        self.g.add(singleStation, self.transit.route, transitRoute)
        self.g.add(singleStation, self.schema.name, Literal(self.route))#NEW
        self.g.add(singleStation, self.geo.location, Literal(singleGeometry))#g.add((singleStation, schema.location, singleAddress))
        self.g.add(singleStation, self.dc.publisher, Literal(self.stationPublisher))
        self.g.add(singleStation, self.locationOnt.businessType, Literal(self.stationBuinessType))

        #TRAIN LINES GRAPH

        singleLine=self.createLine()

        self.g.add(singleLine, self.rdf.type, self.transit.RailRoute) #trainroute to trainroute
        self.g.add(singleLine, self.transit.route, createRoute(self.route))
        self.g.add(createTransitRoute(self.route), schema.name, Literal(self.title))

        return self.g


stationId=['0000','1001', '2002', '3003', '4004']
stationLat=['-0.0001',' -0.10001', '-0.20002', '-0.3003', '-0.4004']
stationLong=['0.0001', '0.10001', '0.20002', '0.3003', '0.4004']
stationGeometry=[]
route=['route0', 'route1', 'route2', 'route3', 'route4']
title=['stationA', 'stationB', 'stationC', 'stationD', 'stationE']
stationBusinessType=URIRef('http://data.linkedevents.org/kos/3cixty/trainstation')
stationPublisher=URIRef('https://tfl.gov.uk/modes/trains/')
trainWkt=['POINT(-0.001 0.001)', 'POINT(-0.002 0.002)', 'POINT(-0.003 0.003)', 'POINT(-0.004 0.004)', 'POINT(-0.005 0.005)']
stationGUID=['0000X', '1001X', '2002X', '3003X', '4004X']

trainStation = ['0000','-0.0001','0.0001','X','route0' ,'stationA' , 'URI', 'URI', '0', 'POINT(-0.001 0.001)', '0000X']
#print createTrainGraph(trainStation).serialize(format='turtle')
print Train('0000','-0.0001','0.0001','X','route0' ,'stationA' , 'URI', 'URI', '0', 'POINT(-0.001 0.001)', '0000X')
print stationId[0], stationLat[0]
