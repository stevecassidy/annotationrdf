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

class TestTextGrid(unittest.TestCase):

    def setUp(self):
        pass
        
        
        
    def test_maus_textgrid(self):
        """Test reading a maus textgrid file"""
        
        tf = "tests/S1219s1.TextGrid"
        
        corpusid = URIRef("http://example.org/corpora/corpus99")
        itemid = URIRef("http://example.org/corpora/corpus99/item123")
    
        collection = annotationrdf.maus_annotations(tf, corpusid, itemid)

        graph = collection.to_rdf()
        
        