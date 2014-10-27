#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_annotationrdf
----------------------------------

Tests for `annotationrdf` module.
"""

import unittest
from rdflib import Namespace, Graph, Literal, XSD, URIRef

import annotationrdf
from annotationrdf.namespaces import DADA, MAUS

class TestAnnotationrdf(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_annotationcollection(self):
        """Test creation of annotation collections"""
        
        
        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")
        
        collection = annotationrdf.AnnotationCollection([], corpusid, itemid)
        
        self.assertFalse(collection.id == "")
        self.assertEqual(Namespace(itemid)["/"+collection.id], collection.uri())
        self.assertEqual(corpusid, collection.corpusID())
        


    def test_create_annotation(self):
        """Test creation of annotations"""
        
        
        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")
        
        collection = annotationrdf.AnnotationCollection([], corpusid, itemid)
        
        MAU = URIRef("http://example.org/schema/maus/phonetic")
        
        # create with no id
        ann = collection.add_annotation(MAU, 'test', 1.0, 2.0)
        
        self.assertEqual(1.0, ann.start)
        self.assertEqual(2.0, ann.end)
        self.assertEqual(['val'], ann.keys())
        
        # create with explicit id
        ann = collection.add_annotation(MAU, 'test', 1.0, 2.0, id='foobar')
        
        self.assertEqual(1.0, ann.start)
        self.assertEqual(2.0, ann.end)
        self.assertEqual(['val'], ann.keys())
        self.assertEqual('foobar', ann.id)
        self.assertEqual(Namespace(itemid)["/"+collection.id+"/annotation/foobar"], ann.uri())
        
    def test_create_annotation_properties(self):
        """Test creation of annotations with some extra properties"""


        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")

        collection = annotationrdf.AnnotationCollection([], corpusid, itemid, annotationrdf.SecondAnnotation)

        MAU = URIRef("http://example.org/schema/maus/phonetic")

        props = {'size': 'one', 'age': 21}

        ann = collection.add_annotation(MAU, 'test', 1.0, 2.0, properties=props)

        graph = Graph()

        collection.to_rdf(graph)

        # check conversion to turtle - shows up some rdf problems (e.g literal subjects)
        rdfstring = graph.serialize(format='turtle')

        #print rdfstring

    def test_annotation_next(self):
        """Test adding 'next' relation between annotations"""
        
        
        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")
        
        collection = annotationrdf.AnnotationCollection([], corpusid, itemid)
        
        MAU = URIRef("http://example.org/schema/maus/phonetic")
        
        # create with no id
        ann1 = collection.add_annotation(MAU, 'test', 1.0, 2.0)
        ann2 = collection.add_annotation(MAU, 'test', 2.0, 3.0)
        
        ann1.set_next(ann2)
        
        self.assertEqual(ann2.uri(), ann1.get_next())
        
        graph = collection.to_rdf()
        self.assertIn((ann1.uri(), DADA.next, ann2.uri()), graph)

        
    def test_annotation_child(self):
        """Test adding 'child' relation between annotations"""
        
        
        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")
        
        collection = annotationrdf.AnnotationCollection([], corpusid, itemid)
        
        MAU = URIRef("http://example.org/schema/maus/phonetic")
        
        # create with no id
        ann1 = collection.add_annotation(MAU, 'test', 1.0, 2.0)
        ann2 = collection.add_annotation(MAU, 'test', 2.0, 3.0)
        
        ann1.add_child(ann2)
        
        self.assertIn(ann2.uri(), ann1.get_children())
        
        graph = collection.to_rdf()
        self.assertIn((ann1.uri(), DADA.hasChild, ann2.uri()), graph)

    
    def test_annotation_link_children(self):
        """Test creating child relations based on times"""
        
        
        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")
        
        collection = annotationrdf.AnnotationCollection([], corpusid, itemid, annotationrdf.SecondAnnotation)
        
        MAU = MAUS.phonetic
        ORT = MAUS.orthography
        
        ort1 = collection.add_annotation(ORT, 'parent', 1.0, 3.0)
        ort2 = collection.add_annotation(ORT, 'parent1', 3.0, 5.0)
        
        ann1 = collection.add_annotation(MAU, 'c1', 1.0, 2.0) # inside parent at start
        ann2 = collection.add_annotation(MAU, 'c2', 1.5, 2.0) # inside parent at end
        ann3 = collection.add_annotation(MAU, 'cx', 0.5, 2.0) # overlaps parent
        ann4 = collection.add_annotation(MAU, 'c3', 3.0, 5.0) # covers all parent1

        collection.link_children(ORT, MAU)
        
        self.assertIn(ann2.uri(), ort1.get_children())
        
        graph = collection.to_rdf()

        self.assertIn((ort1.uri(), DADA.hasChild, ann1.uri()), graph)
        self.assertIn((ort1.uri(), DADA.hasChild, ann2.uri()), graph)
        self.assertNotIn((ort1.uri(), DADA.hasChild, ann3.uri()), graph)
        self.assertIn((ort2.uri(), DADA.hasChild, ann4.uri()), graph)
        self.assertNotIn((ort2.uri(), DADA.hasChild, ann3.uri()), graph)


    
    
    def test_create_second_annotation(self):
        """Test creation of annotations of a different type"""
        
        
        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")
        
        collection = annotationrdf.AnnotationCollection([], corpusid, itemid, annotationrdf.SecondAnnotation)
        
        MAU = URIRef("http://example.org/schema/maus/phonetic")
        
        ann = collection.add_annotation(MAU, 'test', 1.0, 2.0)
        
        self.assertTrue(isinstance(ann, annotationrdf.SecondAnnotation))
        
        
    def test_annotation_rdf(self):
        """Test generation of RDF for an annotation"""
        
        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")
        
        collection = annotationrdf.AnnotationCollection([], corpusid, itemid)
        
        MAU = URIRef("http://example.org/schema/maus/phonetic")
        itemid = URIRef("http://example.org/corpus123/item124")
        
        ann = collection.add_annotation(MAU, 'test', 1.0, 2.0)
        
        graph = Graph()
        
        collection.to_rdf(graph)
        
        # check conversion to turtle - shows up some rdf problems (e.g literal subjects)
        rdfstring = graph.serialize(format='turtle')
        self.assertIn(corpusid, rdfstring)
        
        #print rdfstring
        
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()