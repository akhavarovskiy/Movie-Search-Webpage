# JAMA
# CS 483
# Assignment 3

import csv
import sys
import json
import os
import whoosh
import shutil

from whoosh.qparser import plugins
from whoosh.index import *
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh.lang.stopwords import stoplists
from whoosh import sorting
from whoosh.scoring import Frequency,MultiWeighting,TF_IDF,BM25F

from datetime import datetime


# global variables
# our database file in CSV format (built by .py)
MOVIE_INPUT_FILE = "JAMA_Movie_DB.csv"
# MOVIE_INPUT_FILE = "JAMA_Small_DB.csv"

# ........................................................................................
# import data from CSV file into the respective tables


def index_data():

    # IF indexDir directory already exists, treat as index
    if os.path.exists("indexDir"):
        return open_dir("indexDir")
    else:
        # path doesn't exist, make dir and build index
        os.mkdir("indexDir")

    # JY, add english stopword and ngram
    # stop words are
    # {'because', 'such', 'not', 'off', 'what', 'to', 'very', 'we', 'a', 'own', 'about', 'once', 'herself', 'on', 'how', 'himself', 'by', 'have', 'your', 'his', 'themselves', 'am', 'between', 'does', 'my', 'from', 'or', 'both', 'then', 'no', 'she', 'same', 'above', 'are', 'its', 'ourselves', 'below', 'having', 'me', 'into', 'and', 'ours', 'be', 'at', 'other', 'just', 'again', 'that', 'down', 'these', 'only', 'yourselves', 'under', 'most', 'can', 'itself', 'doing', 'in', 'when', 'has', 'than', 'each',
    #     'of', 'you', 'should', 'here', 'her', 'some', 'now', 'hers', 'why', 'so', 'out', 'where', 'nor', 'our', 'don', 'an', 'been', 'over', 's', 'while', 'were', 'do', 'whom', 'their', 'had', 'is', 'until', 'yourself', 'this', 't', 'few', 'which', 'during', 'who', 'i', 'through', 'there', 'those', 'it', 'more', 'if', 'theirs', 'for', 'will', 'him', 'the', 'was', 'did', 'too', 'with', 'further', 'myself', 'they', 'all', 'yours', 'after', 'but', 'against', 'he', 'before', 'as', 'up', 'them', 'any', 'being'}
    ana = analysis.StandardAnalyzer(
        stoplist=stoplists["en"]) | analysis.NgramFilter(minsize=3, maxsize=10) #| analysis.StemmingAnalyzer()

    # define our database schema
    schema = Schema(
        imdb_id=ID(stored=True, sortable=True),
        title=TEXT(stored=True),
        year=TEXT(stored=True),
        plot=TEXT(stored=True, analyzer=ana),
        poster=ID(stored=True),  # recommend by Whoosh for URL to be ID
        runtime=NUMERIC(int, 16, decimal_places=0, stored=True,
                        signed=False, sortable=True, default=0),
        website=TEXT(stored=True),
        genre=TEXT(stored=True, sortable=True),
        director=TEXT(stored=True),
        actors=TEXT(stored=True),
        rating=TEXT(stored=True, sortable=True),
        country=TEXT(stored=True, sortable=True),
        season=TEXT(stored=True),
        episode=TEXT(stored=True),
        tomato_score=NUMERIC(int, 16, decimal_places=0,
                             signed=False, sortable=True, stored=True, default=0),
        tomato_fresh=TEXT(stored=True)
    )

    # create new index in directory
    indexer = create_in("indexDir", schema)
    index_writer = indexer.writer()  # create index writer to add docs to index

    # open database CSV file
    csvfile = open(MOVIE_INPUT_FILE, 'rt', encoding='utf-8', errors='ignore')
    rows = csv.reader(csvfile, delimiter=',')  # read rows into list
    try:
        next(rows, None)  # skip the headers

        row_count = 1  # counter to check progress

        # iterate through rows and store data
        for row in rows:
            imdb_id = row[0]
            title = row[1]
            year = row[2]
            plot = row[3]
            poster = row[4]
            runtime = row[5]
            website = row[6]
            genre = row[7]
            director = row[8]
            actors = row[9]
            rating = row[10]
            country = row[11]
            season = row[12]
            episode = row[13]
            tomato_score = row[14]
            tomato_fresh = row[15]

            row_count += 1

            # NOTE: We have decided to leave out the following format changes
            try:
                if runtime == 'N/A':
                    runtime = 0
                else:
                    runtime = runtime.replace(" min", "")
                    runtime = int(runtime)
                    # pos = runtime.find("min")
                    # if (pos != -1):
                    #     runtime=float(runtime[0,pos-1])
            except:
                runtime = 0

            try:
                if tomato_score == 'N/A':
                    tomato_score = 0
                else:
                    tomato_score = tomato_score.replace("%", "")
                    tomato_score = int(tomato_score)
                    # pos = runtime.find("%")
                    # if (pos != -1):
                    #     tomato_score=float(runtime[0,pos-1])
            except:
                tomato_score = 0

            # try:
            #     year=datetime.strptime(year, "%y")
            # except:
            #     year=datetime.strptime("1970", "%Y")

            # add document to inverted index
            index_writer.add_document(
                imdb_id=imdb_id,
                title=title,
                year=year,
                plot=plot,
                poster=poster,
                runtime=runtime,
                website=website,
                genre=genre,
                director=director,
                actors=actors,
                rating=rating,
                country=country,
                season=season,
                episode=episode,
                tomato_score=tomato_score,
                tomato_fresh=tomato_fresh
            )

            # print progress of indexing
            if row_count % 100 == 0:
                print("Processed %d/8600 records ..." % (row_count))

        # commit changes
        print("Committing index changes... this could take several minutes.")
        index_writer.commit()
        print("Processed all records.")

        return indexer

    # catch error with csv file
    except csv.Error as e:
        sys.exit('file %s, line %d: %s' %
                 (MOVIE_INPUT_FILE, csv.reader.line_num, e))
    except RuntimeError as e:
        print(e)

# .....................................................................................................


def search(ix, q):

    # JY for the sake of demonstrating ranking weight, not going to affect search much visibly.
    mw=MultiWeighting(BM25F(), imdb_id=Frequency(), plot=TF_IDF())
    with ix.searcher(weighting=mw) as searcher:
        # parse over 4 fields, with fuzzy search support
        parser = MultifieldParser(["actors", "title", "director", "genre",
                                   "plot", "tomato_score"], schema=ix.schema)
        # add fuzzy search plug-in
        # termclass=FuzzyTerm
        parser.add_plugin(plugins.FuzzyTermPlugin())
        query = parser.parse(q)  # build query
        # JY add sort by tomato_score indecending order
        facet = sorting.FieldFacet("tomato_score", reverse=True)
        results = searcher.search(query, sortedby=facet)  # search query and capture results
        # loop through results
        for r in results:
            print()
            # print(r)
            # Output to test search output
            # print("Search Rank = "+str(r.rank)) # debug: view rank
            print("Plot = " + r["plot"])
            print("Title = " + r["title"])
            print("Score = " + str(r["tomato_score"]))
            # print("Director = "+r["director"])
            # print("Actors = "+r["actors"])
            # print("Genre = "+r["genre"])
            # print("-------------------------------------------------------------------")

        # catch no results or output number
        if(len(results) == 0):
            print("No results found. Limited DB.. please try another search.")
        else:
            print()
            print("Found %d records in %0.06f seconds" %
                  (len(results), results.runtime))


if __name__ == '__main__':

    try:
        if(len(sys.argv) < 2):
            raise ValueError("No search query provided")
        # get all input words as a single query string
        query = ' '.join(sys.argv[1:])

    except:
        print('Usage Error: Please provide a search query')
    else:
        # continue with search
        ix = index_data()
        search(ix, query)
