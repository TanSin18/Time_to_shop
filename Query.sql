##Change
CREATE OR REPLACE TABLE `dw-bq-data-d00.SANDBOX_ANALYTICS.TTS_Production`
as
select
CUSTOMER_ID
, ADDRESS_ID
, PREVIOUS_PURCHASE
, SALES_6M
, FP
, COUPON_EXPENSE_6M
, FREQUENCY_6M
, pct_transactions_on_markdowns_discounts as PCT_TXNS_ON_MKD_DISC
, BUYS_Q_03
, COUPON_Q_03
, PH_PFREQ90D
, PH_CFREQ90D
, PH_MREDEEM90D
, beyond_INSTORE_recency_frequency_monetary_DECILE as BBB_INSTORE_RFM_DECILE
, beyond_ECOM_recency_DECILE as BBB_ECOM_R_DECILE
, beyond_OFFCOUPON_recency_frequency_monetary_DECILE as BBB_OFFCOUPON_RFM_DECILE
, number_of_periods_purchased as NUM_PERIODS
, number_of_product_groups_purchased as NUM_PRODUCT_GROUPS
, case when A_A8622N_PRESENCE_OF_CHILD_Y = 1 then 1
	 		when A_A8622N_PRESENCE_OF_CHILD_N = 1 then 2
			else 99 end as PRESENCE_OF_CHILD		 
, case when A_A9509N_EDU_1ST_1 = 1 then 1
	 		when A_A9509N_EDU_1ST_2 = 1 then 2
			when A_A9509N_EDU_1ST_3 = 1 then 3
			when A_A9509N_EDU_1ST_4 = 1 then 4
			else 99 end as EDU_1ST
, case when A_A8609N_MARITAL_STAT_HH_M_A = 1 then 1
	 		when A_A8609N_MARITAL_STAT_HH_S_B = 1 then 2
			else 99 end as MARITAL_STAT
from
(
select 
a.customer_id
, a.address_id
, a.previous_purchase
, a.sales_6M
, a.coupon_expense_6M
, a.Frequency_6M
, a.FP,
SEA.BUYS_Q_03,
SEA.COUPON_Q_03,
PRO.PH_PFREQ90D, 
PRO.PH_CFREQ90D, 
PRO.PH_REDEEM90D, 
PRO.PH_MREDEEM90D, 
PRO.PH_MCPSALE90D,
RFM.beyond_INSTORE_recency_frequency_monetary_DECILE,
RFM.beyond_ecom_recency_decile,
RFM.beyond_OFFCOUPON_recency_frequency_monetary_DECILE,
ADS.number_of_product_groups_purchased, 
ADS.number_of_periods_purchased,
ADS.pct_transactions_on_markdowns_discounts, 
D.A_A8622N_PRESENCE_OF_CHILD_Y,
D.A_A8622N_PRESENCE_OF_CHILD_N,
D.A_A8609N_MARITAL_STAT_HH_M_A,
D.A_A8609N_MARITAL_STAT_HH_S_B,
D.A_A9509N_EDU_1ST_1,
D.A_A9509N_EDU_1ST_2,
D.A_A9509N_EDU_1ST_3,
D.A_A9509N_EDU_1ST_4
From
(
SELECT 
a.customer_id,
c.address_id,
a.previous_purchase,
a.FP,
sum(sales) as sales_6M,
sum(coupon_expense) as coupon_expense_6M,
case when count(DISTINCT b.transaction_booked_date)>20 then 20 else count(DISTINCT b.transaction_booked_date) end AS  Frequency_6M
From
(
select 
customer_id,
transaction_booked_date as previous_purchase,
concat(cast(FORMAT_DATE("%Y", DATE_SUB(transaction_booked_date, INTERVAL 4 MONTH)) AS String),"P",cast(DATE_SUB(transaction_booked_date, INTERVAL 4 MONTH) as string format('MM'))) as FP,
from 
(
select
customer_id,
transaction_booked_date,
ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY transaction_booked_date desc) as time_rank
from `dw-bq-data-p00.ANALYTICAL.sales_datamart_sales_transaction_sum` a
join dw-bq-data-p00.EDW_MCF_VW.CUSTOMER_TXN_XREF b 
on a.transaction_guid=b.trans_id 
and b.customer_id > 0
where concept_format_id = 1
and gross_sales is not null
and transaction_booked_date between DATE_SUB(current_date(), INTERVAL 1 YEAR) and current_date()
and   (SALES_TRANSACTION_TYPE_CODE = 'S' or SALES_TRANSACTION_TYPE_CODE = 'M')
) a
where time_rank=1
) a
left join
(
select  b.customer_id, 
		a.transaction_booked_date,
		sum(sales) as sales,
		sum(coupon_expense) as coupon_expense		
		from `dw-bq-data-p00.ANALYTICAL.sales_datamart_sales_transaction_sum` a
        join dw-bq-data-p00.EDW_MCF_VW.CUSTOMER_TXN_XREF b 
        on a.transaction_guid=b.trans_id 
        and b.customer_id > 0
        where concept_format_id = 1
        and gross_sales is not null
        and   (SALES_TRANSACTION_TYPE_CODE = 'S' or SALES_TRANSACTION_TYPE_CODE = 'M')
        group by 1,2
) b		 
on a.customer_id=b.customer_id 
and b.transaction_booked_date between DATE_SUB(a.previous_purchase, INTERVAL 6 MONTH) and a.previous_purchase

LEFT JOIN 
(SELECT customer_id, address_id FROM
dw-bq-data-p00.EDW_MCF_VW.CUSTOMER_CURR
WHERE customer_purge_ind = 'N'
AND customer_id > 0
AND address_id > 0) c ON a.customer_id = c.customer_id
group by 1,2,3,4
) a

Left Join `dw-bq-data-p00.ANALYTICAL.model_factory_address_seasonality` SEA on a.address_id=SEA.address_guid and a.FP=SEA.fiscal_period_name

Left Join `dw-bq-data-p00.ANALYTICAL.model_factory_address_promo_history_variables` PRO on a.address_id=PRO.address_guid and a.FP=PRO.fiscal_period_name

Left Join `dw-bq-data-p00.ANALYTICAL.model_factory_address_rfm` RFM on a.address_id=RFM.address_guid and a.FP=RFM.fiscal_period_name

Left Join `dw-bq-data-p00.ANALYTICAL.model_factory_shopping_metrics_history` ADS on a.address_id=ADS.address_guid and a.FP=ADS.fiscal_period_name

Left Join `dw-bq-data-p00.ANALYTICAL.model_factory_address_demographics_history` D on a.address_id=D.address_guid and a.FP=D.fiscal_period_name
) a
;
