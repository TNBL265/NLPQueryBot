"""
Create Parser object that can Parse Question and Document
"""
import spacy
from spacy.tokens import Span
from spacy.matcher import PhraseMatcher, Matcher
import inflect
import re

class Parser(object):
    def __init__(self, text, custom_pipe):
        self.text = text
        self.nlp = custom_pipe.nlp

    def docParse(self):
        """
        To parse the whole documents but only for simple sentences at the moment.
        Return a list of triples of Subject-Verb-Object (SVO)
        """
        text = self.text
        text = self.simplify(text)
        nlp = self.nlp
        full_doc = nlp(text)
        
        # Slit into sentences and find Simple sentences
        sent_doc_ls = list(sent for sent in full_doc.sents)
        spl_ls = self.simple_find(sent_doc_ls)
        doc_ls = list(nlp.pipe(spl_ls))

        print("Finding triples (Subject-Verb-Object) from your doc...\n")
        # Our triples will be (ent1, rel, ent2)
        triples = self.all_triples(doc_ls)  
        return triples

    def questionParse(self):
        """
        To parse question only. 
        Return a set of entities ents_set and a set of relations rels_set
        """
        text = self.text
        text = text.lower()
        nlp = self.nlp
        doc = nlp(text)
        print("Finding entities set and relations set...\n")
        ents_set = set(str(ent) for ent in doc.ents)
        rels_list = self.get_relation(doc)
        rels_set = set(str(rel[-1]) for rel in rels_list)
        return ents_set, rels_set

    def get_relation(self, doc):
        """
        Parsing a doc object to find the Relations ("key verbs")
        Return a set of relations rels_set (<start_index>, <relation_name>)
        """
        nlp = self.nlp
        # Matcher class object 
        matcher = Matcher(nlp.vocab)

        #define the pattern (both patterns will be looking for a VERB followed by a PREPOSITION)
        ROOT_pattern = [{'DEP':'ROOT'}, 
                {'DEP':'prep','OP':"?"},
                {'DEP':'agent','OP':"?"},
                {'DEP':'acomp','OP':"?"},
        ] 

        acl_pattern = [{'DEP':'acl'}, 
                {'DEP':'prep','OP':"?"},
                {'DEP':'agent','OP':"?"},
                {'DEP':'acomp','OP':"?"},
        ]

        relations = []
        matcher.add("relations", None, ROOT_pattern, acl_pattern)
        # After the matcher is added, let's run on our Doc to see what it can find
        matches = matcher(doc)

        # Store it in the relations list
        for match_id, start, end in matches:
            matched_span = doc[start:end]
            relation_tuple = (start, matched_span.lemma_)
            relations.append(relation_tuple)

        # Check if there is duplication, we will remove the duplication
        # Examples: "determine" and "determine by" will both be relations but we only need the longer one
        for start, relation1 in relations:
            if len(relation1.split()) != 1:
                continue
            else:
                # comparing our 1st relation to our 2nd relation 
                for _, relation2 in relations:
                    # if 2nd relation also 1 word, won't be a duplicate
                    if len(relation2.split()) == 1:
                        continue
                    # if 1st relation is a substring of 2nd relation --> duplicate
                    if relation2.find(relation1) != -1:
                        relations.remove((start, relation1))
                        break
        return relations

    def simplify(self, text):
        """
        Remove all 'a', 'the' from the text since this is not important to build the KG.
        Also remove '\n' and '=' which is used to format the sub-headings
        Also turn all to lowercase.
        Also remove all texts within brackets (those adding extra information)
        Also clean up 'he she we they this these those that' since we have yet found a way to parse earlier info.
        """
        text = text.lower()
        to_replace_with_space = [' a ', ' the ', ' he ', ' she ', ' we ', ' they ', ' this ', ' that ', ' these ', ' those ']
        to_remove = ['\n', '=']
        source = text
        source = re.sub(" [\(\[].*?[\)\]]", "", source)
        source = re.sub("[=].*? [=]", "", source)
        for dummy in to_remove:
            source = source.replace(dummy, '')
        # clean up period as this punctuation get a bit messy after all the previous replacements
        n = 3
        for i in range(n):
            dummy = '.' + ' '*(n-i)
            source = source.replace(dummy, '.')
        source = source.replace('.', '. ')
        for dummy in to_replace_with_space:
            source = source.replace(dummy, ' ')
        return source
    
    def simple_find(self, doc_ls):
        """
        Only to find Simple sentences to parse.
        Currently ignore Compound and Complex sentences
        Return a list of string object for Simple sentence spl_text_ls.
        """
        spl_text_ls = []

        for doc in doc_ls:
            is_simple = False
            nsubj_tok = [tok for tok in doc if tok.dep_ == "nsubj" or tok.dep_ == "nsubjpass"]
            mark_tok = [tok for tok in doc if tok.dep_ == "mark"]; 

            if len(nsubj_tok) == 1 and len(mark_tok) == 0:
                is_simple = True

            if is_simple == True:
                spl_text_ls.append(doc.string.strip())

        return spl_text_ls

    def all_triples(self, doc_ls):
        """
        Find all triples from the document object
        Return a list of triples
        """
        triples = []
        for doc in doc_ls:
            ent_rel_list = self.ordered_entity_relation(doc)
            triple = self.find_triple(ent_rel_list)
            triples += triple     
        return triples

    def ordered_entity_relation(self, doc):
        '''
        Parse a `doc` object and return entities and the relations between them in order
        '''
        ent_list = []; relation_list = []
        for ent in doc.ents:
            ent_tuple = (ent.end - 1, ent.lemma_, "ents")
            ent_list.append(ent_tuple)

        relations = self.get_relation(doc)
        for start, relation in relations:
            relation_tuple = (start, relation, "rels")
            relation_list.append(relation_tuple)

        combined_list = ent_list + relation_list
        ordered_list = sorted(combined_list, key=lambda x: x[0])
        # check ordered list for tuple of ents follow by rels:
        # if ents.end >= rels.start, False, remove relations
        n = len(ordered_list)
        remove_list = []
        for i in range(n-1):
            tuple1 = ordered_list[i]
            tuple2 = ordered_list[i+1]
            if tuple1[-1] == 'ents' and tuple2[-1] == 'rels':
                if tuple1[0] >= tuple2[0]:
                    remove_list.append(tuple2)
        for trash in remove_list:
            ordered_list.remove(trash)
        ordered_list = sorted(ordered_list, key=lambda x: x[0])
        return ordered_list


    def find_triple(self, ent_rel_list):
        '''
        Filter only entities that have relation between them. And return a list of tuples of (ent1, rel, ent2).
        This is hardecoded and only work well for simple sentence.
        '''
        l = len(ent_rel_list)
        span = 3
        triple = []

        for i in range(l-span+1):
            ind1 = ent_rel_list[i]
            ind2 = ent_rel_list[i + 1]
            ind3 = ent_rel_list[i + 2]

            if ind1[-1] == 'ents' and ind2[-1] == 'rels' and ind3[-1] == 'ents':
                triple_tuple = (ind1[1], ind2[1], ind3[1])
                triple.append(triple_tuple)

        return triple