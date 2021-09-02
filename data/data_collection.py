import csv
import requests
import sys
import yaml
import pandas as pd
import time
import os

def main():
    # Read the configuration file
    with open("config.yaml", "r") as ymlfile:
        config = yaml.safe_load(ymlfile)

    url = f'{config["prometheus_server"]}/api/v1/query_range'

    columns = ['metric', 'intf', 'value', 'timestamp']

    data = {col:[] for col in columns}

    for idx, metric in enumerate(config["metrics"]):

        response = requests.get(url,
                params={'query': metric,
                        'start': config["initial"],
                        'end': config["end"],
                        'step': config["step"]
                        })

        print(response.request.url)

        results = response.json()['data']['result']

        for res in results:
            if 'os_name' not in res['metric']:
                assert res['metric']['agent'] == '127.0.0.1'
                continue

            intf = res['metric'].get('ifname', None)
            
            if intf == None:
                continue
            
            for data_point in res['values']:
                data['metric'].append(idx)
                data['intf'].append(intf)
                data['value'].append(float(data_point[1]))
                data['timestamp'].append(float(data_point[0]))

    df = pd.DataFrame(data)
    print(df.head())
    df.to_csv('data.csv', index=False)

if __name__ == '__main__':
    main()