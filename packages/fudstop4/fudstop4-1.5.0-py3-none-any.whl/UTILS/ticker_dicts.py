import os
from dotenv import load_dotenv
load_dotenv()

ticker_hooks_dict = {
    'WFC': os.environ.get('financial_services', '') + str(1381376169018134558),
    'V': os.environ.get('financial_services', '') + str(1381376292586393635),
    'USB': os.environ.get('financial_services', '') + str(1381376515031302294),
    'PNC': os.environ.get('financial_services', '') + str(1381376618249060373),
    'GS': os.environ.get('financial_services', '') + str(1381376946591760555),
    'SCHW': os.environ.get('financial_services', '') + str(1381377025964642547),
    'PYPL': os.environ.get('financial_services', '') + str(1381377208374792383),
    'MS': os.environ.get('financial_services', '') + str(1381377327262601216),
    'MA': os.environ.get('financial_services', '') + str(1381377422032769095),
    'JPM': os.environ.get('financial_services', '') + str(1381377521110614116),
    'C': os.environ.get('financial_services', '') + str(1381377615830712421),
    'BX': os.environ.get('financial_services', '') + str(1381377719966633995),
    'BLK': os.environ.get('financial_services', '') + str(1381377779341459537),
    'BAC': os.environ.get('financial_services', '') + str(1381377858043121805),
    'AXP': os.environ.get('financial_services', '') + str(1381377932819304589),
    'COIN': os.environ.get('financial_services', '') + str(1394222646836592782),
    'MARA': os.environ.get('financial_services', '') + str(1392232621022515335),

    'BP': os.environ.get('energy', '') + str(1381379873825624114),
    'CVE': os.environ.get('energy', '') + str(1381380033733595246),
    'LNG': os.environ.get('energy', '') + str(1381380302345342996),
    'CVX': os.environ.get('energy', '') + str(1381380384364953650),
    'XOM': os.environ.get('energy', '') + str(1381380460575461397),
    'DVN': os.environ.get('energy', '') + str(1381380595401097377),
    'ET': os.environ.get('energy', '') + str(1381380669850124328),
    'OXY': os.environ.get('energy', '') + str(1381380764083683389),
    'PBR': os.environ.get('energy', '') + str(1381380843066364065),



    'GOLD': os.environ.get('basic_materials', '') + str(1381383071181308034),
    'NEM': os.environ.get('basic_materials', '') + str(1381383291210301641),


    'JNJ': os.environ.get('healthcare', '') + str(1381381874617942177),
    'MRK': os.environ.get('healthcare', '') + str(1381381926539231333),
    'UNH': os.environ.get('healthcare', '') + str(1381382183985348818),
    'PFE': os.environ.get('healthcare', '') + str(1381382248359526400),
    'GILD': os.environ.get('healthcare', '') + str(1381382396644954112),
    'LLY': os.environ.get('healthcare', '') + str(1381382477074927638),
    'CVS': os.environ.get('healthcare', '') + str(1381382564224434307),
    'ABBV': os.environ.get('healthcare', '') + str(1381382647611396096),
    'BMY': os.environ.get('healthcare', '') + str(1381382767857897493),



    'AAL': os.environ.get('industrials', '') + str(1381394281045954650),
    'BA': os.environ.get('industrials', '') + str(1381394320313024583),
    'CCL': os.environ.get('industrials', '') + str(1381394364483502120),
    'CSX': os.environ.get('industrials', '') + str(1381394426194165781),
    'DAL': os.environ.get('industrials', '') + str(1381394461631975485),
    'FDX': os.environ.get('industrials', '') + str(1381394520502960340),
    'GE': os.environ.get('industrials', '') + str(1381394559359254538),
    'LMT': os.environ.get('industrials', '') + str(1381394613012791316),
    'LUV': os.environ.get('industrials', '') + str(1381394654960029798),
    'MMM': os.environ.get('industrials', '') + str(1381394699545477170),
    'NCLH': os.environ.get('industrials', '') + str(1381394749277208577),
    'RTX': os.environ.get('industrials', '') + str(1381394794378432623),
    'UPS': os.environ.get('industrials', '') + str(1381394840020979732),
    'UAL': os.environ.get('industrials', '') + str(1381394885554208878),
    'ZIM': os.environ.get('industrials', '') + str(1381394943880466573),



    'AMZN': os.environ.get('ai', '') + str(1381381389785501706),
    'MSFT': os.environ.get('ai', '') + str(1381381464821727393),
    'NVDA': os.environ.get('ai', '') + str(1381381539065237685),
    'PLTR': os.environ.get('ai', '') + str(1381381594396229713),
    'TSLA': os.environ.get('ai', '') + str(1381381669411491920),



    'PCG': os.environ.get('utilities', '') + str(1381384077399162890),
    'NEE': os.environ.get('utilities', '') + str(1381384286686416916),
    'COST': os.environ.get('consumer_discretionary', '') + str(1381392607640555560),
    'KO': os.environ.get('consumer_discretionary', '') + str(1381392746379481240),
    

    'AMC': os.environ.get('consumer_staples', '') + str(1381388332553998396),
    'BABA': os.environ.get('consumer_staples', '') + str(1381388389605179483),
    'BBY': os.environ.get('consumer_staples', '') + str(1381388441622806590),
    'CHWY': os.environ.get('consumer_staples', '') + str(1381388494668304394),
    'CMG': os.environ.get('consumer_staples', '') + str(1381388564323110943),
    'CVNA': os.environ.get('consumer_staples', '') + str(1381388618471440394),
    'DKNG': os.environ.get('consumer_staples', '') + str(1381388672003211314),
    'ETSY': os.environ.get('consumer_staples', '') + str(1381388717129732136),
    'EBAY': os.environ.get('consumer_staples', '') + str(1381388790031061164),
    'GM': os.environ.get('consumer_staples', '') + str(1381388835753296033),
    'GME': os.environ.get('consumer_staples', '') + str(1381388878501642402),

    'HD': os.environ.get('consumer_staples', '') + str(1381388920419520674),
    'JD': os.environ.get('consumer_staples', '') + str(1381388956070838342),
    'LI': os.environ.get('consumer_staples', '') + str(1381389018394005544),
    'LOW': os.environ.get('consumer_staples', '') + str(1381389058785280110),
    'LULU': os.environ.get('consumer_staples', '') + str(1381389105249648842),
    'LVS': os.environ.get('consumer_staples', '') + str(1381389148514029568),
    'MCD': os.environ.get('consumer_staples', '') + str(1381389201211134022),
    'M': os.environ.get('consumer_staples', '') + str(1381389250129563739),
    'MGM': os.environ.get('consumer_staples', '') + str(1381389297239719946),
    'NKE': os.environ.get('consumer_staples', '') + str(1381389357801279700),
    'ONON': os.environ.get('consumer_staples', '') + str(1381389398955921448),
    'PDD': os.environ.get('consumer_staples', '') + str(1381389443214344242),
    'SBUX': os.environ.get('consumer_staples', '') + str(1381389520494137394),
    'VFC': os.environ.get('consumer_staples', '') + str(1381389572310827119),
    'W': os.environ.get('consumer_staples', '') + str(1381389623023898765),
    'XPEV': os.environ.get('consumer_staples', '') + str(1381389664253906944),
    'CZR': os.environ.get('consumer_staples', '') + str(1381389702225072232),


    'NFLX': os.environ.get('communication_services', '') + str(1382007472037822514),
    'BIDU': os.environ.get('communication_services', '') + str(1381395878459474061),
    'BILI': os.environ.get('communication_services', '') + str(1381395923191468142),
    'DASH': os.environ.get('communication_services', '') + str(1381395968112726220),
    'CMCSA': os.environ.get('communication_services', '') + str(1381396020591595560),
    'DIS': os.environ.get('communication_services', '') + str(1381396063604183183),
    'GOOGL': os.environ.get('communication_services', '') + str(1381396136136278126),
    'GOOG': os.environ.get('communication_services', '') + str(1381396196077080697),
    'PINS': os.environ.get('communication_services', '') + str(1381396260627415162),
    'RBLX': os.environ.get('communication_services', '') + str(1381396303581286553),
    'RDDT': os.environ.get('communication_services', '') + str(1381396345390108692),
    'ROKU': os.environ.get('communication_services', '') + str(1381396396766134312),
    'SPOT': os.environ.get('communication_services', '') + str(1381396435697668227),
    'T': os.environ.get('communication_services', '') + str(1381396490366488697),
    'VZ': os.environ.get('communication_services', '') + str(1381396526462402610),


    'ADBE': os.environ.get('technology', '') + str(1381384580572905502),
    'AMD': os.environ.get('technology', '') + str(1381384636558479360),
    'AAPL': os.environ.get('technology', '') + str(1381384717777108992),
    'AMAT': os.environ.get('technology', '') + str(1381384783937929399),
    'AVGO': os.environ.get('technology', '') + str(1381384866079309834),
    'CSCO': os.environ.get('technology', '') + str(1381384927572004885),
    'INTC': os.environ.get('technology', '') + str(1381385018529681529),
    'IBM': os.environ.get('technology', '') + str(1381385080701845504),
    'MU': os.environ.get('technology', '') + str(1381385204953911628),
    'QCOM': os.environ.get('technology', '') + str(1381385297358618764),
    'AI': os.environ.get('technology', '') + str(1381385367143579668),
    'AFRM': os.environ.get('technology', '') + str(1381385487079440546),
    'ARM': os.environ.get('technology', '') + str(1381385690238947379),
    'ASTS': os.environ.get('technology', '') + str(1381385839472414811),
    'CRWD': os.environ.get('technology', '') + str(1381385933839929487),
    'DDOG': os.environ.get('technology', '') + str(1381385968724217957),
    'DOCU': os.environ.get('technology', '') + str(1381386039721066626),
    'HOOD': os.environ.get('technology', '') + str(1381386080699420885),
    'HPQ': os.environ.get('technology', '') + str(1381386146902315008),
    'LYFT': os.environ.get('technology', '') + str(1381386224836542656),
    'META': os.environ.get('technology', '') + str(1381386269925310514),
    'MDB': os.environ.get('technology', '') + str(1381386357947109560),
    'MRVL': os.environ.get('technology', '') + str(1381386429829087232),
    'MSTR': os.environ.get('technology', '') + str(1381386483591676014),
    'NET': os.environ.get('technology', '') + str(1381386582950547546),
    'ON': os.environ.get('technology', '') + str(1381386639896744137),
    'ORCL': os.environ.get('technology', '') + str(1381386774806532236),
    'SHOP': os.environ.get('technology', '') + str(1381386848563101839),
    'SMCI': os.environ.get('technology', '') + str(1381386896034369576),
    'SNOW': os.environ.get('technology', '') + str(1381386950396612752),
    'U': os.environ.get('technology', '') + str(1381386996991131799),
    'UBER': os.environ.get('technology', '') + str(1381387046333186058),
    'TSM': os.environ.get('technology', '') + str(1381387087512604762),
    'TXN': os.environ.get('technology', '') + str(1381387135097110568),
    'ZM': os.environ.get('technology', '') + str(1381387209051082803),
    

    'XSP': os.environ.get('etfs_unknown', '') + str(1394501829689212929),
    'VIX': os.environ.get('etfs_unknown', '') + str(1394502350395150438),
    'UUP': os.environ.get('etfs_unknown', '') + str(1394502350395150438),

    'DJT': os.environ.get('communication_services', '') + str(1394500891289194547)
}




tickers_dict = {'AMC': 1381388332553998396, 'BABA': 1381388389605179483, 'BBY': 1381388441622806590, 'CHWY': 1381388494668304394, 'CMG': 1381388564323110943, 'CVNA': 1381388618471440394, 'DKNG': 1381388672003211314, 'ETSY': 1381388717129732136, 'EBAY': 1381388790031061164, 'GM': 1381388835753296033, 'GME': 1381388878501642402, 'HD': 1381388920419520674, 'JD': 1381388956070838342, 'LI': 1381389018394005544, 'LOW': 1381389058785280110, 'LULU': 1381389105249648842, 'LVS': 1381389148514029568, 'MCD': 1381389201211134022, 'M': 1381389250129563739, 'MGM': 1381389297239719946, 'NKE': 1381389357801279700, 'ONON': 1381389398955921448, 'PDD': 1381389443214344242, 'SBUX': 1381389520494137394, 'VFC': 1381389572310827119, 'W': 1381389623023898765, 'XPEV': 1381389664253906944, 'CZR': 1381389702225072232,
'ADBE': 1381384580572905502, 'AMD': 1381384636558479360, 'AAPL': 1381384717777108992, 'AMAT': 1381384783937929399, 'AVGO': 1381384866079309834, 'CSCO': 1381384927572004885, 'INTC': 1381385018529681529, 'IBM': 1381385080701845504, 'MU': 1381385204953911628, 'QCOM': 1381385297358618764, 'AI': 1381385367143579668, 'AFRM': 1381385487079440546, 'ARM': 1381385690238947379, 'ASTS': 1381385839472414811, 'CRWD': 1381385933839929487, 'DDOG': 1381385968724217957, 'DOCU': 1381386039721066626, 'HOOD': 1381386080699420885, 'HPQ': 1381386146902315008, 'LYFT': 1381386224836542656, 'META': 1381386269925310514, 'MDB': 1381386357947109560, 'MRVL': 1381386429829087232, 'MSTR': 1381386483591676014, 'NET': 1381386582950547546, 'ON': 1381386639896744137, 'ORCL': 1381386774806532236, 'SHOP': 1381386848563101839, 'SMCI': 1381386896034369576, 'SNOW': 1381386950396612752, 'U': 1381386996991131799, 'UBER': 1381387046333186058, 'TSM': 1381387087512604762, 'TXN': 1381387135097110568, 'ZM': 1381387209051082803,'AMZN': 1381381389785501706, 'MSFT': 1381381464821727393, 'NVDA': 1381381539065237685, 'PLTR': 1381381594396229713, 'TSLA': 1381381669411491920,'JNJ': 1381381874617942177, 'MRK': 1381381926539231333, 'UNH': 1381382183985348818, 'PFE': 1381382248359526400, 'GILD': 1381382396644954112, 'LLY': 1381382477074927638, 'CVS': 1381382564224434307, 'ABBV': 1381382647611396096, 'BMY': 1381382767857897493,'GOLD': 1381383071181308034, 'NEM': 1381383291210301641,'BP': 1381379873825624114, 'CVE': 1381380033733595246, 'LNG': 1381380302345342996, 'CVX': 1381380384364953650, 'XOM': 1381380460575461397, 'DVN': 1381380595401097377, 'ET': 1381380669850124328, 'OXY': 1381380764083683389, 'PBR': 1381380843066364065,'WFC': 1381376169018134558, 'V': 1381376292586393635, 'USB': 1381376515031302294, 'PNC': 1381376618249060373, 'GS': 1381376946591760555, 'SCHW': 1381377025964642547, 'PYPL': 1381377208374792383, 'MS': 1381377327262601216, 'MA': 1381377422032769095, 'JPM': 1381377521110614116, 'C': 1381377615830712421, 'BX': 1381377719966633995, 'BLK': 1381377779341459537, 'BAC': 1381377858043121805, 'AXP': 1381377932819304589}