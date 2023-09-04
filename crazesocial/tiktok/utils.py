

def get_followers_graph_data(followers_graph_data):
    pass

def get_best_monthly_engagement_data(month_engagement_data):
    cleaned_data = []
    labels = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']

    for engagement_data in month_engagement_data:
        key = list(engagement_data.keys())[0]
        new_key = key.split('_')[0]

        results_data = {
            'name': new_key,
            'data': []
        }

        engagements_gr = engagement_data.get(key)

        for label in labels:

            try:
                gr = engagements_gr[labels.index(label)]
            except:
                gr = {
                    "month": label,
                    "engagement": 0.0,
                }
            
            if gr.get("month") in labels:
                results_data['data'].append(float(gr.get("engagement", 0.0)))
            else:
                results_data['data'].append(0.0)

        cleaned_data.append(results_data)


    return {
        'labels': labels,
        'data': cleaned_data
    }

def get_monthly_interations_data(monthly_interactions_data):
    cleaned_data = []
    labels = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']

    for interaction_data in monthly_interactions_data:
        key = list(interaction_data.keys())[0]
        new_key = key.split('_')[0]

        results_data = {
            'name': new_key,
            'data': []
        }

        interactions_gr = interaction_data.get(key)

        for label in labels:

            try:
                gr = interactions_gr[labels.index(label)]
            except:
                gr = {
                    "month": label,
                    "interactions": 0,
                }
            
            if gr.get("month") in labels:
                results_data['data'].append(int(gr.get("interactions", 0)))
            else:
                results_data['data'].append(0)

        cleaned_data.append(results_data)

    return {
        'labels': labels,
        'data': cleaned_data
    }


def get_weekly_distribution_of_data(analytics_data, inner_key):
    cleaned_data = []
    
    # WEEKS RANGES FROM FEB-2022 TO MAY 2022
    labels = [
        '31-Jan-2022 to 06-Feb-2022', '07-Feb-2022 to 13-Feb-2022', '14-Feb-2022 to 20-Feb-2022', '21-Feb-2022 to 27-Feb-2022', 

        '28-Feb-2022 to 06-Mar-2022', '07-Mar-2022 to 13-Mar-2022', '14-Mar-2022 to 20-Mar-2022', '21-Mar-2022 to 27-Mar-2022',

        '28-Mar-2022 to 03-Apr-2022', '04-Apr-2022 to 10-Apr-2022', '11-Apr-2022 to 17-Apr-2022',  '18-Apr-2022 to 24-Apr-2022', 
        '25-Apr-2022 to 01-May-2022',

        '02-May-2022 to 08-May-2022', '09-May-2022 to 15-May-2022', '16-May-2022 to 22-May-2022', '23-May-2022 to 29-May-2022', 
        '30-May-2022 to 05-Jun-2022'
    ]

    for data in analytics_data:
        key = list(data.keys())[0]
        new_key = key.split('_')[0]

        results_data = {
            'name': new_key,
            'data': [0] * len(labels)
        }

        data_gr = data.get(key)

        for label in labels:
            try:
                gr = data_gr[labels.index(label)]
            except:
                gr = {
                    "week": label,
                    f"{inner_key}": 0,
                }
            
            if gr.get("week") in labels:
                if inner_key == "engagement":
                    results_data['data'][labels.index(gr.get("week"))] = float(gr.get(f"{inner_key}", 0))
                elif inner_key == "interactions" or inner_key == "followers":
                    results_data['data'][labels.index(gr.get("week"))] = int(gr.get(f"{inner_key}", 0))

        cleaned_data.append(results_data)

    return {
        'labels': labels,
        'data': cleaned_data
    }