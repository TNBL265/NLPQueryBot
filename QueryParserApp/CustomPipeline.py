"""
Creating custom pipeline that can parse custom entities
"""
import spacy
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher, Matcher
import inflect
import os

class Pipeline(object):
    def __init__(self):	
        nlp = spacy.load("en_core_web_sm")
        self.nlp = self.pipeline(nlp)

    def pipeline(self, nlp):
        compound_ls = []; simple_ls = []
        with open("./QueryParserApp/content/compound_keywords.txt", "r", encoding="ISO-8859-1") as f:
            keyterms = f.readlines()
            keyterms = self.clean_keyterms(keyterms)
            compound_ls.extend(keyterms)
        with open("./QueryParserApp/content/simple_keywords.txt", "r", encoding="ISO-8859-1") as f:
            keyterms = f.readlines()
            keyterms = self.clean_keyterms(keyterms)
            simple_ls.extend(keyterms)
        # Adding plural form to the list
        simple_ls = self.singular_to_both(simple_ls);

        entity_matcher = CompoundEntityMatcher(nlp, compound_ls, 'Compound_Keynouns')
        nlp.add_pipe(entity_matcher, before='ner')    

        entity_matcher = SimpleEntityMatcher(nlp, simple_ls, 'Simple_Keynouns')
        nlp.add_pipe(entity_matcher, after='ner')        
        return nlp

    def clean_keyterms(self, keyterms):
        """
        Clean up all the keyterms from the .txt file (removing "\n")
        """
        cleaned_keyterms = []
        for keyterm in keyterms:
            # remove trailing char
            keyterm = keyterm.rstrip()
            cleaned_keyterms.append(keyterm)
        return cleaned_keyterms

    def singular_to_both(self, phrase_list):
        '''
        INPUT: a singular phrase list
        OUTPUT: a phrase list contains both singular and plural forms
        '''
        p = inflect.engine()
        plural_list = []
        for phrase in phrase_list:
            plural = p.plural(phrase)
            plural_list.append(plural)
        phrase_list += plural_list
        return phrase_list

# Ref (to build custom pipe): https://support.prodi.gy/t/adding-a-custom-ner-to-a-pipeline-overrides-an-original-ner/837

## First custom matcher will look for compound keynouns.
## It will be added before NER but won't overwrite any previously defined ents from the built-in NER
## Second custom matcher will look for simple keynouns.
## If the ents are already defined from previous pipes, we won't mark it as an ents here a gain.
## So we will need to add if after NER (last in our pipeline)
## E.g: the phrase "stock market" should have been parsed as an ent. We won't mark "stock" as another ent

class CompoundEntityMatcher(object):
    '''
    This custom matcher will be added before 'ner' in our pipeline.
    It will find "Financial-related" entities from our compound_list.
    '''
    name = 'compound_keynouns'

    def __init__(self, nlp, terms, label):
        patterns = [nlp.make_doc(term) for term in terms]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add(label, None, *patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        spans = []
        for label, start, end in matches:
            span = Span(doc, start, end, label=label)
            spans.append(span)
        doc.ents = list(doc.ents) + spans
        return doc

class SimpleEntityMatcher(object):
    '''
    This custom matcher will be added after 'ner' in our pipeline.
    It will find "Financial-related" entities from our simple_list.
    '''
    name = 'simple_keynouns'

    def __init__(self, nlp, terms, label):
        patterns = [nlp.make_doc(term) for term in terms]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add(label, None, *patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        spans = []
        for label, start, end in matches:
            span = Span(doc, start, end, label=label)
            
            # We don't want to set the entities previously defined by 'compound_fin_keynouns' or 'ner' again
            duplicate = False
            ## If already defined, we will set flag == True
            for ent in doc.ents:
                if (str(span) in str(ent) and ent.start <= span.end <= ent.end):
                    duplicate = True
                    
            ## If flag == False (no duplicate), add it to our entities list.
            if duplicate == False:
                spans.append(span)
        doc.ents = list(doc.ents) + spans
        return doc