from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from collections import defaultdict


def report_turnover_by_year_month(period_begin, period_end):
    # TODO: TASK → make report using 1 database query without any math in python -done
    # example output
    # return {
    #     "2009-11": {
    #         {
    #             "incomes": {
    #                 "PLN": 120
    #             },
    #             "expenses": {
    #                 "PLN": 100
    #             }
    #         }
    #     }
    # }
    qs = (
        StatementItem.objects
        .filter(statement__date__range=(period_begin, period_end))
        .annotate(month=TruncMonth("statement__date"))
        .values("month", "currency")
        .annotate(incomes=Sum("amount", filter=models.Q(amount__gt=0)),
                  expenses=Sum("amount", filter=models.Q(amount__lt=0)))
        .order_by("month", "currency")
    )

    result = defaultdict(lambda: {"incomes": {}, "expenses": {}})
    for row in qs:
        month = row["month"].strftime("%Y-%m")
        currency = row["currency"]
        if row["incomes"]:
            result[month]["incomes"][currency] = float(row["incomes"])
        if row["expenses"]:
            result[month]["expenses"][currency] = float(-row["expenses"])
    return dict(result)


class Account(models.Model):
    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=3)
    # TODO: TASK → add field balance that will update automatically - done
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.name}[{self.currency}]'


class Statement(models.Model):
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    date = models.DateField()
    # TODO: TASK → make sure that account and date is unique on database level - done

    def __str__(self):
        return f'{self.account} → {self.date}'

    class Meta:
        unique_together = ('account', 'date')


class StatementItem(models.Model):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    title = models.CharField(max_length=100)
    # TODO:  TASK → add field comments (type text) - done
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'[{self.statement}] {self.amount} {self.currency} → {self.title}'
