import pickle
import numpy as np
import sklearn
import numpy
import scipy

bundle_recommender = pickle.load(open('toy_bundle_recommenders.pkl','rb'), encoding='utf-8')

# utilities for feature engineering from inputs

def determine_group_size_group(num_of_adults,num_of_childrens):
    size = num_of_adults + num_of_childrens
    if size < 1:
        return None
    if size == 1:
        return 1
    elif size == 2:
        return 2
    else:
        return 3

def determine_los_group(num_nights):
    if num_nights < 1:
        return -1
    if num_nights <= 2:
        return 1
    elif num_nights <= 4:
        return 2
    else:
        return 3


def create_feature_vector(
    num_of_adults:int,
    num_of_childrens: int,
    num_of_infants: int,
    arrival_month: int,
    num_nights: int,
    weekend: bool,
    holiday: bool,
    customer_origin: str,
    features: list[str],
    month_map: dict,
    kid_map:dict,
    custom_origin_map:dict
):
    vector = []
    for feature in features:
        if feature == 'NUMBEROFADULT':
            vector.append(num_of_adults)
        elif feature == 'NUMBEROFCHILD':
            vector.append(num_of_childrens)
        elif feature == 'NUMBEROFINFANT':
            vector.append(num_of_infants)
        elif feature == 'NUMNIGHTS':
            vector.append(num_nights)
        elif feature == 'ARRIVALMONTH':
            vector.append(month_map[arrival_month])
        elif feature == 'CUSTOMER_ORIGIN':
            vector.append(custom_origin_map[customer_origin])
        elif feature == 'HOLIDAY':
            vector.append(holiday)
        elif feature == 'WEEKEND':
            vector.append(weekend)
        elif feature == 'ACTUAL_GROUP_SIZE':
            vector.append(num_of_adults+num_of_childrens)
        elif feature == 'GROUP_SIZE':
            vector.append(determine_group_size_group(num_of_adults,num_of_childrens))
        elif feature == 'LOS_GROUP':
            vector.append(determine_los_group(num_nights))
        elif feature == 'KID':
            if num_of_childrens + num_of_infants > 0:
                vector.append(kid_map['with-kid'])
            else:
                vector.append(kid_map['without-kid'])
    return np.array(vector)

# the main function
def bundle_reccommendation(
    hotel_name: str,
    num_of_adults:int,
    num_of_childrens: int,
    num_of_infants: int,
    arrival_month: int,
    num_nights: int,
    weekend: bool,
    holiday: bool,
    customer_origin: str
):
    recommenders = bundle_recommender[bundle_recommender['hotel_name'] == hotel_name]
    recommended_bundles = []
    for _, recommender in recommenders.iterrows():
        features = recommender['features']
        maps = recommender['maps']
        custom_origin_map = {}
        for e in maps['custom_origin_map']:
            custom_origin_map[e] = len(custom_origin_map)
        month_map = {}
        for e in maps['month_map']:
            month_map[int(e.split('/')[1])] = len(month_map)
        kid_map = {}
        for e in maps['kid_map']:
            kid_map[e] = len(kid_map)

        vector = create_feature_vector(
            num_of_adults=num_of_adults,
            num_of_childrens=num_of_childrens,
            num_of_infants=num_of_infants,
            arrival_month=arrival_month,
            num_nights=num_nights,
            weekend=weekend,
            holiday=holiday,
            customer_origin=customer_origin,
            features=features,
            month_map=month_map,
            kid_map=kid_map,
            custom_origin_map=custom_origin_map
        )
        model = recommender['model']
        recommended_bundles.append(
            {
            'bundle': recommender['bundle'].split('\n'),
             'prob': model.predict_proba(vector.reshape(1,-1))[0][0]
            }
        )
    return recommended_bundles
def upsale(
    hotel_name: str,
    num_of_adults:int,
    num_of_childrens: int,
    num_of_infants: int,
    arrival_month: int,
    num_nights: int,
    weekend: bool,
    holiday: bool,
    customer_origin: str,
    bought_items: list[str]
):
    recommended_bundles = bundle_reccommendation(
                            hotel_name=hotel_name,
                            num_of_adults=num_of_adults,
                            num_of_childrens=num_of_childrens,
                            num_of_infants=num_of_infants,
                            arrival_month=arrival_month,
                            num_nights=num_nights,
                            weekend=weekend,
                            holiday=holiday,
                            customer_origin=customer_origin
                        )
    recommended_bundles = [
        {
            'bundle': set(e['bundle']),
            'prob': e['prob'],
            'score': 0.0
        } for e in recommended_bundles
    ]
    bought_items = set(bought_items)
    for bundle in recommended_bundles:
        if bought_items == bundle['bundle']:
            continue
        for item in bought_items:
            if item in bundle['bundle']:
                bundle['score'] += bundle['prob']
    recommended_bundles = [bundle for bundle in recommended_bundles if bundle['score'] > 0]
    recommended_bundles.sort(key=lambda e: e['score'],reverse=True)

    return recommended_bundles
    
if __name__ == "__main__":
    # here is an example for getting bundle recommendation
    recommended_bundles = bundle_reccommendation(
        hotel_name='Vinpearl Wonderworld Phú Quốc', # refer to the cell belows for possible values
        num_of_adults=2,
        num_of_childrens=0,
        num_of_infants=0,
        arrival_month=4,
        num_nights=2,
        weekend=True,
        holiday=False,
        customer_origin='North' # or 'South', or 'Midle', or 'Oversea'
    )
    print(recommended_bundles)