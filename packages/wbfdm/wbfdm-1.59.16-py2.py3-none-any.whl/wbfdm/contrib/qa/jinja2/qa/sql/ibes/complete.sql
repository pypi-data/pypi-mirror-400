{% with financial_table="TreActRpt", value="DefActValue", estimate=False %}
    {% include 'qa/sql/ibes/financials.sql' %}
{% endwith %}

union

{% with financial_table="TreSumPer", value="DefMeanEst", from_index=1, estimate=True %}
    {% include 'qa/sql/ibes/financials.sql' %}
{% endwith %}
