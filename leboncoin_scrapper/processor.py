# -*- coding: windows-1252 -*-
import logging

__author__ = 'buzz'

import requests
import bs4
import ast
from datetime import datetime, date, timedelta
import re
from leboncoin_scrapper.item import Item
import locale
import Queue
import threading


class Processor(object):
    nb_ad_per_page = 35
    search = None

    def __init__(self, search):
        self.search = search

    @staticmethod
    def parse_date(day_or_date, hour):
        """Transform a variable date+hour format in normalized one.

          eg. :  transform_date("2 août 12:51", "12:51")="2015/08/02 17:03"

        :rtype : str
        :param day_or_date: String representing whether "Aujourd'hui", "Hier", or a date with format "2 août 12:51"
        :param hour: String representing the hour and minutes, eg "17:03"
        :return: a datetime oject representing the date and time
        """
        if day_or_date == "Aujourd'hui":
            day = date.today().strftime('%Y/%m/%d')
        elif day_or_date == 'Hier':
            day = (date.today() - timedelta(1)).strftime('%Y/%m/%d')
        else:
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
            # This is to parse correctly the abbreviated month with the weird formatting of the items list
            rep={'oct':'oct.','Oct':'oct.','nov':'nov.','Nov':'nov.','sept':'sept.','Sept':'sept.','juil':'juil.','Juil':'juil.','févr':'févr.','Févr':'févr.','janv':'janv.','Janv':'janv.','déc':'déc.','Déc':'déc.'}
            rep=dict((re.escape(k),v) for k,v in rep.iteritems())
            pattern=re.compile("|".join(rep.keys()))
            day_or_date=pattern.sub(lambda m: rep[re.escape(m.group(0))],day_or_date)

            day = datetime.strptime(day_or_date.encode('UTF-8') + ' ' + date.today().strftime('%Y'),
                                    '%d %b %Y').strftime("%Y/%m/%d")
        return datetime.strptime(day + " " + hour, "%Y/%m/%d %H:%M")

    @staticmethod
    def extract_item_id(url):
        """Return the ID of the matching item.
        A regexp is used. If the regexp is not found, return None

        :type url: str
        :param url: String representing the URL of an ad, or None if no ad ID has been found in the URL
        :rtype : str
        """
        m = re.search('/([0-9]+)\.htm', url)
        if m is not None:
            return m.group(1)
        else:
            return None

    def get_item_list_details_fast(self, item_list, q):
        for i in item_list:
            q.put(self.parse_item_details(i))

    def get_item_list_with_full_details_fast(self, stop_item=None, max_page=25):
        """
        Get the item list and the entire items details by using several threads to speed up processing.
        First the list of items are retrieved by using multi threading.
        Then the list is processed ; a thread is processing a fixed number of items (5 by default).
        :param stop_item: optional. If specified, the publication date is used to retrieve only the items newer than
                          the stop item. If not specified, all the items are retrieved
        :param max_page: optional. The maximum number of pages to process. If not specified, this value is fixed to 25
        :return: a list of Item with full details
        """
        item_list = self.get_item_list(stop_item, max_page)
        q = Queue.Queue()
        item_per_thread = 5
        logging.info("Running threads ...")

        x = 1
        thread_list = []
        for _ in item_list[::item_per_thread]:
            t = threading.Thread(target=self.get_item_list_details_fast,
                                 args=(item_list[item_per_thread * (x - 1):item_per_thread * x:1], q))
            t.daemon = True
            t.start()
            thread_list.append(t)
            x += 1

        logging.info("{} threads launched".format(len(thread_list)))

        logging.info("Waiting for all threads to finish...")
        for t in thread_list:
            t.join()

        logging.info("Finished !")
        res = []
        while not q.empty():
            res.append(q.get())
        return res

    def get_item_list_from_page(self, page_number, q, stop_item=None):
        """


        :param page_number:
        :param q:
        :param stop_item:
        :type q: Queue
        """
        logging.info("Thread {0} : Getting item list from page {1}".format(threading.currentThread(), str(page_number)))
        response = requests.get(self.search.url + '&o=' + str(page_number))
        full_page_soup = bs4.BeautifulSoup(response.text)
        for current_item_with_url_soup in full_page_soup.select('div.list-lbc a'):
            current_item = self.parse_item_summary(current_item_with_url_soup)

            # Check if we must stop now
            # TODO Traiter le cas si plusieurs items sont à la même date de publication, et qu'ils sont choisis
            #      comme stop item (transformer la comparaison de date en strict, et gerer ensuite ce cas avec
            #      une requete SQL pour savoir ceux déjà en base et ceux à inserer.
            if stop_item is not None and current_item.publication_date < stop_item.publication_date:
                logging.info(
                    "Thread {0} : Stop crawling : Found an item older or same as the stop item {1} : {2}".format(
                        threading.currentThread(), stop_item.item_id, current_item.item_id))
                break

            q.put(current_item)

    def get_item_list(self, stop_item=None, max_page=25):
        q = Queue.Queue()
        item_list = []
        nb_thread = 5

        logging.info("Running threads ...")

        for page_nb in range(1, max_page + 1, nb_thread):
            thread_list = []
            for i in range(nb_thread):
                if page_nb + i <= max_page:
                    t = threading.Thread(target=self.get_item_list_from_page, args=(page_nb + i, q, stop_item))
                    t.daemon = True
                    t.start()
                    thread_list.append(t)
                    logging.info("Thread {0} launched on page {1}".format(t.name, page_nb + i))

            logging.info("Waiting for all threads to finish...")
            for t in thread_list:
                t.join()

            nb_item_in_queue = q.qsize()
            while not q.empty():
                item_list.append(q.get())

            if nb_item_in_queue < nb_thread * self.nb_ad_per_page:
                logging.info("The queue is not full [{0}<{1}], we stop here".format(nb_item_in_queue,
                                                                                    nb_thread * self.nb_ad_per_page))
                break

        return item_list

    def parse_item_summary(self, current_item_with_url_soup):
        title, place, price, pictures = ("", "", "", [])
        item_url = current_item_with_url_soup.attrs.get('href')
        item_id = self.extract_item_id(item_url)
        logging.info("Analyzing item {0}".format(str(item_id)))
        current_item_soup = current_item_with_url_soup.select('div.lbc')[0]
        # Parse date
        date_to_format = current_item_soup.select('div.date div')
        publication_date = Processor.parse_date(date_to_format[0].get_text(), date_to_format[1].get_text())
        # Parse image
        main_pic_url = ""
        for pic_anchor in current_item_soup.select('div.image div.image-and-nb img'):
            main_pic_url = pic_anchor.attrs.get('src')
        pictures.append(main_pic_url)
        # Parse detail
        for detail in current_item_soup.select('div.detail'):
            for tag in detail.select('h2.title'):
                title = tag.get_text().strip()
            for tag in detail.select('div.placement'):
                place = " ".join(tag.get_text().strip().split())
            for tag in detail.select('div.price'):
                price = tag.get_text().strip()
        current_item = Item(item_id, publication_date, title, place, price, item_url, pictures)
        return current_item

    def parse_item_details(self, item):
        """
        :param item:
        :return:
        """

        response = requests.get(item.url)
        soup = bs4.BeautifulSoup(response.text)

        for tag in soup.select('div.upload_by a'):
            # Retrieve seller name
            item.seller_name = tag.get_text().strip()

            # Mail : URL used to send mail
            item.mail_url_post = tag.attrs.get('href')

        # Try with the data in the script tag
        for tag in soup.find_all('script'):
            if tag.attrs.get('src') is None and tag.attrs.get('id') is None and tag.attrs.get(
                    'type') == 'text/javascript':
                m = re.search(u'var utag_data = ({.*})', tag.get_text(), re.DOTALL)
                if m is not None:
                    new_string = re.sub('(\w+)( ?: ?"\w+")', '"\\1"\\2', m.group(1))  # Embrace keys with double quote
                    key_value_list_text = ast.literal_eval(new_string)  # Evaluate expression
                    item.full_dic = key_value_list_text
                    if key_value_list_text.get('departement') is not None:
                        item.dept_code = key_value_list_text.get('departement')
                    if key_value_list_text.get('cp') is not None:
                        item.post_code = key_value_list_text.get('cp')

        # Retrieve the city
        tag_list = soup.select('td[itemprop="addressLocality"]')
        for tag in tag_list:
            item.city = tag.get_text().strip()

        # Retrieve the description
        tag_list = soup.select('div[itemprop="description"]')
        for tag in tag_list:
            item.description = "".join(tag.stripped_strings)

        for tag in soup.select('div.AdviewContent div.content'):
            # description = tag.get_text().strip()
            item.description = "".join(tag.stripped_strings)

        # Phone (if any)
        # TODO Risque d'être un peu chaud, à cause des restrictions du CORS du WS Rest obtenant l'image du tel...

        # Pictures
        # Set is used because if there is only one picture, the carousel in LBC
        # is not present
        item.big_pictures = set([])

        # Main pic
        for tag in soup.select('div.lbcImages div.images_cadre a'):
            m = re.search("(http://.*)'\);", tag.attrs.get('style'))
            item.big_pictures.add(m.group(1))

        # From the carousel
        for tag in soup.select('div#thumbs_carousel a span.thumbs'):
            m = re.search("(http://.*)/thumbs(/.*)'\);", tag.attrs.get('style'))
            item.big_pictures.add(m.group(1) + '/images' + m.group(2))

        return item

    def print_list(self, item_list):
        for i in item_list:
            i.printargs()
            print("--------------")
