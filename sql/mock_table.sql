create or replace view GFORSYTHE.MARKETINGBOT.MARKETING_METRICS_FINAL_MOCK_A(
	TITLE,
	VARIABLE,
	VALUE,
	MONTH,
	YEAR,
	MEDIUM,
    WON
) as (
with
    distinct_accounts as (
        select row_number() over (order by null) as id, *
        from
            (
                select distinct title as account
                from marketing_metrics_final
                where medium = 'ACCOUNT' OR MEDIUM = 'OPPORTUNITY'
            )
    ),
    account_x_mock_account as (
        select da.account, am.account as mock_account
        from account_mock as am
        join distinct_accounts as da on am.id = da.id
    )
select
    case
        when axma.mock_account is not null then axma.mock_account else title
    end as title,
    mmf.* exclude(title)
from marketing_metrics_final mmf
left outer join account_x_mock_account as axma on mmf.title = axma.account
);
