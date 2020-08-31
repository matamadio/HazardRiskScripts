import grequests
from tqdm import tqdm
import pandas as pd
from collections import defaultdict

"""
Instructions:

You will need to install requests, grequests, and pandas if you have not already done so.

conda install -c conda-forge requests grequests pandas

OR 

pip install requests grequests pandas
"""


def parse_response(url, resp, df):
    """Parse JSON response and insert into dataframe."""

    # Because we send the requests asynchronously, results may not
    # be returned in the order we sent it, so we get
    # the country code from the URL
    country_code = int(url.rsplit("/",1)[1].split(".")[0])

    row = {}
    for hazard in resp:
        # Hazard type
        haztype = hazard['hazardtype']['mnemonic']

        # Hazard Level
        hazlevel = hazard['hazardlevel']['mnemonic']
        row[haztype] = hazlevel
    # End for

    # Have to loop over columns to ensure values are put in the correct position
    for col in df.columns:
        df.loc[df.index == country_code, col] = row[col]
# End parse_response()


def failure_handler(r, exception):
    print("Warning! Request for {} failed!".format(r.url))


def collect_requests(responses, result_df):
    for idx, r in enumerate(tqdm(responses)):
        if (r is None) or (r.status_code != 200):
            continue

        parse_response(r.url, r.json(), result_df)
    # End for
# End collect_requests()


target_url = "http://thinkhazard.org/en/report/{}.json"
file_loc = "../../ADM0_TH.csv"
code_data = pd.read_csv(file_loc, sep=';')

adm0_codes = code_data['ADM0_CODE'].tolist()
adm0_urls = [target_url.format(adm_code) for adm_code in adm0_codes]

# List of things to do asynchronously
url_responses = [grequests.get(url) for url in adm0_urls]

result_df = pd.DataFrame(columns=['FL', 'UF', 'CF', 'EQ', 'LS', 'TS', 'VA', 'CY', 'DG', 'EH', 'WF'],
                         index=adm0_codes)
result_df.index.name = 'country_code'

# Send out asynchronous requests
responses = grequests.imap(url_responses, exception_handler=failure_handler, size=4)
collect_requests(responses, result_df)

print(result_df)
result_df.to_csv('collated_result.csv', sep=';')
