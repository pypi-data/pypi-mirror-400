import pandas as pd



class YFNews:
    def __init__(self, content, ticker):

        self.id = [i.get('id') for i in content]
        self.contentType = [i.get('contentType') for i in content]
        self.title = [i.get('title') for i in content]
        self.description = [i.get('description') for i in content]
        self.summary = [i.get('summary') for i in content]
        self.pubDate = [i.get('pubDate') for i in content]
        thumbnail = [i.get('thumbnail') for i in content]
        print(thumbnail)
        if thumbnail is not None:
            self.originalUrl = [i.get('originalUrl') if i is not None and i.get('originalUrl') is not None else None for i in thumbnail]
        provider = [i.get('provider') for i in content]
        self.provider = [i.get('displayName') for i in provider]
        canonicalUrl = [i.get('canonicalUrl') for i in content]
        self.url = [i.get('url') for i in canonicalUrl]


        self.data_dict = { 
            'id': self.id,
            'content_type': self.contentType,
            'title': self.title,
            'description': self.description,
            'summary': self.summary,
            'pub_date': self.pubDate,
            'thumbnail': self.originalUrl,
            'provider': self.provider,
            'url': self.url
       

        }


        self.as_dataframe = pd.DataFrame(self.data_dict)
        self.as_dataframe['ticker'] = ticker