from django.shortcuts import render
from django.http import HttpResponse
from .forms import NLPQueryForm
from KnowledgeGraphApp.KGbuild import KnowledgeGraph 
from QueryParserApp.KeywordsParser import Parser
from QueryParserApp.CustomPipeline import Pipeline
import os

class results_data(object):
    """
    Information that need to be stored when changing from MainPage to ResultsPage
    """
    def __init__(self, subtopic, triples_ls, ents_set, rels_set):
        self.db_file = "NLPQueryApp/database/data.json"
        self.subtopic = subtopic
        self.triples_ls = triples_ls
        self.ents_set = ents_set
        self.rels_set = rels_set
    
    def update(self, subtopic, triples_ls, ents_set, rels_set):
        self.subtopic = subtopic
        self.triples_ls = triples_ls
        self.ents_set = ents_set
        self.rels_set = rels_set

my_results = results_data(None, None, None, None)
print("Step 1: Building Custom Spacy Pipeline...\n")
custom_pipe = Pipeline()

def homepage(request):
    return render(request, 'home.html')

def contactpage(request):
    return render(request, 'contacts.html')

def home(request):
    """
    HomePage
    """
    # If Submit button is Clicked, get form data
    if request.method == 'POST':
        if 'home_question_sub' in request.POST:
            form = NLPQueryForm(request.POST)
            question = form['question'].value()
            subtopic = form['subtopic'].value()
            #declaration of empty document incase no Doc were parsed
            document = bytearray()
            if 'document' in request.FILES:
                    document = request.FILES['document'].read()
            document = document.decode("utf-8")

            # Parsing question
            print("\nStep 2: Parsing your Question...")
            qu = Parser(question, custom_pipe)
            ents_set, rels_set = qu.questionParse()

            # Parsing document
            print("Step 3: Parsing your Document...")
            file = Parser(document, custom_pipe)
            triples_ls = file.docParse()

            my_results.update(subtopic, triples_ls, ents_set, rels_set)
            return results(request, my_results.subtopic, my_results.triples_ls, 
                my_results.ents_set, my_results.rels_set, custom_pipe)

        else:
            return results(request, my_results.subtopic, my_results.triples_ls,
                my_results.ents_set, my_results.rels_set, custom_pipe)

    form = NLPQueryForm()
    #renders html code from templates folder
    return render(request, 'home.html', {'form': form})

def results(request,subtopic,triples_ls,ents_set, rels_set, custom_pipe):
    """
    ResultsPage
    """
    if request.method == 'POST':
        form = NLPQueryForm(request.POST)
        # cwd = os.getcwd()
        # print("cwd:",cwd)
        KG = KnowledgeGraph(my_results.db_file, my_results.subtopic, my_results.triples_ls)

        # 2nd run onwards (if a new question is being asked in the Results page)
        if 'results_question_sub' in request.POST:
            question = form['question'].value()
            
            print("\nParsing new Questions...")
            qu = Parser(question, custom_pipe)
            ents_set, rels_set = qu.questionParse()
            entities = ', '.join(str(s) for s in ents_set)
            relations = ', '.join(str(s) for s in rels_set)

            print("Replotting Graphs\n")
            KG.KGdraw(ents_set, rels_set) 
            main_html_str = KG.main_html_str
            return render(request, 'results.html', {'main_html_str': main_html_str, 
                'entities': entities, 'relations': relations})
        
        # 1st run: from Home page to Results page
        else:
            entities = ', '.join(str(s) for s in my_results.ents_set)
            relations = ', '.join(str(s) for s in my_results.rels_set)

            print("Step 4: Returning results. Graph plotting.\n")
            KG.KGdraw(my_results.ents_set, my_results.rels_set)
            main_html_str = KG.main_html_str
            return render(request, 'results.html', {'main_html_str': main_html_str,
                'entities': entities, 'relations': relations})