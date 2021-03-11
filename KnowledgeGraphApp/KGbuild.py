"""
Build and Draw KG based on both users' Document and our Database
"""
import json
import os
import networkx as nx
import matplotlib.pyplot as plt
import mpld3
mpld3.enable_notebook
from copy import deepcopy

class KnowledgeGraph(object):
    def __init__(self, db_file, subtopic, triples_ls):
        """
        INPUT: db_file is the json file that store our whole database
               triples_ls is the list of triple parsed from users' document
               subtopic is the subtopic for the Database (currently defualt for Finance)
        """
        self.db_file = db_file
        self.subtopic = subtopic
        self.triples_ls = triples_ls
        # a html string so we can easily reload the webpage and change the html paragraph for new KG
        self.main_html_str = ""
        
    def KGsave(self, subtopic):
        """
        Add triples_ls (from users' documents) into our DB if allowed
        """
        self.json_store(self.triples_ls, subtopic, self.db_file)
        os.remove("private_db")

    def KGdelete(self, subtopic):
        """
        Delete the temporary json file from the user used to draw KG
        """
        os.remove("private_db")

    def KGdraw(self, ents_set, rels_set):
        """
        From the ents_set and rels_set parsed from the question, 
        draw KG based on 1. users' doc and 2. our db
        """
        # Find sub list of triples_ls from users doc based on ents_set and rels_set
        ents_ls = list(ents_set)
        plt.rcParams['figure.figsize'] = [8,12]
        plt.rcParams['figure.dpi'] = 100
        fig = plt.figure()
        # From the document
        self.json_store(self.triples_ls, self.subtopic, "private_db")
        with open("private_db") as f:
            priv_data = json.load(f)
        t1, t2, t3, t4 = self.find_triples(priv_data, self.subtopic, ents_ls, rels_set)
        # Sub_list1: perfect match to query
        # plt.subplot(3, 2, 1)
        title1 = "Perfect Match from your Doc"
        self.printGraph(t1, fig, 321, title1, self.main_html_str)
        # Sub_list2: different relations from query
        #plt.subplot(3, 2, 2)
        title2 = "Both similar Entities from your Doc"
        self.printGraph(t2, fig, 322, title2, self.main_html_str)
        # Sub_list3: only ent1 match
        #plt.subplot(3, 2, 3)
        title3 = f"Entity '{ents_ls[0]}' from your doc"
        self.printGraph(t3, fig, 323, title3, self.main_html_str)
        # Sub_list4: only ent2 match
        #plt.subplot(3, 2, 4)
        title4 = f"Entity '{ents_ls[-1]}' from your doc"
        self.printGraph(t4, fig, 324, title4, self.main_html_str)

        # From database
        with open(self.db_file) as f:
            main_data = json.load(f)

        t5, t6, t7, t8 = self.find_triples(main_data, self.subtopic, ents_ls, rels_set)

        # Sub_list5: perfect match to query
        #plt.subplot(3, 2, 5)
        title5 = "Perfect Match from our Database"
        self.printGraph(t5, fig, 325, title5, self.main_html_str)
        # Sub_list6: different relations from query
        #plt.subplot(3, 2, 6)
        title6 = "Partial Match from our Database"
        self.printGraph(t6, fig, 326, title6, self.main_html_str)

        # plt.axis('off')
        # plt.show()
        self.KGdelete(self.subtopic)


    def json_store(self, triples_ls, subtopic, filename):
        """
        INPUT: triples_ls is the list of triple parsed from users' document
               subtopic is the name of the database to be queried (currently only support Finance)
               db_file is the json file that store our whole database
        OUTPUT: continue to write onto existing DB db_file
        """
        # open json file, if no then create 1.
        try:
            with open(db_file) as f:
                data = json.load(f)
        except:
            data = {}
        # storing fist key according to the wiki name
        data[subtopic] = {}

        # iterate through triple to find instance where same entities share multiple relations
        # find counter value (number of triples_ls already stored):
        if not data[subtopic]:
            cnt = 0
        else:
            cnt = len(data[subtopic])

        for triple in triples_ls:
            obj_flag = False; subj_flag = False; verb_flag = False

            # if the dictionary is still empty, just add
            if not data[subtopic]:
                name = 'triple' + str(cnt)
                data[subtopic].update({name : {
                                                'subject': triple[0],
                                                'relations': [triple[1]],
                                                'object': triple[2]
                                            }})
                cnt += 1
                continue
            else:
                for name, triple_dict in data[subtopic].items():
                    # iterate throught triple_dict of subject, relations, object
                    for k, v in triple_dict.items():
                        if k == 'subject' and triple[0] == v:
                            subj_flag = True
                        if k == 'object' and triple[2] == v:
                            obj_flag = True
                        if k == 'relations' and triple[1] in v:
                            verb_flag = True
                    if subj_flag == True and obj_flag == True:
                        curr_name = name
                        break
                    else:
                        subj_flag = False
                        obj_flag = False

            if subj_flag == True and obj_flag == True and verb_flag == False:
                data[subtopic][curr_name]['relations'].append(triple[1])
            elif subj_flag == True and obj_flag == True and verb_flag == True:
                continue
            # else no duplication at all
            else:
                name = 'triple' + str(cnt)
                data[subtopic].update({name : {
                                                'subject': triple[0],
                                                'relations': [triple[1]],
                                                'object': triple[2]
                                            }})
                cnt += 1
        with open(filename, 'w+') as outfile:
            json.dump(data, outfile)

    def find_triples(self, data, subtopic, ents_ls, rel_set):
        """
        Find matching triples from the users' Questions vs their Document or our Database
        There will be 4 cases as shown below.
        INPUT: data is the database to compare, it can be our DB 
                or the temporary DB we create from the users' Doc
               subtopic is the chosen DB to compare with (defualt as "Finance")
               ents_ls is the list of entities from the users' Questions
               rels_set is the set of relations from the users' Questions
        """
        t1,t2,t3,t4 = [],[],[],[]
        for triple in data[subtopic]:
            subj = data[subtopic][triple]['subject']
            obj = data[subtopic][triple]['object']
            rels_ls = data[subtopic][triple]['relations']
            # scenario 1 (t1) : a list of perfect match: ent1 and ent2 in ents_ls AND rel in rel_set
            if ((subj == ents_ls[0] and obj == ents_ls[-1]) or 
                (obj == ents_ls[0] and subj == ents_ls[-1])) and \
                any(item in rels_ls for item in list(rel_set)):
                    for triple_rel in rels_ls:
                        for set_rel in rel_set:
                            if set_rel in triple_rel:
                                new_triple = deepcopy(data[subtopic][triple])
                                new_triple["relations"] = triple_rel
                                triple_set = (new_triple['subject'], new_triple["relations"], new_triple["object"])
                                t1.append(triple_set)
            # scenario 2 (t2) : 2 entities match, different relations: ent1 and ent2 in ents_ls AND rel not in rel_set
            elif ((subj == ents_ls[0] and obj == ents_ls[-1]) or 
                (obj == ents_ls[0] and subj == ents_ls[-1])):
                for triple_rel in rels_ls:
                    new_triple = deepcopy(data[subtopic][triple])
                    new_triple["relations"] = triple_rel
                    triple_set = (new_triple['subject'], new_triple["relations"], new_triple["object"])
                    t2.append(triple_set)
            # scenario 3 (t3) : only ent1 can be found as subject
            elif subj == ents_ls[0]:
                for triple_rel in rels_ls:
                    new_triple = deepcopy(data[subtopic][triple])
                    new_triple["relations"] = triple_rel
                    triple_set = (new_triple['subject'], new_triple["relations"], new_triple["object"])
                    t3.append(triple_set)
            # scenario 4 (t4) : only ent2 can be found as subject
            elif subj == ents_ls[-1]:
                for triple_rel in rels_ls:
                    new_triple = deepcopy(data[subtopic][triple])
                    new_triple["relations"] = triple_rel
                    triple_set = (new_triple['subject'], new_triple["relations"], new_triple["object"])
                    t4.append(triple_set)
        return t1,t2,t3,t4

    def printGraph(self, triples_ls, fig, subplot_pos, title, _main_html_str):
        '''
        Display KG from list of triple
        '''
        G = nx.MultiDiGraph()
        color_map = []
        cap = 3

        # If not match found, display "No Mathc Found"
        if not triples_ls:
            pos = nx.circular_layout(G)
            ax = fig.add_subplot(subplot_pos)
            ax.set_title(title, fontsize=20)
            plt.text(0.5, 0.5, 'No Match Found', fontsize = 12, color='red',
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
            plt.axis('off')
        # draw node and edges for KG
        else:
            verb_cnt = 0;
            for triple in triples_ls:
                if verb_cnt == cap:
                    break
                subj = triple[0]
                verb = triple[1]
                obj = triple[2]
            
                if subj not in G:
                    G.add_node(subj)
                    color_map.append('blue')
                if verb not in G and verb_cnt < cap:
                    G.add_node(verb)
                    color_map.append('red')
                    verb_cnt += 1
                if obj not in G:
                    G.add_node(obj)
                    color_map.append('blue')

                G.add_edge(subj, verb)
                G.add_edge(verb, obj)   
            pos = nx.circular_layout(G)
            ax = fig.add_subplot(subplot_pos)

            nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
                    node_size=200, node_color=color_map, alpha=0.9,
                    labels={node: node for node in G.nodes()})
            ax.set_title(title, fontsize=20)
            plt.axis('off')

        # Resizing
        scale_factor = 1.5

        xmin, xmax = plt.xlim()
        ymin, ymax = plt.ylim()

        plt.xlim(xmin * scale_factor, xmax * scale_factor)
        plt.ylim(ymin * scale_factor, ymax * scale_factor)

        # An html string to easily update our ResultsPage 
        html_str = mpld3.fig_to_html(fig)
        self.main_html_str = html_str