import pandas as pd





class FundPerforms:
    def __init__(self, data):
        self.during = [i.get('during') for i in data]
        self.applies = [i.get('applies') for i in data]
        self.data_dict = { 
            'date': self.during,
            'applies': self.applies
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class FundRating:
    def __init__(self, data):

        self.ratingDate = [i.get('ratingDate') for i in data]
        self.ratingId = [i.get('ratingId') for i in data]
        self.rating = [i.get('rating') for i in data]
        self.ratingCycle = [i.get('ratingCycle') for i in data]
        self.ratingResults = [i.get('ratingResults') for i in data]


        self.data_dict = { 
            'rating_date': self.ratingDate,
            'rating_id': self.ratingId,
            'rating': self.rating,
            'rating_cycle': self.ratingCycle,
            'rating_results': self.ratingResults

        }

        self.as_dataframe = pd.DataFrame(self.data_dict)