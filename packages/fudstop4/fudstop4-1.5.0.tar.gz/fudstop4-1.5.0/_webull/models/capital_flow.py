import pandas as pd


class CapitalFlowLatest:
    def __init__(self, date, latest):
        self.superLargeInflow = float(latest.get('superLargeInflow'))
        self.superLargeOutflow = float(latest.get('superLargeOutflow'))
        self.superLargeNetFlow = float(latest.get('superLargeNetFlow'))
        self.largeInflow = float(latest.get('largeInflow'))
        self.largeOutflow = float(latest.get('largeOutflow'))
        self.largeNetFlow = float(latest.get('largeNetFlow'))
        self.newLargeInflow = float(latest.get('newLargeInflow'))
        self.newLargeOutflow = float(latest.get('newLargeOutflow'))
        self.newLargeNetFlow = float(latest.get('newLargeNetFlow'))
        self.newLargeInflowRatio = round(float(latest.get('newLargeInflowRatio'))*100,2)
        self.newLargeOutflowRatio = round(float(latest.get('newLargeOutflowRatio'))*100,2)
        self.mediumInflow = float(latest.get('mediumInflow'))
        self.mediumOutflow = float(latest.get('mediumOutflow'))
        self.mediumNetFlow = float(latest.get('mediumNetFlow'))
        self.mediumInflowRatio = round(float(latest.get('mediumInflowRatio'))*100,2)
        self.mediumOutflowRatio = round(float(latest.get('mediumOutflowRatio'))*100,2)
        self.smallInflow = float(latest.get('smallInflow'))
        self.smallOutflow = float(latest.get('smallOutflow'))
        self.smallNetFlow = float(latest.get('smallNetFlow'))
        self.smallInflowRatio = round(float(latest.get('smallInflowRatio'))*100,2)
        self.smallOutflowRatio = round(float(latest.get('smallOutflowRatio'))*100,2)
        self.majorInflow = float(latest.get('majorInflow'))
        self.majorInflowRatio = round(float(latest.get('majorInflowRatio'))*100,2)
        self.majorOutflow = float(latest.get('majorOutflow'))
        self.majorOutflowRatio = round(float(latest.get('majorOutflowRatio'))*100,2)
        self.majorNetFlow = float(latest.get('majorNetFlow'))
        self.retailInflow = float(latest.get('retailInflow'))
        self.retailInflowRatio = round(float(latest.get('retailInflowRatio'))*100,2)
        self.retailOutflow = float(latest.get('retailOutflow'))
        self.retailOutflowRatio = round(float(latest.get('retailOutflowRatio'))*100,2)

        self.data_dict = { 
            'super_inflow': self.superLargeInflow,
            'super_netflow': self.superLargeNetFlow,
            'super_outflow': self.superLargeOutflow,
            'large_inflow': self.largeInflow,
            'large_netflow': self.largeNetFlow,
            'large_outflow': self.largeOutflow,
            'newlarge_inflow': self.newLargeInflow,
            'newlarge_outflow': self.newLargeOutflow,
            'newlarge_netflow': self.newLargeNetFlow,
            'newlarge_inflow_ratio': self.newLargeInflowRatio,
            'newlarge_outflow_ratio': self.newLargeOutflowRatio,
            'medium_inflow': self.mediumInflow,
            'medium_outflow': self.mediumOutflow,
            'medium_netflow': self.mediumNetFlow,
            'medium_inflow_ratio': self.mediumInflowRatio,
            'medium_outflow_ratio': self.mediumOutflowRatio,
            'small_inflow': self.smallInflow,
            'small_outflow': self.smallOutflow,
            'small_netflow': self.smallNetFlow,
            'small_inflow_ratio': self.smallInflowRatio,
            'small_outflow_ratio': self.smallOutflowRatio,
            'major_inflow': self.majorInflow,
            'major_outflow': self.majorOutflow,
            'major_netflow': self.majorNetFlow,
            'major_inflow_ratio': self.majorInflowRatio,
            'major_outflow_ratio': self.majorOutflowRatio,
            'retail_inflow': self.retailInflow,
            'retail_inflow_ratio': self.retailInflowRatio,
            'retail_outflow': self.retailOutflow,
            'retail_outflow_ratio': self.retailOutflowRatio
        }


        self.as_dataframe = pd.DataFrame(self.data_dict, index=[0])
        self.as_dataframe['date'] = date