from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic

from MyWallet.forms import TransactionForm
from MyWallet.models import Account, Split, Transaction


class TransactionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Transaction
    context_object_name = 'transaction'

    def get_context_data(self, **kwargs):
        context = super(TransactionDetailView, self).get_context_data(**kwargs)
        context['menu'] = 'transactions'
        return context


class TransactionDeleteView(LoginRequiredMixin, generic.edit.DeleteView):
    model = Transaction
    success_url = reverse_lazy('accounts')

    def get_context_data(self, **kwargs):
        context = super(TransactionDeleteView, self).get_context_data(**kwargs)
        context['menu'] = 'transactions'
        return context


class TransactionIndex(LoginRequiredMixin, generic.ListView):
    template_name = 'MyWallet/transaction_overview.html'
    context_object_name = 'transactions'
    model = Split
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().filter(account__account_type=Account.PERSONAL)

        if 'category' in self.request.GET:
            queryset = queryset.filter(category_id=self.request.GET['category'])
        if 'recurrence' in self.request.GET:
            queryset = queryset.filter(transaction__recurrence_id=self.request.GET['recurrence'])
        if 'account' in self.request.GET:
            queryset = queryset.filter(account_id=self.request.GET['account'])
        elif 'opposing_account' in self.request.GET:
            queryset = queryset.filter(opposing_account_id=self.request.GET['opposing_account'])
        else:
            queryset = queryset.transfers_once()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'transactions'
        context['submenu'] = 'all'
        return context


class TransactionCreate(LoginRequiredMixin, generic.edit.CreateView):
    model = Transaction
    template_name = 'MyWallet/transaction_edit.html'

    def dispatch(self, request, *args, **kwargs):
        self.type = kwargs.pop('type')
        return super(TransactionCreate, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return TransactionForm

    def get_context_data(self, **kwargs):
        context = super(TransactionCreate, self).get_context_data(**kwargs)
        context['menu'] = 'transactions'
        context['submenu'] = self.type
        return context


class TransactionUpdateView(LoginRequiredMixin, generic.edit.UpdateView):
    template_name = 'MyWallet/transaction_edit.html'
    model = Transaction

    def get_initial(self):
        initial = super().get_initial()
        self.transaction = Split.objects.get(transaction_id=self.kwargs.get('pk'), amount__gt=0)
        initial['source_account'] = self.transaction.opposing_account.pk
        initial['destination_account'] = self.transaction.account.pk
        if self.object.transaction_type == Transaction.WITHDRAW:
            initial['destination_account'] = self.transaction.account
        elif self.object.transaction_type == Transaction.DEPOSIT:
            initial['source_account'] = self.transaction.opposing_account
        initial['amount'] = self.transaction.amount
        initial['category'] = self.transaction.category
        initial['value_date'] = self.transaction.date
        return initial

    def get_queryset(self):
        queryset = super(TransactionUpdateView, self).get_queryset()
        return queryset.exclude(transaction_type=Transaction.SYSTEM)

    def get_form_class(self):
        return TransactionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'transactions'
        return context


