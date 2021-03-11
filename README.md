# NLPQueryBot
## 1. Description
- A web application that can answer simple Questions `Qu` regarding relationships between two *objects*.
- `Qu` from users using *Natural Language Processing (NLP)*. Different from the ordinary Google searches, our answers won't be simply based on online articles and information. Instead, the answers will largely depend on the information from the document - `Doc` the user uploaded. This means, the main use of our `NLPQueryBot` is to verify the information from your `Doc`, i.e. if you have a very long `Doc` and don't have time to read everything, you can upload your `Doc` and ask `Qu` to verify the information inside your `Doc`. 
- This is different from a simple `Ctrl + F` search since our `NLPQueryBot` will make use of the latest *NLP* parser to quickly identify the *relationships* as well as *information* related to the *objects* from your `Qu` so you don't have to read the whole thing on your own. 
- We will then use both the information from your `Doc` and our Database - `DB` to draw a Knowledge Graph - `KG` so you can easily comprehend the *relationships* among the *keywords* from your `Qu`. Our `DB` is built on the topic of **Finance** after web-scraping 30
- Currently, our `NLPQueryBot` is only able to parse simple sentences from your `Doc` and return simple *Subject-Verb-Object (SVO)* relationships. These *SVO* triples will be used to draw the `KG`.
- We are using the [spaCy](https://spacy.io/) library to build a `Custom Pipeline` for parsing of `Qu` and `Doc`. Our `KG` is drawn using [NetworkX](https://networkx.org/). The [mpld3](https://mpld3.github.io/) library is then used to render our `KG` on the local website hosted using [Django](https://www.djangoproject.com/).
- Overall, our `NLPQueryBot` only require 4 main steps to run:
    - **Step 1**: Building `Custom Pipeline` (This pipeline will only need to be built once as you start the `NLPQueryBot`)
    - **Step 2**: Parsing your `Qu`
    - **Step 3**: Parsing your `Doc`
    - **Step 4**: Returning results and plotting `KG` 
    
## 2. Collaborators and Timeline
- We are a group of SUTDents working on a self-initiated project for the [Digital Desgin and Development Club (3DC)](https://3dc.opensutd.org/) in SUTD:
    - **Project Manager**: Tran Nguyen Bao Long [@TNBL265](https://github.com/TNBL265)
    - **Full-stack Dev**: Joe Baarath S/O Sellathurai [@kingbaarath](https://github.com/kingbaarath)
    - **Front-end Design**: Jodi Wu Wenjiang [@jodiwu](https://github.com/jodiwu)
    - **Back-end Devs**: Michael Chun Kai Peng [@mckp0](https://github.com/mckp0) *&&* Han Wei Guang [@64hann](https://github.com/64hann)
- The full detailed timeline of how we have been working on this project can be found [here](https://hackmd.io/@TNBL265/ByeKqthHP).

## 3. Project Structure
- We adopt the general structure of a *Django* project. Our main application is located inside `NLPQueryApp` folder as indicated by the file `admin.py`. Within this folder, inside `views.py` is where we put all the main functions to be used for our `NLPQueryBot`. 
- To parse `Qu` and `Doc`, we use the functions inside [KeywordsParser.py](QueryParserApp/KeywordsParser.py) from `QueryParserApp` folder  after building the `Custom Pipeline` using [CustomPipeline.py](QueryParserApp/CustomPipeline.py) from `QueryParserApp` folder.
*&&* to draw `KG` we use the functions inside [KGbuild.py](KnowledgeGraphApp/KGbuild.py) from `KnowledgeGraphApp` folder 
- Our `Custom Pipeline` was built to detect *Finance-related* keywords. We collect simple keywords (1 word) and compound keywords (>= 2 words) from the [Investopedia Financial Term Dictionary](https://www.investopedia.com/financial-term-dictionary-4769738) and stored them in [simple_keywords.txt](QueryParserApp/content/simple_keywords.txt) and [compound_keywords.txt](QueryParserApp/content/compound_keywords.txt) respectively. (Both are from `QueryParserApp/content` folder.)
- Our `DB` is a *json* file located at `NLPQueryApp/database`.
- Our *HTML* and *CSS* files are located inside `NLPQueryApp/static` and `NLPQueryApp/templates` respectively.
```
NLPQueryBot
│   .gitignore.txt
│   db.sqlite3
│   manage.py
│   README.md
│   requirements.txt
│
└───Example_inputs 
│   │   Stocks.txt
│   │   Qus_ls.txt
│
└───KnowledgeGraphApp
│   │   _init_.py
│   │   apps.py
│   │   KGbuild.py     
│   
└───NLPQueryApp
│   │   _inti_.py  
│   │   admin.py
│   │   apps.py
│   │   forms.py
│   │   urls.py
│   │   views.py
│   │   
│   └───database
│   │   │   data.json
│   │
│   └───static
│   │   │   querybot.css
│   │   │   
│   │   └───images
│   │       │   upload-docs-green.png
│   │
│   └───templates
│   │   │    base.html
│   │   │    home.html
│   │   │    results.html
│   │
└───QueryParserApp
│   │   _init_.py
│   │   apps.py
│   │   CustomPipeline.py   
│   │   KeywordsParser.py 
│   │   
│   └───content
│   │   │   _init.py
│   │   │   compound_keywords.txt
│   │   │   simple_keywords.txt
│   │
└───Web
│   │   _init_.py
│   │   asgi.py
│   │   apps.py
│   │   settings.py
│   │   urls.py
│   │   wsgi.py
```
## 4. Usage
- Clone this repository.
- Create a virtual environemnt and install files listed in [requirements.txt](). In fact, you only need the 6 libraries/packages below as the rest will be installed along (as complementary packages) so you can run `pip install` manually:
    - 1. `pip install django==2.2`
    - 2. `pip install spacy==2.3.2`
    - 3. `python -m spacy download en_core_web_sm`
    - 4. `pip install inflect==5.3.0`
    - 5. `pip install networkx==2.5`
    - 6. `pip install mpld3==0.5.2`
- Go to the folder `QueryBot` and run `python manage.py runserver`
- Open the link shown in the console below:<br>
![](https://i.imgur.com/JHibbk3.png)
(As you can see from the console, the `Custom Pipeline` has already been initialized before launching our website.)
- You will be welcomed with a *HomePage* like the one below where you can start uploading your `Doc` and ask `Qus` (A question should contain a subject, a verb and an object so our `QueryBot` can try to find the related *relationships* from your `Doc`). A sample `Doc` can be found at [Example_inputs/Stock.txt]() (It is simply the content of the ['Stock' Wiki page](https://en.wikipedia.org/wiki/Stock)) and some sample `Qus` can be found at [Example_inputs/Qus_ls.txt]().
- As you click the *Submit* button, you will be redirected to the *ResultsPage*.
- At the top of the *ResultsPage*, our `QueryBot` allowed you to ask another questions (the *ResultsPage* will simply reload to show the new results): 
- Right below is a small paragraph showing the `Entities` and `Relations` we found from your `Qus`. These `Entities` and `Relations` will be grouped into *SVO* triples to be used to draw the `KG` below.
- At the bottom of the *ResultsPage*, our `KG` can be seen in 6 sections:
    - ***Perfect Match from your Doc:*** the exact`Entities` and `Relations` from your `Qus` can be found in your `Doc`.
    - ***Both similar Entities from your Doc:*** only `Entities` from your `Qus` is similar to those in your `Doc`. The `Relations` can vary.
    - ***Entity {subject} from your Doc:*** only the *Entity 1* from your `Qus` can be found as a *Subject* in your `Doc`.
    - ***Entity {object} from your Doc:*** only the *Entity 2* from your `Qus` can be found as an *Object* in your `Doc`.
    - ***Perfect Match form our Database:*** both the `Entities` and `Relations` from your `Qus` can be found inside our `DB`.
    - ***Partial Match from our Database:*** only the `Entities` from your `Qus` can be found in the `DB`. The `Relations` can vary.
- If you take a look at the console, as our `QueryBot` run, we will be printing out the process that our `QueryBot` is at: <br>
![](https://i.imgur.com/ufjBogE.png)
- And if you ask a `Qus` again while in the *ResultsPage*, this will be the console messages:<br>
![](https://i.imgur.com/jTkEQy0.png)

## 5. Future Work
- Host our application online using [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/).
- Use *Django* built-in database *MySQL* to store our data instead of using a json file.
- Optimize the searching algorithm wrt *MySQL*.
- Add more databases on other topics such as: Sports or Cuisine...
- Add Custom Pipelines that can parse *complex and complicated sentences* to find more high level information.