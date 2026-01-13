{% with financial_table="TreSumPer", value="DefMeanEst", estimate=True%}
    {% include 'qa/sql/ibes/base_estimates.sql' %}
{% endwith %}
