from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Account, StatementItem
from django.db.models import Sum


def update_account_balance(account):
    total = StatementItem.objects.filter(statement__account=account).aggregate(total=Sum('amount'))['total'] or 0
    account.balance = total
    account.save(update_fields=['balance'])

@receiver(post_save, sender=StatementItem)
@receiver(post_delete, sender=StatementItem)
def handle_statementitem_change(sender, instance, **kwargs):
    update_account_balance(instance.statement.account)
