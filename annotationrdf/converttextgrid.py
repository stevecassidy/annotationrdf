from rdflib import Namespace, Graph, Literal, XSD, URIRef

from annotation import AnnotationCollection, SecondAnnotation
from namespaces import DADA, MAUS

from textgrid import TextGrid


def textgrid_annotations(tgfile):
    """Read annotations from a TextGrid file and generate a collection
    of annotation objects"""
    
    # dictionary of tier domination pairs: key dominates childtier[key]
    childtier = {'ORT': 'KAN',
                 'KAN': 'MAU',}
    
    corpusid = URIRef("http://example.org/corpora/corpus99")
    itemid = URIRef("http://example.org/corpora/corpus99/item123")
    
    collection = AnnotationCollection([], corpusid, itemid, SecondAnnotation)
    
    tiers = {'MAU': URIRef("http://example.org/schema/maus/phonetic"),
             'ORT': URIRef("http://example.org/schema/maus/orthographic"),
             'KAN': URIRef("http://example.org/schema/maus/canonical"),
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
    collection.link_children(tiers['KAN'], tiers['MAU'])

    return collection

    
if __name__=='__main__':
    
    import sys
    
    tf = sys.argv[1]
    collection = textgrid_annotations(tf)

    graph = collection.to_rdf()
    
    print graph.serialize(format='turtle')
    