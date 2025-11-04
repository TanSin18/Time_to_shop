"""
Objective: To predict the likelihood of Bed Bath Customer making their next purchase within 90 days from the day they made their last purchase.

Author: Tanmay Sinnarkar (tanmay.sinnarkar@bedbath.com)

"""


from google.oauth2 import service_account
from google.cloud import bigquery
from google.cloud import bigquery_storage
import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
import pickle
import logging
from datetime import date


logger = logging.getLogger()
logger.setLevel(logging.INFO)

key_path = '/home/jupyter/d00_key.json'
credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)


def get_client(credentials):
   
    bq_client = bigquery.Client(credentials=credentials,
                                project=credentials.project_id)
    bqstorageclient = bigquery_storage.BigQueryReadClient(
        credentials=credentials)
    return bq_client, bqstorageclient


def copy_results_to_bq(data, output_name, credentials):
    bq_client, bqstorageclient = get_client(credentials=credentials)
    logging.info("Copying results to BQ...")
    data.to_gbq(destination_table=f'SANDBOX_ANALYTICS.{output_name}',
                project_id=credentials.project_id,
                if_exists='append',
                table_schema=[ 
                               {'name': 'CUSTOMER_ID','type': 'INTEGER'},
                               {'name': 'PREVIOUS_PURCHASE','type': 'DATETIME'},
                               {'name': 'DECILE','type': 'INTEGER'},
                               {'name': 'P','type': 'FLOAT'}],
                credentials=credentials)
    logging.info("Results exported successfully.")
    

def data_upload(QUERY):
    key_path = '/home/jupyter/d00_key.json'
    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )

    bq_client = bigquery.Client(credentials=credentials,
                                project=credentials.project_id)
    bqstorageclient = bigquery_storage.BigQueryReadClient(
        credentials=credentials)

    data = bq_client.query(QUERY).result().to_dataframe(
        bqstorage_client=bqstorageclient)

    for col in data.columns:
        if 'DECILE' in col:
            data[col].fillna(11, inplace=True)
        elif '_R' in col and 'DECILE' not in col:
            data[col].fillna(366, inplace=True)
        else:
            data[col].fillna(0, inplace=True)
    data.SALES_6M.loc[data.SALES_6M < 0] = 0
    data.COUPON_EXPENSE_6M.loc[data.COUPON_EXPENSE_6M < 0] = 0

    key = ['CUSTOMER_ID', 'ADDRESS_ID']
    data[key] = data[key].astype("object")
    key1 = [
        'SALES_6M', 'COUPON_EXPENSE_6M', 'BUYS_Q_03', 'COUPON_Q_03',
        'PH_MREDEEM90D', 'PH_PFREQ90D', 'PH_CFREQ90D',
        'BBB_INSTORE_RFM_DECILE', 'BBB_ECOM_R_DECILE',
        'BBB_OFFCOUPON_RFM_DECILE', 'PCT_TXNS_ON_MKD_DISC'
    ]
    data[key1] = data[key1].astype('int')
    return data


def extratrees_predict(data, model):
    """
    Objective: To predict the likelihood of Bed Bath Customer making their next purchase     within 90 days from the day they made their last purchase.

    Author: Tanmay Sinnarkar (tanmay.sinnarkar@bedbath.com)

    """
    Score1 = data[[
        'SALES_6M', 'FREQUENCY_6M', 'BUYS_Q_03', 'COUPON_Q_03',
        'PH_MREDEEM90D', 'PH_PFREQ90D', 'PH_CFREQ90D',
        'BBB_INSTORE_RFM_DECILE', 'BBB_ECOM_R_DECILE',
        'BBB_OFFCOUPON_RFM_DECILE', 'NUM_PERIODS', 'NUM_PRODUCT_GROUPS',
        'PRESENCE_OF_CHILD', 'MARITAL_STAT'
    ]]
    predicted = model.predict(Score1)

    predicted_df = pd.DataFrame(data=predicted,
                                columns=['y_hat'],
                                index=data.index.copy())
    probn = model.predict_proba(Score1)

    prob1 = probn[:, 1]
    prob0 = probn[:, 0]
    Proba = pd.DataFrame(data=prob1, columns=['P'], index=data.index.copy())
    df_out1 = pd.merge(data[['CUSTOMER_ID', 'PREVIOUS_PURCHASE']],
                       Proba,
                       how='left',
                       left_index=True,
                       right_index=True)
    cut_labels_10 = ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']

    cut_bins = [
        0.00, 0.19662877, 0.21054794, 0.25123934, 0.26712146, 0.42682036,
        0.493293, 0.59348687, 0.67486295, 0.77079006, 1
    ]
    df_out1['DECILE'] = pd.cut(df_out1['P'],
                               bins=cut_bins,
                               labels=cut_labels_10)
    return df_out1



def main():
    QUERY = """SELECT * FROM `dw-bq-data-d00.SANDBOX_ANALYTICS.TTS_Production`"""
    model = pickle.load(open('finalized_model.sav', 'rb'))
    data = data_upload(QUERY)
    output = extratrees_predict(data, model)
    output.reset_index(drop=True, inplace=True)
    output['CUSTOMER_ID'] = output['CUSTOMER_ID'].astype(int)
    output['PREVIOUS_PURCHASE']=pd.to_datetime(output['PREVIOUS_PURCHASE'])
    output['DECILE'] = output['DECILE'].astype(int)
    output['P'] = output['P'].astype(float)
    output_name = 'time_to_shop'
    copy_results_to_bq(output, output_name, credentials)


if __name__ == "__main__":
    main()
