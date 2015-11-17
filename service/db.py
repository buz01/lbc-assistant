# -*- coding: utf-8 -*-
from model.item import Item
from service.processor import Processor
import os

__author__ = 'buzz'

import sqlite3
from model.search import Search
import logging
import logging.config
import datetime


class DB(object):
    BASE_DIR ='/home/buzz/Documents/Python/PycharmProjects/lbc-assistant/'
    DB_NAME = os.path.join(BASE_DIR,'database', 'lbc.sqlite')

    db_name = None
    db_version = None
    cnx = None

    def __init__(self, db_name=DB_NAME, db_version=None):
        self.db_name = db_name
        self.db_version = db_version
        self.cnx = sqlite3.connect(db_name)

    def printargs(self):
        """Method docstring."""
        print ('db_name : ' + self.db_name)
        print ('db_version : ' + self.db_version)

    def drop_full_db(self):
        c = self.cnx.cursor()
        try:
            c.execute('drop table param')
            c.execute('drop table search')
            c.execute('drop table prices')
            c.execute('drop table item')
        except sqlite3.OperationalError:
            pass

    def drop_gracefully_db(self):
        c = self.cnx.cursor()
        try:
            c.execute('drop table param')
            c.execute('drop table search')
        except sqlite3.OperationalError:
            pass

    def drop_and_create_full_db(self):
        c = self.cnx.cursor()
        try:
            c.execute('drop table param')
        except sqlite3.OperationalError:
            pass
        try:
            c.execute('drop table search')
        except sqlite3.OperationalError:
            pass
        try:
            c.execute('drop table person')
        except sqlite3.OperationalError:
            pass
        try:
            c.execute('drop table prices')
        except sqlite3.OperationalError:
            pass
        try:
            c.execute('drop table item')
        except sqlite3.OperationalError:
            pass
        self.create_table_param()
        self.create_table_search()
        self.create_table_item()
        self.create_table_prices()

    def drop_and_create_db_keep_param_and_search(self):
        c = self.cnx.cursor()
        try:
            c.execute('drop table person')
            c.execute('drop table prices')
            c.execute('drop table item')
        except sqlite3.OperationalError:
            pass
        self.create_table_item()

    def create_table_param(self):
        c = self.cnx.cursor()
        c.execute("""create table param(
                        version         integer ,
                        refresh_delay   integer,
                        message_default_name    varchar(200),
                        message_default_email   varchar(200),
                        message_default_tel     varchar(20),
                        message_default_text    varchar(500)
                    )
        """)

    def create_table_search(self):
        c = self.cnx.cursor()
        c.execute("""create table search(
                        id_search       integer primary key autoincrement,
                        label           varchar(50) not null,
                        url             varchar(2000) not null,
                        description     varchar(500),
                        refresh_delay   integer,
                        message_name    varchar(200),
                        message_email   varchar(200),
                        message_tel     varchar(20),
                        message_text    varchar(500),
                        creation_date   datetime,
                        last_run        datetime
                    )
        """)

    def create_table_item(self):
        c = self.cnx.cursor()
        c.execute("""create table item(
                        id_item       integer primary key autoincrement,
                        id_search     integer not null references search(id_search),

                        item_id       varchar(20) not null,
                        publication_date    datetime,
                        title         varchar(200) not null,
                        place         varchar(200),
                        price         integer,
                        url           varchar(500) not null,
                        description   varchar(2000),

                        seller_name            varchar(50) not null,
                        mail_url_post   varchar(500),
                        phone       varchar(20),
                        post_code     varchar(10),
                        city            varchar(200),

                        creation_date   datetime
                    )
        """)

    def create_table_prices(self):
        c = self.cnx.cursor()
        c.execute("""create table prices(
                        id_item     integer not null references item(id_item),
                        price       integer ,
                        from_date   datetime not null,
                        to_date  datetime
                    )
        """)

    def fill_param(self):
        c = self.cnx.cursor()
        c.execute('begin transaction')
        c.execute("""insert into param( version, refresh_delay,
                                message_default_name, message_default_email, message_default_tel, message_default_text)
                        values (
                    1, 5,
                    "Sébastien",
                    "_lbc.20.buz_01@antichef.net",null,
                    "Bonjour, je suis interessé par votre annonce. Est-ce que {{PRIX}} euros vous conviennent pour une livraison en France métropolitaine (Toulouse) ? Je peux vous régler en Paypal ou chèque à votre convenance. Cordialement, Sébastien"
                )
        """)
        self.cnx.commit()

    def fill_search_example(self):
        c = self.cnx.cursor()
        c.execute('begin transaction')
        c.execute("""insert into search (   label, url, description, refresh_delay,
                                            message_name,message_email,message_tel,message_text,
                                            creation_date, last_run)
                        values (
                    'Chemises Luxe',
                    'http://www.leboncoin.fr/vetements/offres/midi_pyrenees/occasions/?f=a&th=1&ct=3&clos=4&q=chemise+desigual+or+chemise+burton+or+chemise+billabong+or+chemise+armani+or+chemise+kaporal+or+chemise+boss+or+chemise+diesel+or+chemise+hilfiger+or+chemise+eden+park+or+chemise+guess+or+chemise+teddy+smith+or+chemise+timberland+or+chemise+ralph+lauren+or+chemise+kenzo+or+chemise+burberry',
                    '',
                    5,
                    "Sébastien", "_lbc.20.buz_01@antichef.net","","Bonjour, je suis interessé par votre annonce. Est-ce que {{PRIX}} euros vous conviennent pour une livraison en France métropolitaine (Toulouse) ? Je peux vous régler en Paypal ou chèque à votre convenance. Cordialement, Sébastien",
                    datetime('now','localtime'),
                    null
                )
        """)
        self.cnx.commit()

    def insert_item(self, search, item):
        c = self.cnx.cursor()
        c.execute('begin transaction')

        param_list = [search.search_id]
        param_list.extend(item.to_param_list())
        c.execute("""insert into item (
                        id_search,
                        item_id, publication_date, title, place, price, url, description,
                        seller_name, mail_url_post, phone, post_code, city,
                        creation_date
                    ) values (
                        ?,
                        ?,?,?,?,?,?,?,
                        ?,?,?,?,?,
                        datetime('now','localtime')
                    )
        """, param_list)
        prices_param_list = [c.lastrowid, item.price]
        # TODO Gérer les prix sur les objets deja existants
        c.execute("""insert into prices (
                        id_item, price, from_date, to_date
                    ) values (
                        ?, ?, datetime('now','localtime'), null
                    )
        """, prices_param_list)

        self.cnx.commit()

    def find_item_by_id(self, item_id):
        c = self.cnx.cursor()
        c.execute("""select id_search, item_id, publication_date, title, place, price, url, description,
                        seller_name, mail_url_post, phone, post_code, city, creation_date
                     from item
                     where item_id=?""", [item_id])
        rec = c.fetchone()
        item = Item(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[6], rec[7], rec[8])
        search.creation_date = rec[9]
        search.last_run = rec[10]
        return search

    def find_search_by_id(self, search_id):
        c = self.cnx.cursor()
        c.execute("""select id_search, label, url, description, refresh_delay, message_name, message_email, message_tel,
                            message_text, creation_date, last_run
                     from search
                     where id_search=?""", [search_id])
        rec = c.fetchone()
        search = Search(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[6], rec[7], rec[8])
        search.creation_date = rec[9]
        search.last_run = rec[10]
        return search


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    my_db = DB()
    my_db.drop_and_create_full_db()
    my_db.fill_param()
    my_db.fill_search_example()
    my_search = my_db.find_search_by_id(1)
    processor = Processor(my_search)
    stop_item=Item(999, datetime.datetime(2015,8,18), "", "", "", "", [])

    item_queue = processor.get_item_list_with_full_details_fast(stop_item=stop_item)
    for i in item_queue:

        my_db.insert_item(my_search, i)

