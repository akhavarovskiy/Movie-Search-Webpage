import omdb
import csv
import requests

def search_dictionaries(key, value, list_of_dictionaries):
	return [element for element in list_of_dictionaries if element[key] == value]

API_KEY = 'd76fe527' #premium service OMDB API Key
# Set the default key for all future calls.
omdb.set_default('apikey', API_KEY)

#build list of valid IMDB_IDs
valid_imdbids = []
with open("valid_imdbid.csv") as file:
    for line in file:
        line = line.strip() #preprocess line
        valid_imdbids.append(line)

#print(valid_imdbids)

# Prepare CSV file for output of db
with open('JAMA_Movie_DB.csv', mode='w', encoding='utf8') as dbfile:
	db_writer = csv.writer(dbfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL) #csv formatting
	# File header population
	db_writer.writerow(['imdb_id', 'title', 'year', 'plot', 'poster', 'runtime', 'website', 'genre', 'director', 'actors', 'rating', 'country', 'season', 'episode', 'tomato_score', 'tomato_fresh'])
	
	#loop from imdbid 0000001 to 0001000   <--- This will likely change to a static valid IMDBID list to iterate through
	for x in reversed(valid_imdbids):

		print(x) #debug to check progress and API call speed.

		
		imdbid = "tt" + str(x).zfill(7) # create imdbid with padding 0s. Seven int length. i.e. 24 = 0000024

		try:
			res = omdb.get(imdbid=imdbid,tomatoes=True)
		except:
			print("Internal Error - Timeout Detected.")
			continue

		#print(res)

		#if there is a valid API response
		if res:

			# Fields of our schema
			imdb_id = str(res.get("imdb_id"))
			title = str(res.get("title"))
			year = str(res.get("year"))
			plot = str(res.get("plot"))
			poster = str(res.get("poster"))
			runtime = str(res.get("runtime"))
			website = str(res.get("website"))
			genre = str(res.get("genre"))
			director = str(res.get("director"))
			actors = str(res.get("actors"))
			rating = str(res.get("rated"))
			country = str(res.get("country"))
			season = str(res.get("season"))
			episode = str(res.get("episode"))
			tomato_score = search_dictionaries("source", "Rotten Tomatoes",res.get("ratings"))
			if tomato_score:
				tomato_score = tomato_score[0].get("value")
			else:
				tomato_score = "N/A"
			tomato_fresh = str(res.get("tomato_fresh"))
			# write the fields to file
			db_writer.writerow([imdb_id,title,year,plot,poster,runtime,website,genre,director,actors,rating,country,season,episode,tomato_score,tomato_fresh])