from bs4 import BeautifulSoup
import logging
import urllib.request
import re


logger = logging.getLogger('mylogger')
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)


class FlightScraper():

    def __init__(self, links, blockmap, datamap):
        self.links = links
        self.blockmap = blockmap
        self.datamap = datamap
        self.page_list = []
        self.block_list = []
        self.sublinks = []
        self.data_list = []
        self.test = False
        self.build_page_list()
        self.build_block_list()
        self.build_data_list()
        logger.info('FlightScraper object initialized')

    def build_page_list(self):
        links_g = iter(self.links)
        first_link = links_g.__next__()
        if first_link == 'test':
            self.build_test_page_list(links_g)  # will loop over remaining links.
            self.test = True
            logger.info('{} test link(s) found'.format(len(self.links)))
        else:
            logger.info('Live link(s) found')
            self.build_live_page_list(self.links)  # will loop over all links.

    def build_test_page_list(self, links):
        for link in links:
            self.get_page(open(link))
        logger.info('{} page(s) were added to the test page_list'.format(
            len(self.page_list)))

    def build_live_page_list(self, links):
        for link in self.links:
            html = urllib.request.urlopen(link)
            self.get_page(html)
        logger.info('{} page(s) were added to the live page_list'.format(
            len(self.page_list)))

    def get_page(self, html):
        page = BeautifulSoup(html, 'lxml')
        self.page_list.append(page)
        logger.info('A new page was added to the page_list')

    def build_block_list(self):
        for page in self.page_list:
            tag, attribute = self.blockmap
            b = page.find_all(tag, **attribute)
            self.block_list += b
        logger.info('{} blocks(s) were added to the block list'.format(
            len(self.block_list)))

    def build_data_list(self):
        for i, block in enumerate(self.block_list):
            block_data = self.get_block_data(block)
            if 'exclude' not in block_data:
                self.data_list.append(block_data)
                logger.info('Block data obtained for block {} containing {}'.format(i + 1, repr(block_data)))
                if 'link' in block_data:
                    self.sublinks.append(block_data['link'])
                else:
                    links_count = len(self.links)
                    if self.test:
                        links_count = len(self.links) - 1
                    if len(self.block_list) == links_count:
                        block_data['link'] = self.links[i]

    def get_content(self, mapitem, block):
        data = block.get_content(
            mapitem['tag'],
            string=re.compile(mapitem.get('contains', '')),
            **mapitem.get('attribute', {}))
        try:
            return data
        except:
            return('Not available')

    def get_string(self, mapitem, block):
        data = block.find(
            mapitem['tag'],
            string=re.compile(mapitem.get('contains', '')),
            **mapitem.get('attribute', {}))

        try:
            string = re.sub(mapitem.get('strip', ''), '', data.string)
            return mapitem.get('prefix', '') + string
        except:
            return('Not available')

    def get_block_data(self, block):
        block_data = {}
        for i, m in enumerate(self.datamap):

            if m['action'] == 'default':
                data = m['string']

            elif m['action'] == 'get_table_columns':
                columns = block.find_all('td')
                for i, col in enumerate(columns, 1):
                    if i == m['remove_column']:
                        continue
                    else:
                        data_label = m['labels'][i - 1]
                        data = col.string
                        block_data[data_label] = data

            elif m['action'] == 'find string':
                data = self.get_string(m, block)

            elif m['action'] == 'find attribute':
                try:
                    data = block.find(m['tag']).get(m['attribute'])
                    data = m.get('prefix', '') + data
                except TypeError:
                    data = ''

            elif m['action'] == 'find parent attribute':
                data = block.find(m['tag'], **m.get('attribute', {}))
                data = data.find_parent(m['parent tag'])
                data = data.get(m['parent attribute'])
                data = m.get('prefix', '') + data

            else:
                data = 'Not available'

            if m.get('label', None):
                data_label = m['label']
                block_data[data_label] = data

                if self.find_exclusions(m, data):
                    block_data['exclude'] = True

        return block_data

    def find_exclusions(self, m, data):
        exclusions = m.get('exclude', [])
        return data in exclusions
