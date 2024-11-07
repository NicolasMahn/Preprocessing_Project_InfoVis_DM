import json
from collections import defaultdict, Counter

def analyze_property_values(geojson_file, max_categories=15):
    with open(geojson_file, 'r') as file:
        geojson_data = json.load(file)

    property_analysis = defaultdict(lambda: {
        'null_count': 0,
        'categories': Counter(),
        'numeric_range': [float('inf'), float('-inf')]
    })

    for feature in geojson_data['features']:
        for key, value in feature['properties'].items():
            if value is None:
                property_analysis[key]['null_count'] += 1
            else:
                property_analysis[key]['categories'][value] += 1
                if isinstance(value, (int, float)):
                    property_analysis[key]['numeric_range'][0] = min(property_analysis[key]['numeric_range'][0], value)
                    property_analysis[key]['numeric_range'][1] = max(property_analysis[key]['numeric_range'][1], value)

                # check if ints are mostly even or odd
                if isinstance(value, int):
                    property_analysis[key]['categories']['even'] += value % 2 == 0
                    property_analysis[key]['categories']['odd'] += value % 2 == 1

    for key, analysis in property_analysis.items():
        if len(analysis['categories']) > max_categories:
            analysis['categories'] = dict(analysis['categories'].most_common(max_categories))

    return property_analysis
