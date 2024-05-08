from SPARQLWrapper import SPARQLWrapper, JSON
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def get_genres(lang='en'):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
        SELECT DISTINCT ?genre STR(?glabel)
        WHERE {{
            ?genre rdf:type dbo:MusicGenre .
            ?genre dcterms:subject dbr:Category:Film_genres .
            ?genre rdfs:label ?glabel .
            FILTER(LANG(?glabel) IN ("", "{lang}")) .
        }}
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    results = [
        {
            'name': item.get('callret-1').get('value'),
            'uri': item.get('genre').get('value'),
        }
        for item in results.get('results').get('bindings')
    ]

    return results


def get_movies(genres=(), limit=100, lang='en'):
    genres_list = ', '.join(f'"{g}"' for g in genres)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?movie ?title STR(?glabel)
        WHERE {{
            ?movie rdf:type dbo:Film .
            ?movie rdfs:label ?title .
            FILTER(LANG(?title) = '{lang}') .
            ?movie dbo:genre ?genre .
            ?genre rdfs:label ?glabel .
            FILTER(LANG(?glabel) IN ("", "{lang}")) .
            FILTER(STR(?glabel) IN ({genres_list})) .
        }}
        LIMIT {limit}
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    results = [
        {
            'title': item.get('title').get('value'),
            'genre': item.get('callret-2').get('value'),
            'uri': item.get('movie').get('value'),
        }
        for item in results.get('results').get('bindings')
    ]

    return results


@app.route('/genres', methods=['GET'])
def genres_view():
    lang = request.args.get('lang', 'en')
    genres_list = get_genres(lang=lang)
    return genres_list


@app.route('/movies', methods=['GET'])
def movies_view():
    genres = request.args.get('genres')
    limit = request.args.get('limit', 100)
    lang = request.args.get('lang', 'en')
    movies = get_movies(genres=genres.split(','), limit=limit, lang=lang)
    return movies


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
