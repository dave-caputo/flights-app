from bs4 import BeautifulSoup
import urllib.request
import re


class FlightScraper():

    def __init__(self, links, bowlmap, chunkmap):
        self.links = links
        self.bowlmap = bowlmap
        self.chunkmap = chunkmap
        self.soups = []
        self.soupbowls = []
        self.sublinks = []
        self.chunks = []
        self.make_soup()
        self.serve_soupbowls()
        self.scoopout_chunks()

    def make_soup(self):
        for link in self.links:
            html = urllib.request.urlopen(link)
            soup = BeautifulSoup(html, 'lxml')
            self.soups.append(soup)

    def serve_soupbowls(self):
        for soup in self.soups:
            tag, attribute = self.bowlmap
            b = soup.find_all(tag, **attribute)
            self.soupbowls += b

    def scoopout_chunks(self):
        for i, bowl in enumerate(self.soupbowls):
            chunk = self.get_chunk(bowl)
            if 'exclude' not in chunk:
                self.chunks.append(chunk)
                if 'link' in chunk:
                    self.sublinks.append(chunk['link'])
                else:
                    chunk['link'] = self.links[i]

    def get_content(self, mapitem, bowl):
        data = bowl.get_content(
            mapitem['tag'],
            string=re.compile(mapitem.get('contains', '')),
            **mapitem.get('attribute', {}))
        try:
            return data
        except:
            return('Not available')

    def get_string(self, mapitem, bowl):
        data = bowl.find(
            mapitem['tag'],
            string=re.compile(mapitem.get('contains', '')),
            **mapitem.get('attribute', {}))

        try:
            string = re.sub(mapitem.get('strip', ''), '', data.string)
            return mapitem.get('prefix', '') + string
        except:
            return('Not available')

    def get_chunk(self, bowl):
        chunk = {}
        for i, m in enumerate(self.chunkmap):
            label = m['label']

            if m['action'] == 'default':
                data = m['string']

            elif m['action'] == 'find string':
                data = self.get_string(m, bowl)

            elif m['action'] == 'find attribute':
                data = bowl.find(m['tag']).get(m['attribute'])
                data = m.get('prefix', '') + data

            elif m['action'] == 'find parent attribute':
                data = bowl.find(m['tag'], **m.get('attribute', {}))
                data = data.find_parent(m['parent tag'])
                data = data.get(m['parent attribute'])
                data = m.get('prefix', '') + data

            else:
                data = 'Not available'

            chunk[label] = data

            if self.find_exclusions(m, data):
                chunk['exclude'] = True

        return chunk

    def find_exclusions(self, m, data):
        exclusions = m.get('exclude', [])
        return data in exclusions
