import pandas as pd



class Institutions:
    def __init__(self, stat, newPosition, increase, soldOut, decrease):

        self.holding_count = float(stat.get('holdingCount')) if stat.get('holdingCount') is not None else None
        self.holdingCountChange = float(stat.get('holdingCountChange')) if stat.get('holdingCountChange') is not None else None
        self.holdingRatio = float(stat.get('holdingRatio')) if stat.get('holdingRatio') is not None else None
        self.holdingRatioChange = float(stat.get('holdingRatioChange')) if stat.get('holdingRatioChange') is not None else None
        self.institutionCount = float(stat.get('institutionalCount')) if stat.get('institutionalCount') is not None else None
        self.newholdingCountChange = float(newPosition.get('holdingCountChange')) if newPosition.get('holdingCountChange') is not None else None
        self.newinstitutionalCount = float(newPosition.get('institutionalCount')) if newPosition.get('institutionalCount') is not None else None

        self.increaseholdingCountChange = float(increase.get('holdingCountChange')) if increase.get('holdingCountChange') is not None else None
        self.increaseinstitutionalCount = float(increase.get('institutionalCount')) if increase.get('institutionalCount') is not None else None

        self.soldholdingCountChange = float(soldOut.get('holdingCountChange')) if soldOut.get('holdingCountChange') is not None else None
        self.soldinstitutionalCount = float(soldOut.get('institutionalCount')) if soldOut.get('institutionalCount') is not None else None
 
        self.decreaseholdingCountChange = float(decrease.get('holdingCountChange')) if decrease.get('holdingCountChange') is not None else None
        self.decreaseinstitutionalCount = float(decrease.get('institutionalCount')) if decrease.get('institutionalCount') is not None else None


        self.data_dict = { 
            'holding_count': self.holding_count,
            'holding_change': self.holdingCountChange,
            'holding_ratio': self.holdingRatio,
            'ratio_change': self.holdingRatioChange,
            'institution_count': self.institutionCount,
            'new_count_change': self.newholdingCountChange,
            'new_institution_count': self.newinstitutionalCount,
            'increased_count': self.increaseinstitutionalCount,
            'increased_change': self.increaseholdingCountChange,
            'sold_count': self.soldinstitutionalCount,
            'sold_change': self.soldholdingCountChange,
            'decrease_count': self.decreaseinstitutionalCount,
            'decrease_change': self.decreaseholdingCountChange

        }
        self.as_dataframe = pd.DataFrame(self.data_dict, index=[0])