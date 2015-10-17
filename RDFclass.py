__author__ = 'CASA 3cixty team'

import csv
import uuid
import pyproj
from rdflib import URIRef, Literal, Namespace, plugin, Graph, ConjunctiveGraph
from rdflib.store import Store
from collections import defaultdict

class RDFclass:

    # initialise graph variable, read dictionary and bing prefixes
    def __init__(self):
        store = plugin.get('IOMemory', Store)()
        self.g=Graph(store)
        prefixes=self.readDict()
        self.bindingPrefixes(prefixes)

    def readCsv(self,inputfile):
        try:
            f=open(inputfile);
            rf=csv.reader(f,delimiter=',');
            return rf;
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
            raise

    def readDict(self):
        dict = defaultdict(list)
        with open('dictionary.csv','rb') as f:
            r = csv.DictReader(f)
            for row in r:
                for (k,v) in row.items():
                    dict[k]=v
        f.close()
        return dict

    def getUid(self,s,n):
        idencode=s.encode('utf-8')
        uid=uuid.uuid5(n, idencode)
        return uid

    def convertProj(self,lon,lat):
        Bng = pyproj.Proj(init='epsg:27700')
        Wgs84 = pyproj.Proj(init='epsg:4326')
        wgsLon,wgsLat = pyproj.transform(Bng,Wgs84,lon, lat)
        return wgsLon,wgsLat

    def writeDict(self,prefixes):
        with open('dictionary.csv','wb') as f:
            w = csv.writer(f)
            w.writerow(prefixes.keys())
            w.writerow(prefixes.values())
        f.close()

    def bindingPrefixes(self,prefixes):
        for key in prefixes:
            self.g.bind(key, prefixes[key])


    def createBusStop(self,stopId):
        singleStop = URIRef("http://data.linkedevents.org/transit/London/stop/" + stopId)
        return singleStop

    def createGeometry(self, stopsGUID):
        singleGeometry = URIRef(('http://data.linkedevents.org/location/%s/geometry') % stopsGUID)
        return singleGeometry

    def createAddress(self, stopsGUID):
        singleAddress = URIRef(('http://data.linkedevents.org/location/%s/address') % stopsGUID)
        return singleAddress

    def writeRDF(self,outputfile):
         self.g.serialize(outputfile,format='turtle')

    def creatRDF(self,row):

        nspaces=self.readDict()

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

        stopid  = row[1]
        uid=self.getUid(row[0],naptan)

        stopLat,stopLong=convertProj(row[4],row[5])
        #stopLat,stopLong=row[4],row[5]

        noAddress=""
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

        singleStop = self.createBusStop(stopid)
        singleAddress = self.createAddress(stopGUID)
        singleGeometry = self.createGeometry(stopGUID)

        self.g.add((singleStop, rdf.type, naptan.BusStop))
        self.g.add((singleStop, rdf.type, dul.Place))
        self.g.add((singleStop, rdf.type, transit.Stop))
        self.g.add((singleStop, dc.identifier, Literal(stopid)))
        self.g.add((singleStop, geom.geometry, singleGeometry))
        self.g.add((singleStop, schema.geo, singleGeometry))
        self.g.add((singleAddress, rdf.type, schema.PostalAddress))
        self.g.add((singleAddress, rdf.type, dcterms.Location))
        self.g.add((singleAddress, dcterms.title, stopTitle))
        self.g.add((singleAddress, schema.streetAddress, stopAddress))
        self.g.add((singleAddress, locn.address, stopLocnAddress))
        self.g.add((singleAddress, schema.addressLocality, stopAddressLocality))
        self.g.add((singleAddress, locn.adminUnitL12, stopAdminUnitL2))
        self.g.add((singleGeometry, rdf.type, geo.Point))
        self.g.add((singleGeometry, geo.lat, Literal(stopLat, datatype=xsd.double)))
        self.g.add((singleGeometry, geo.long, Literal(stopLong, datatype=xsd.double)))
        self.g.add((singleGeometry, locn.geometry, Literal(stopGeometry, datatype=geosparql.wktLiteral)))
        self.g.add((singleStop, geo.location, singleGeometry))
        self.g.add((singleStop, transit.route, stopRoute))
        self.g.add((singleStop, schema.location, singleAddress))
        self.g.add((singleStop, locn.address, singleAddress))
        self.g.add((singleStop, dc.publisher, stopPublisher))
        self.g.add((singleStop, locationOnt.businessType, stopBusinessType))
        self.g.add((singleStop, rdfs.label, stopLabel))
        return self.g
