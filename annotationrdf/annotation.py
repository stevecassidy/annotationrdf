from UserDict import DictMixin
from uuid import uuid4
from rdflib import Namespace, Graph, Literal, XSD, URIRef
from namespaces import *

from annotation_names import NAMEMAP



class Annotation(DictMixin):
    """
    An annotation on a region of a source document with the position
    of the source region defined by start and end offsets.
    By default (this class) these are interpreted as UTF8 character
    offsets from the start of the file. Subclasses define alternate
    interpretations, eg. second times in an audio file.
    """

    uniqueid = 0

    def __init__(self, tipe, val, start, end, collection, id=None, properties=None):
        # generate an id unless we're given one
        if id:
            self.id = str(id)
        else:
            self.id = str(Annotation.uniqueid)
            Annotation.uniqueid = Annotation.uniqueid + 1

        # validate types of some parameters
        assert(isinstance(collection, AnnotationCollection))
        self.collection = collection

        assert(isinstance(tipe, URIRef))
        self.tipe = tipe

        self.start = start
        self.end = end

        # dictionary for properties
        if properties:
            self.properties = properties
        else:
            self.properties = dict()
        # val is a special property
        if val:
            self.properties['val'] = val
        else:
            self.properties['val'] = ""


    # define the dictionary interface
    def __getitem__(self, key):
        return self.properties[key]

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __delitem__(self, key):
        self.properties.__delitem__(key)

    def keys(self):
        return self.properties.keys()

    def __repr__(self):
        return (self.tipe + ': ' + self['val'] + ' ' + str(self.start) + ' -> ' + str(self.end))

    def __cmp__(self, other):
        if not isinstance(other, Annotation):
            return -1
        if (cmp(self.tipe, other.tipe) == 0):
            if (cmp(self["val"], other["val"]) == 0):
                if (cmp(self.start, other.start) == 0):
                    return cmp(self.end, other.end)
                else:
                    return cmp(self.start, other.start)
            else:
                return cmp(self["val"], other["val"])
        else:
            return cmp(self.tipe, other.tipe)

    def uri(self):
        """Return the URI for this annotation"""

        return Namespace(self.collection.uri())['/annotation/' + self.id]


    def set_next(self, ann):
        """assert that 'ann' is the next in sequence to this annotation"""

        self[DADA.next] = ann.uri()
        
        
    def get_next(self):
        """Return the next annotation in sequence if any, or None"""
        
        if self.has_key(DADA.next):
            return self[DADA.next]
        else:
            return None

    def add_child(self, ann):
        """add an annotation as the child of this one, nodes can 
        have multiple children"""

        if DADA.hasChild in self:
            self[DADA.hasChild].append(ann.uri())
        else:
            self[DADA.hasChild] = [ann.uri()]
    
    def get_children(self):
        """Return the children of this annotation or None if there is none"""
        
        if self.has_key(DADA.hasChild):
            return self[DADA.hasChild]
        else:
            return None

    def to_rdf(self, g):
        """Add triples to this rdf graph to represent this
        annotation. Nodes go into the given namespace
        and are part of the collectionUri"""

        corpusID = self.collection.corpusID()
        collectionUri = self.collection.uri()

        # some identifiers
        property_namespace = self.collection.property_namespace()

        annoturi = self.uri()

        locatoruri = URIRef(self.uri()+"L")

        # annotation
        g.add((annoturi, RDF.type, DADA.Annotation))
        g.add((annoturi, DADA.partof, collectionUri))

        # locator info depends on the type of annotation
        locatoruri = self.locator_rdf(locatoruri, g)
        g.add((annoturi, DADA.targets, locatoruri))

        g.add((annoturi, DADA.type, self.tipe))

        for key in self.keys():
            if self[key] != '':
                if isinstance(key, URIRef):
                    prop = key
                elif key == 'val':
                    prop = DADA.label
                elif key == "speakerid":
                    prop = AUSNC.speakerid
                else:
                    prop = property_namespace[key]
                
                # if we have a singleton value, make it a list
                if type(self[key]) != list:
                    values = [self[key]]
                else:
                    values = self[key]
                
                for value in values:
                    if isinstance(value, URIRef):
                        obj = value
                    else:
                        obj = Literal(unicode(value))
                
                    g.add((annoturi, prop, obj))


    def locator_rdf(self, locatoruri, graph):
        """Add RDF triples to the graph to represent the locator information
        for this annotation"""

        graph.add((locatoruri, RDF.type, DADA.TextRegion))
        graph.add((locatoruri, DADA.start, Literal(int(self.start), datatype=XSD.integer)))
        graph.add((locatoruri, DADA.end, Literal(int(self.end), datatype=XSD.integer)))

        return locatoruri


class SecondAnnotation(Annotation):
    """An annotation on a audio/video document with endpoints defined by offsets in seconds,
    defines the serialisation of the locator"""


    def locator_rdf(self, locatoruri, graph):
        """Add RDF triples to the graph to represent the locator information
        for this annotation"""


        graph.add((locatoruri, RDF.type, DADA.SecondRegion))
        graph.add((locatoruri, DADA.start, Literal(float(self.start), datatype=XSD.float)))
        graph.add((locatoruri, DADA.end, Literal(float(self.end), datatype=XSD.float)))
        return locatoruri

class HMSAnnotation(Annotation):
    """An annotation on a audio/video document with endpoints defined by offsets in HH:MM:SS
    defines the serialisation of the locator"""

    def locator_rdf(self, locatoruri, graph):
        """Add RDF triples to the graph to represent the locator information
        for this annotation"""

        graph.add((locatoruri, RDF.type, DADA.HMSRegion))
        graph.add((locatoruri, DADA.start, Literal(self.start)))
        graph.add((locatoruri, DADA.end, Literal(self.end)))
        return locatoruri



# TODO: AnnotationCollection should have metadata - at least owner, date, source, possibly PROV-O
# TODO: method to export to JSON-LD format
# TODO: method to read from JSON-LD format
class AnnotationCollection:
    """All the annotations on an item"""


    def __init__(self, annotationList, corpusid, itemid, aclass=Annotation):

        self.annotations = annotationList

        self.itemid = itemid
        self.id = str(uuid4())   # random unique identifier
        self.corpusid = corpusid
        self.aclass = aclass

    def uri(self):
        """Return an identifier URI for this annotation collection"""

        return Namespace(self.itemid)["/"+self.id]

    def corpusID(self):
        """Return the corpus identifier associated with this annotation"""

        return self.corpusid

    def property_namespace(self):
        """Return the default property namespace for this collection"""

        return Namespace('http://example.org/properties/')


    def add_annotation(self, tipe, val, start, end, id=None, properties=None):
        """Add a new annotation to this collection"""

        ann = self.aclass(tipe, val, start, end, self, id=id, properties=properties)
        self.annotations.append(ann)

        return ann

    def link_children(self, parenttier, childtier):
        """Generate links between annotations on the parent and child tiers"""
        
        parents = [a for a in self.annotations if a.tipe==parenttier]
        children =  [a for a in self.annotations if a.tipe==childtier]
        
        for parent in parents:
            for child in children:
                if child.start >= parent.start and child.end <= parent.end:
                    parent.add_child(child)


    def to_rdf(self, graph=None):
        """Add RDF for all of the annotations in the collection
        in an RDF graph"""

        if graph == None:
            graph = Graph()

        graph = bind_graph(graph)

        for a in self.annotations:
            a.to_rdf(graph)

        graph.add((self.uri(), RDF.type, DADA.AnnotationCollection))
        graph.add((self.uri(), DADA.annotates, self.itemid))

        return graph
