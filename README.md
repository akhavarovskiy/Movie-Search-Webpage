# Movie Database

![Alt text](/images/ss1.png?raw=true "SS1")
![Alt text](/images/ss3.png?raw=true "SS3")


README
Assignment 3
TEAM JAMA

In this directory there are two separate program directories Search and BuildDB.

BuildDB contains the program files to build our movie DB (csv) using the OMDB API.

Search contains a command line program which allows you to search the movie db using an inverted index and Whoosh!

Details below on each program.

--------------------------------------------- Search ---------------------------------------------

To run the program, navigate to the "search" subdirectory and simply execute the search.py with your search as a command line argument(s). The JAMA_Movie_DB.csv database file must be present in the same directory.

	* python search.py [keyword search]
		OR
	* python3 search.py [keyword search]

An already built DB and index file are provided to save time on execution.

****NOTE: You must delete the IndexDir directory if you wish to rebuild the Index or if program gives error for some undefined reason (file missing etc) and creates the directory.****

If the index directory is deleted, the program will first create the index file. This could take several minutes depending on system speed. The console will output progress, as well when the index changes are committed (which can take minutes on its own). The "indexDir" directory will be created to store the file.

----- Keyword Search:

The program will take all text passed as arguments and convert them to a single query. You can use AND/OR operators to combine searches - to search over actors, title, director and genre. Fuzzy searching is implemented. Example keywords:

	* Sci-Fi AND Horror
	* Ghost AND Patrick
	* Matt Damon
	* Lord of the Rings

----- Field search, range:
	tomato_score:[11 TO 20]

----- Output:

The program will output a tuple from our database where a match is found.

---------------------------------------------------------------------------------------------------------------------
One can also search for particular field, note the 'plot' field has an NGRAM and Stopwords attached to it.
search like:    plot:hap   will match anytine word starts with 'hap' such as 'happy', happen' in the 'pplot field.

The stopwords chosen are:
 {'because', 'such', 'not', 'off', 'what', 'to', 'very', 'we', 'a', 'own', 'about', 'once', 'herself', 'on', 'how', 'himself', 'by', 'have', 'your', 'his', 'themselves', 'am', 'between', 'does', 'my', 'from', 'or', 'both', 'then', 'no', 'she', 'same', 'above', 'are', 'its', 'ourselves', 'below', 'having', 'me', 'into', 'and', 'ours', 'be', 'at', 'other', 'just', 'again', 'that', 'down', 'these', 'only', 'yourselves', 'under', 'most', 'can', 'itself', 'doing', 'in', 'when', 'has', 'than', 'each','of', 'you', 'should', 'here', 'her', 'some', 'now', 'hers', 'why', 'so', 'out', 'where', 'nor', 'our', 'don', 'an', 'been', 'over', 's', 'while', 'were', 'do', 'whom', 'their', 'had', 'is', 'until', 'yourself', 'this', 't', 'few', 'which', 'during', 'who', 'i', 'through', 'there', 'those', 'it', 'more', 'if', 'theirs', 'for', 'will', 'him', 'the', 'was', 'did', 'too', 'with', 'further', 'myself', 'they', 'all', 'yours', 'after', 'but', 'against', 'he', 'before', 'as', 'up', 'them', 'any', 'being'}


---------------------------------------------------------------------------------------------------------------------
Sorting:

Any query if thre are HITS, will be also sorted by tomato_score in descending order.
This make sense to display HIT with the most popular score.


---------------------------------------------------------------------------------------------------------------------
Ranking weights:

The following weight algorithm is used:
BM25F(),   				#for everything else
imdb_id=Frequency(), 	#for id field
plot=TF_IDF()			#for plot field



--------------------------------------------- BuildDB ---------------------------------------------
To build the database, navigate to the "build_db" subdirectory and simply execute omdb_import.py with no arguments. For example:

	* python omdb_import.py
		OR
	* python3 omdb_import.py

The program loops through the IMDBs in a provided list of IMDB_IDs to reduce the time spent calling the API for invalid/un-used IMDB_IDs. This was recommended on the OMDB usage as the range would otherwise take unreasonably long to iterate through (many many days). If you would like to rather run in this iterative fashion, with no reliance on the IMDB_ID list, you can replace line 28 with a static range to loop through (1 to 9999999 for all records). Even with this time saving feature, the runtime is around 12-24 hours to get all the data from the API.

The built database includes ~58,000 rows.

Output:
	JAMA_Movie_DB.csv database file.


