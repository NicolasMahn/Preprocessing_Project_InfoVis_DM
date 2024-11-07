import csv
from collections import defaultdict, Counter


def analyze_csv_values(csv_file, max_categories=10):
    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)

        property_analysis = defaultdict(lambda: {
            'null_count': 0,
            'categories': Counter(),
            'numeric_range': [float('inf'), float('-inf')]
        })

        for row in reader:
            for key, value in row.items():
                if value == '' or value is None:
                    property_analysis[key]['null_count'] += 1
                else:
                    property_analysis[key]['categories'][value] += 1
                    try:
                        numeric_value = float(value)
                        property_analysis[key]['numeric_range'][0] = min(property_analysis[key]['numeric_range'][0],
                                                                         numeric_value)
                        property_analysis[key]['numeric_range'][1] = max(property_analysis[key]['numeric_range'][1],
                                                                         numeric_value)
                    except ValueError:
                        pass

        for key, analysis in property_analysis.items():
            if len(analysis['categories']) > max_categories:
                analysis['categories'] = dict(analysis['categories'].most_common(max_categories))

    return property_analysis