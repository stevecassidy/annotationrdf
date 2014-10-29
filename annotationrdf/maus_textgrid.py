from rdflib import Namespace, Graph, Literal, XSD, URIRef

from annotation import AnnotationCollection, SecondAnnotation
from namespaces import MAUS

from textgrid import TextGrid


def maus_annotations(tgfile, corpusid, itemid):
    """Read annotations from a MAUS generated TextGrid file and generate a collection
    of annotation objects"""
    
    collection = AnnotationCollection([], corpusid, itemid, SecondAnnotation)
    
    tiers = {'MAU': MAUS.phonetic,
             'ORT': MAUS.orthographic,
             'KAN': MAUS.canonical,
             }
             
    tg = TextGrid.load(tgfile)
        
    for i, tier in enumerate(tg):
        # generate annotations for this tier
        
        last = None
        for row in tier.simple_transcript:
            (start, end, label) = row
            if label == "":
                label = "#"
                
            ann = collection.add_annotation(tiers[tier.tier_name()], label, start, end)
            if last != None:
                last.set_next(ann)
            last = ann

    collection.link_children(tiers['ORT'], tiers['KAN'])
    collection.link_children(tiers['ORT'], tiers['MAU'])    

    return collection

    
if __name__=='__main__':
    
    import sys
    
    tf = sys.argv[1]
    
    corpusid = URIRef("http://example.org/corpora/corpus99")
    itemid = URIRef("http://example.org/corpora/corpus99/item123")
    
    collection = maus_annotations(tf, corpusid, itemid)

    graph = collection.to_rdf()
    
    print graph.serialize(format='turtle')
    