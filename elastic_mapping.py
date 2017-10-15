from elasticsearch_dsl import Keyword, Mapping, Text, Date, Integer, Float
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['localhost'])

m = Mapping('movie')

m.field('name', 'text')
m.field('plot', 'text')
m.field('genres', 'text')
m.field('director', 'text')
m.field('keywords', 'text')
m.field('awards', 'text')
m.field('stars', 'text')
m.field('duration', 'text')
m.field('actors', 'text')
m.field('creators', 'text')
m.field('description', 'text')

m.field('rating_value', 'float')
m.field('rating_count', 'integer')

m.field('language', 'keyword')
m.field('country', 'keyword')

m.field('release_date', 'date')

m.save('imdb')