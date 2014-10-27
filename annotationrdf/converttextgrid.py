from annotation import SecondAnnotation
from textgrid import TextGrid


def textgrid_annotations(tgfile):
    """Read annotations from a TextGrid file and generate a collection
    of annotation objects"""
    
    # dictionary of tier domination pairs: key dominates childtier[key]
    childtier = {'ORT': 'KAN',
                 'KAN': 'MAU',}
    
    
    anns = []
     
    tg = TextGrid.load(tgfile)
    
    print "TIERS: ", tg.tiers
    
    for i, tier in enumerate(tg):
        # generate annotations for this tier
        
        for row in tier.simple_transcript:
            (start, end, label) = row
            if label == "":
                label = "#"
            ann = SecondAnnotation(tier.nameid, label, start, end)
            print tier.nameid, label, start, end
            
            # can we find any annotation starting at the same time
            for oa in anns:
                if oa.start == ann.start:
                    print "\tSAME START", oa
                elif oa.end == ann.end:
                    print "\tSAME END", oa
        
            anns.append(ann)
        
        
        
    return anns

    
if __name__=='__main__':
    
    import sys
    
    tf = sys.argv[1]
    anns = textgrid_annotations(tf)
    
    for ann in anns:
        print ann