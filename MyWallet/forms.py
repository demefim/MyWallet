from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from MyWallet import models


class BudgetForm(forms.Form):
    budget_id = forms.IntegerField()
    category_id = forms.IntegerField()
    category_name = forms.CharField(max_length=64)
    spent = forms.CharField(max_length=32)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    left = forms.CharField(max_length=32)
    month = forms.DateField()

    def save(self):
        if self.cleaned_data['budget_id'] == -1:
            if self.cleaned_data['amount'] != 0:
                # new budget
                models.Budget.objects.create(
                    category_id=self.cleaned_data['category_id'],
                    month=self.cleaned_data['month'],
                    amount=self.cleaned_data['amount'])
        elif self.cleaned_data['amount'] != 0:
            models.Budget.objects.update_or_create(id=self.cleaned_data['budget_id'], defaults={
                'amount': self.cleaned_data['amount']
            })
        else:
            models.Budget.objects.get(id=self.cleaned_data['budget_id']).delete()


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ['title', 'source_account', 'destination_account',
                  'amount', 'date', 'value_date', 'category', 'notes']

    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    category = forms.ModelChoiceField(
        queryset=models.Category.objects.exclude(active=False).order_by('name'), required=False)
    value_date = forms.DateField(required=False)

    source_account = forms.ModelChoiceField(queryset=models.Account.objects.filter(
        account_type=models.Account.PERSONAL, active=True))
    destination_account = forms.ModelChoiceField(queryset=models.Account.objects.filter(
        account_type=models.Account.PERSONAL, active=True))

    def save(self, commit=True):
        transaction = super().save(commit)
        src = self.cleaned_data['source_account']
        dst = self.cleaned_data['destination_account']
        amount = self.cleaned_data['amount']
        value_date = self.cleaned_data.get('value_date') or transaction.date
        models.Split.objects.update_or_create(
            transaction=transaction, amount__lt=0,
            defaults={'amount': -amount, 'account': src,
                      'opposing_account': dst, 'date': value_date,
                      'title': transaction.title,
                      'category': self.cleaned_data['category']})
        models.Split.objects.update_or_create(
            transaction=transaction, amount__gt=0,
            defaults={'amount': amount, 'account': dst,
                      'opposing_account': src, 'date': value_date,
                      'title': transaction.title,
                      'category': self.cleaned_data['category']})
        return transaction

BudgetFormSet = forms.formset_factory(BudgetForm, extra=0)


CategoryAssignFormset = forms.modelformset_factory(models.Split, fields=('category',), extra=0)
