from datetime import datetime

__author__ = 'buzz'


class Search(object):
    """Represents a search."""

    def __init__(self, search_id, label, url, description=None, refresh_delay=5, message_name=None, message_email=None,
                 message_tel=None, message_text=None):
        """Constructor.
        """
        self.search_id = search_id
        self.label = label
        self.url = url
        self.description = description
        self.refresh_delay = refresh_delay
        self.message_name = message_name
        self.message_email = message_email
        self.message_tel = message_tel
        self.message_text = message_text
        self.creation_date = datetime.now()
        self.last_run = None

    def printargs(self):
        """Method docstring."""
        print ('search_id : ' + str(self.search_id))
        print ('label : ' + self.label)
        print ('url : ' + self.url)
        print ('description : ' + self.description)
        print ('refresh_delay : ' + str(self.refresh_delay))
        print ('message_name : ' + self.message_name)
        print ('message_email : ' + self.message_email)
        print ('message_tel : ' + self.message_tel)
        print ('message_text : ' + self.message_text)
        print ('creation_date : ' + self.creation_date)
        print ('last_run : ' + str(self.last_run))

    def to_param_list(self):
        param_list = [self.label, self.url, self.description, self.refresh_delay, self.message_name, self.message_email,
                      self.message_tel, self.message_text, self.creation_date, self.last_run]
        return param_list
