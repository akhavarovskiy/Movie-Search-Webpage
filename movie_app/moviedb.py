from flask import Flask, render_template, url_for, request
import whoosh
import os
from whoosh.index import create_in
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
from whoosh.qparser import plugins
from whoosh.qparser import PhrasePlugin

from whoosh.lang.stopwords import stoplists
from whoosh import sorting
from whoosh.scoring import Frequency,MultiWeighting,FunctionWeighting,TF_IDF,BM25F

from whoosh import qparser
import csv

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def index():
	#print('HEya')
	return render_template('home.html')

@app.route('/my-link/')
def my_link():
	#print('clicked')
	return 'Click'

@app.route('/results/', methods=['GET', 'POST'])
def results():
	global mysearch
	if request.method == 'POST':
		data = request.form
		print( "POST" )
		print( data )
	else:
		data = request.args
		print( "GET" )
		print( data )

	
	keywordquery = data.get('searchterm')
	page         = data.get('page')
	if page is None:
		page = 1

	print('Keyword Query is: ' + keywordquery)

	titles, plot, poster, tomato_score, year, actors, director, genre, pages = mysearch.search(keywordquery, int(page))
	return render_template('results.html',  query=keywordquery, results=(pages,zip(titles, plot, poster, tomato_score, year, actors, director, genre)))

def custom_weight(searcher, fieldname, text, matcher):
	if fieldname == 'tomato_score':
		return matcher.value()/100
	return 0.0

class MyWhooshSearch(object):
	"""docstring for MyWhooshSearch"""
	def __init__(self):
		super(MyWhooshSearch, self).__init__()

	def search(self, queryEntered, page):
		title    = list()
		plot     = list()
		poster   = list()
		year     = list()
		director = list()
		genre    = list()
		actors   = list()
		tomato_score = list()

 		# JY for the sake of demonstrating ranking weight, not going to affect search much visibly. 
		#mw=MultiWeighting(BM25F(), tomato_score=FunctionWeighting(custom_weight)) # plot=BM25F(B=0.75, plot_B=1.0, K1=2.0), actors=BM25F(B=0.75, actors_B=1.0, K1=1.5), director=TF_IDF()  )
		with self.indexer.searcher(weighting=BM25F()) as search: 
			parser = MultifieldParser(['title', 'plot','actors', 'director', 'genre'], schema=self.indexer.schema, termclass=FuzzyTerm) #
			parser.add_plugin(plugins.FuzzyTermPlugin())
			parser.add_plugin(plugins.SequencePlugin())
			query = parser.parse(queryEntered)
			results = search.search_page(query, page, 20, sortedby = {'tomato_score'}, reverse=True) # 'tomato_score', 'year'

			for x in results:
				title.append(x['title'])
				plot.append(x['plot'])
				poster.append(x['poster'])
				tomato_score.append(x['tomato_score'])
				year.append(x['year'])
				director.append(x['director'])
				actors.append(x['actors'])
				genre.append(x['genre'])

		return title, plot, poster, tomato_score, year, actors, director, genre, results.pagecount if results.pagecount < 23 else 23 
	
	def index_csv(self):

		if os.path.exists("movieIndex"):
			self.indexer= open_dir("movieIndex")
			return
		else:
			# path doesn't exist, make dir and build index
			os.mkdir("movieIndex")

		# JY, add english stopword and ngram
    	# stop words are
    	# {'because', 'such', 'not', 'off', 'what', 'to', 'very', 'we', 'a', 'own', 'about', 'once', 'herself', 'on', 'how', 'himself', 'by', 'have', 'your', 'his', 'themselves', 'am', 'between', 'does', 'my', 'from', 'or', 'both', 'then', 'no', 'she', 'same', 'above', 'are', 'its', 'ourselves', 'below', 'having', 'me', 'into', 'and', 'ours', 'be', 'at', 'other', 'just', 'again', 'that', 'down', 'these', 'only', 'yourselves', 'under', 'most', 'can', 'itself', 'doing', 'in', 'when', 'has', 'than', 'each',
    	#     'of', 'you', 'should', 'here', 'her', 'some', 'now', 'hers', 'why', 'so', 'out', 'where', 'nor', 'our', 'don', 'an', 'been', 'over', 's', 'while', 'were', 'do', 'whom', 'their', 'had', 'is', 'until', 'yourself', 'this', 't', 'few', 'which', 'during', 'who', 'i', 'through', 'there', 'those', 'it', 'more', 'if', 'theirs', 'for', 'will', 'him', 'the', 'was', 'did', 'too', 'with', 'further', 'myself', 'they', 'all', 'yours', 'after', 'but', 'against', 'he', 'before', 'as', 'up', 'them', 'any', 'being'}
		# 
		#ana = analysis.StandardAnalyzer(stoplist=stoplists["en"]) # | analysis.NgramFilter(minsize=3, maxsize=10)
		schema = Schema(
			imdb_id=ID(stored=True,sortable=True),
			title=TEXT(stored=True, sortable=True),
			year=TEXT(stored=True, sortable=True),
			plot=TEXT(stored=True, sortable=True),
			poster=ID(stored=True),
			runtime=TEXT(stored=True), #NUMERIC(int, 16, decimal_places=0, stored=True, signed=False, sortable=True, default=0),
			website=ID(stored=True),
			genre=TEXT(stored=True, sortable=True),
			director=TEXT(stored=True),
			actors=TEXT(stored=True),
			rating=TEXT(stored=True, sortable=True),
			country=TEXT(stored=True, sortable=True),
			season=TEXT(stored=True),
			episode=TEXT(stored=True),
			tomato_score=NUMERIC(int, 16, decimal_places=0, signed=False, sortable=True, stored=True, default=0),	
			tomato_fresh=TEXT(stored=True)
    	)

		indexer = create_in('movieIndex', schema)
		writer  = indexer.writer()

		#imdb_id,title,year,plot,poster,runtime,website,genre,director,actors,rating,country,season,episode,tomato_score,tomato_fresh
		with open('JAMA_Movie_DB.csv', 'rt', encoding='utf-8', errors='ignore') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')

			row_count = 0  # counter to check progress
			for row in reader:
				try:
					ts = int(row[14].replace('%',' ').replace('N/A', '0'))
				except ValueError:
					ts = 0
				
				writer.add_document(imdb_id =row[0],
									title   =row[1],
									year    =row[2],
									plot    =row[3], 
									poster  =row[4],
									runtime =row[5],
									website =row[6],
									genre   =row[7],
									director=row[8], 
									actors  =row[9].replace(', ', ','),
									rating  =row[10],
									country =row[11],
									season  =row[12],
									episode =row[13], 
									tomato_score = ts,
									tomato_fresh = row[15] 
					
				)

				# print progress of indexing
				if row_count % 5000 == 0:
					print("Processed %d/58100 records ..." % (row_count))

				row_count += 1

		print("Processed %d/58100 records." % (row_count))
		print("---------------------------")
		print("Commiting Index")
		print("---------------------------")
		writer.commit()
		self.indexer = indexer
		print("---------------------------")
		print("Done")
		print("---------------------------")

if __name__ == '__main__':
	global mysearch
	mysearch = MyWhooshSearch()
	mysearch.index_csv()
	app.run(debug=True)