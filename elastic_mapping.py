from elasticsearch_dsl import Mapping
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['localhost'])


def create_mapping():
    print "Creating mapping..."

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

    m.field('ratingValue', 'float')
    m.field('ratingCount', 'integer')

    m.field('language', 'keyword')
    m.field('country', 'keyword')

    m.field('releaseDate', 'date')

    m.save('imdb')

if __name__ == '__main__':
    create_mapping()