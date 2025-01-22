from django.shortcuts import render,redirect,get_object_or_404
from home.models import Add
from django.views.generic import TemplateView,CreateView,UpdateView,DeleteView,ListView
from django.urls import reverse_lazy
import csv
from django.http import HttpResponse
import pandas as pd
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout as auth_logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

# Create your views here.
# def index(request):
#     return render(request, 'index.html')
class Login(TemplateView):
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html')

class Index(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:  # Check if the user is logged in
            return redirect('login')
        return super().get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

def logout(request):
    auth_logout(request)
    request.session.flush()  # Clears the session data
    cache.clear()      # Clears any cached data
    return redirect('login')

def delete_account(request):
    if request.method == "POST":
        user = request.user
        username = user.username
        auth_logout(request)
        user.delete()
        messages.success(request, f"Account '{username}' and all related records have been deleted successfully.")
        return redirect('login')
    return render(request, 'delete_account.html')

class Register(TemplateView):
    template_name = 'register.html'

    def post(self, request, *args, **kwargs):
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        user.first_name = firstname     # User model uses first_name (with underscores) to store a user's first and last names.
        user.last_name = lastname
        user.save()
        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('login')

# def add(request):
#     if request.method == "POST":
#         title = request.POST.get('title')
#         amount = request.POST.get('amount')
#         category = request.POST.get('category')
#         notes = request.POST.get('notes')
#         date = request.POST.get('date')
#         add = Add(title=title, amount=amount, category=category, notes=notes, date=date)
#         add.save()
#         return redirect('view')
#
#     return render(request, 'add.html')
class AddView(LoginRequiredMixin,CreateView):
    model = Add
    template_name = 'add.html'
    fields = ['title', 'amount', 'category', 'notes', 'date']
    success_url = reverse_lazy('view')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the logged-in user
        return super().form_valid(form)

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


# def update(request, record_id):
#     record = get_object_or_404(Add, id=record_id)
#
#     if request.method == "POST":
#
#         record.title = request.POST.get('title')
#         record.amount = request.POST.get('amount')
#         record.category = request.POST.get('category')
#         record.notes = request.POST.get('notes')
#         record.date = request.POST.get('date')
#         record.save()
#         return redirect('view')
#
#     record_date = record.date.strftime('%Y-%m-%d')
#
#     return render(request, 'update.html', {'record': record, 'record_date': record_date})
class Update(LoginRequiredMixin,UpdateView):
    model = Add
    template_name = 'update.html'
    fields = ['title', 'amount', 'category', 'notes', 'date']
    success_url = reverse_lazy('view')

    def get_queryset(self):
        return Add.objects.filter(user=self.request.user)  # Restrict to user's data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['record_date'] = self.object.date.strftime('%Y-%m-%d') if self.object.date else ''
        return context

# def delete(request, record_id):
#     record = Add.objects.get(id=record_id)
#     record.delete()
#     return redirect('view')
class Delete(LoginRequiredMixin,DeleteView):
    model = Add
    template_name = 'delete.html'
    success_url = reverse_lazy('view')

    def get_queryset(self):
        return Add.objects.filter(user=self.request.user)  # Restrict to user's data



# def view(request):
#     category = request.GET.get('category')
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
#
#     records = Add.objects.all().order_by('date')
#
#     if category:
#         records = records.filter(category=category)
#     if start_date and end_date:
#         records = records.filter(date__range=[start_date, end_date])
#
#     for record in records:
#         record.record_date = record.date.strftime('%Y-%m-%d')
#
#     #total_amount = sum(float(record.amount) for record in records)
#     total_amount = sum(
#         float(record.amount) for record in records if
#         record.amount and record.amount.strip().replace('.', '', 1).isdigit()
#     )
#
#     return render(request, 'view.html',{'records': records,
#                                         'total_amount': total_amount,
#                                         'category': category,
#                                         'start_date':start_date,
#                                         'end_date': end_date})
class View(LoginRequiredMixin,ListView):
    model = Add
    template_name = 'view.html'
    context_object_name = 'records'

    def get_queryset(self):
        queryset = Add.objects.filter(user=self.request.user).order_by('date')
        category = self.request.GET.get('category','')
        start_date = self.request.GET.get('start_date','')
        end_date = self.request.GET.get('end_date','')

        if category:
            queryset = queryset.filter(category=category)
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        records = context['records']

        for record in records:
            record.record_date = record.date.strftime('%Y-%m-%d') if record.date else ''

        total_amount = sum(
            float(record.amount) for record in records if record.amount and record.amount.strip().replace('.', '', 1).isdigit()
        )
        context['total_amount'] = total_amount

        # for displaying the selected category in filter button
        context['category'] = self.request.GET.get('category','')
        context['start_date'] = self.request.GET.get('start_date','')
        context['end_date'] = self.request.GET.get('end_date','')

        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

@login_required()
def export_csv(request):
    user=request.user
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    records = Add.objects.filter(user=user)
    if category:
        records = records.filter(category=category)
    if start_date and end_date:
        records = records.filter(date__range=[start_date, end_date])

    response=HttpResponse(content_type='text/csv')
    writer=csv.writer(response)
    writer.writerow(['Title','Amount','Category','Notes','Date'])
    for record in records:
        writer.writerow([record.title, record.amount, record.category, record.notes, record.date])

    writer.writerow([])
    total_amount = sum(
        float(record.amount) for record in records if
        record.amount and record.amount.strip().replace('.', '', 1).isdigit()
    )
    writer.writerow(['Summary'])
    summary = f'You have spent Rs. {total_amount}'

    if category:
        summary += f' on {category}'

    if start_date and end_date:
        summary += f' between {start_date} and {end_date}'

    writer.writerow([summary])

    filename=f"{user.first_name}_{user.last_name}_records.csv"

    response['Content-Disposition']=f'attachment; filename="{filename}"'

    return response

@login_required()
def export_excel(request):
    user=request.user
    category=request.GET.get('category')
    start_date=request.GET.get('start_date')
    end_date=request.GET.get('end_date')

    records=Add.objects.filter(user=user)
    if category:
        records=records.filter(category=category)
    if start_date and end_date:
        records=records.filter(date__range=[start_date,end_date])

    data = list(records.values('title', 'amount', 'category', 'notes', 'date'))

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"{user.first_name}_{user.last_name}_records.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return response
