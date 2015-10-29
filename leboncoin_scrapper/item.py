__author__ = 'buzz'


class Item(object):
    """Represents an item."""

    def __init__(self, item_id, publication_date, title, place, price, url, pictures):
        """Constructor.
        :type pictures: object
        """
        self.item_id = item_id
        self.publication_date = publication_date
        self.title = title
        self.place = place
        self.price = price
        self.url = url
        self.pictures = pictures

        # Details of the item

        # The seller nickname
        self.seller_name = None

        # A table with pictures
        self.big_pictures = None

        # Department code (ex : 31930)
        self.dept_code = None

        # URL us
        self.mail_url_post = None
        self.city = None
        self.post_code = None
        self.description = None
        self.phone = None
        self.full_dic = None

    def printargs(self):
        """Method docstring."""
        print ('ID : ' + self.item_id)
        print ('Date : ' + self.publication_date)
        print ('Title : ' + self.title)
        print ('Place : ' + self.place)
        print ('Price : ' + self.price)
        print ('Url : ' + self.url)
        for pic in self.pictures:
            print ('Url: ' + pic)
        for pic in self.big_pictures:
            print ('Url: ' + pic)
        print ('Seller : ' + self.seller_name)
        print ('mail url post : ' + self.mail_url_post)
        print ('city : ' + self.city)
        print ('post code : ' + self.post_code)
        print ('description : ' + self.description)
        print ('phone : ' + self.phone)

    def to_param_list(self):
        param_list = [self.item_id, self.publication_date, self.title, self.place, self.price, self.url,
                      self.description, self.seller_name, self.mail_url_post, self.phone, self.post_code, self.city]
        return param_list
