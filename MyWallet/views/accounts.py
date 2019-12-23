from datetime import date, datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import generic

from MyWallet.forms import AccountCreateForm, ReconcilationForm
from MyWallet.models import Account, Split, Transaction


class AccountCreate(LoginRequiredMixin, generic.edit.CreateView):
    model = Account
    form_class = AccountCreateForm
    success_url = reverse_lazy('accounts')

    def get_context_data(self, **kwargs):
        context = super(AccountCreate, self).get_context_data(**kwargs)
        context['menu'] = 'accounts'
        return context


class ForeignAccountCreate(LoginRequiredMixin, generic.edit.CreateView):
    model = Account
    form_class = ForeignAccountForm

    def form_valid(self, form):
        account = form.save(commit=False)
        account.account_type = Account.FOREIGN
        account.save()
        return HttpResponseRedirect(reverse_lazy('foreign_accounts'))


class AccountUpdate(LoginRequiredMixin, generic.edit.UpdateView):
    model = Account
    fields = ['name', 'active', 'show_on_dashboard']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.account_type == Account.SYSTEM:
            return HttpResponse(_('You are not allowed to edit this account'), status=403)
        return generic.edit.ProcessFormView.post(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.account_type == Account.SYSTEM:
            return HttpResponse(_('You are not allowed to edit this account'), status=403)
        return generic.edit.ProcessFormView.get(self, request, *args, **kwargs)

    def get_form_class(self):
        if self.object.account_type != Account.PERSONAL:
            self.fields = ['name']
        return super(AccountUpdate, self).get_form_class()


class AccountDelete(LoginRequiredMixin, generic.edit.DeleteView):
    model = Account
    success_url = reverse_lazy('accounts')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.account_type == Account.SYSTEM:
            return HttpResponse(_('You are not allowed to delete this account'), status=403)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.account_type == Account.SYSTEM:
            return HttpResponse(_('You are not allowed to delete this account'), status=403)
        self.object.delete()
        return HttpResponseRedirect(self.success_url)


class AccountIndex(LoginRequiredMixin, generic.TemplateView):
    template_name = 'MyWallet/accounts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'accounts'
        balances = Split.objects.personal().past().order_by('account_id').values(
            'account_id').annotate(Sum('amount'))
        accounts = list(Account.objects.personal().values('id', 'name', 'active'))
        for a in accounts:
            a['balance'] = 0
        for b in balances:
            for a in accounts:
                if a['id'] == b['account_id']:
                    a['balance'] = b['amount__sum']
        context['accounts'] = accounts
        return context

