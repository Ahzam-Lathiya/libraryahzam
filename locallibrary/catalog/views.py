import datetime
from io import BytesIO

from django.shortcuts import render, get_object_or_404
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.template.loader import get_template
from django.template import Context

from catalog.models import Book, Author, BookInstance, Genre
from catalog.forms import RenewBookForm, ReturnBookForm, ReserveBookForm
from catalog.utils import render_to_pdf

from xhtml2pdf import pisa

# Create your views here.

class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial = { 'date_of_death': '05/01/2018'}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class BookCreate(CreateView):
    model = Book
    fields = "__all__"
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
    permission_required = 'catalog.can_mark_returned'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_required'

def render_to_pdf( template_src, context_dict={} ):

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')

    return None




class ViewPDF(View):
    def get(Self, request, pk, *args, **kwargs):

        user = request.user

        book_instance = get_object_or_404(BookInstance, pk = pk)

        date_today = datetime.date.today()

        date_delta = 0

        if(book_instance.calculate_due != 0):
            date_delta = book_instance.calculate_due//100 

        context = {'book_instance': book_instance,
                   'user': user,
                   'date' : date_today,
                   'date_delta' : date_delta,
                  }

        pdf = render_to_pdf('catalog/pdf_template.html', context)
        return HttpResponse(pdf, content_type='application/pdf')


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    #If this is a POST request then process the Form data
    if(request.method == 'POST'):

        #create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        #check if the form is valid:
        if( form.is_valid() ):
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            #redirect to a new URL:
            return HttpResponseRedirect( reverse('all-borrowed') )

    #If this is a GET or any other method
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={ 'renewal_date': proposed_renewal_date} )

    context = {
        'form': form,
        'book_instance' : book_instance,
}

    return render(request, 'catalog/book_renew_librarian.html', context)

def get_book_user(request, pk):

    book_instance = get_object_or_404(BookInstance, pk=pk)
    due_date = datetime.date.today() + datetime.timedelta(weeks=3)

    if(request.user.is_authenticated):
        user = request.user

    if(request.method == 'POST'):
        # change status to 'on loan'
        book_instance.status = 'o'

        # assign borrower id to the instance
        book_instance.borrower_id = user.id

        # assign the due-date to book instance
        book_instance.due_back = due_date

        #save the instance
        book_instance.save()

        return HttpResponseRedirect( reverse('my-borrowed') )



    context = {'book_instance': book_instance,
               'due_date': due_date,
              }

    return render(request, 'catalog/get_book_user.html', context)

def reserve_book_user(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if(request.user.is_authenticated):
        user = request.user

    if(request.method == 'POST'):
        form = ReserveBookForm(request.POST)

        if( form.is_valid() ):
            # change book status to 'reserved'
            book_instance.status = 'r'

            # assign the borrower id to the instance
            book_instance.borrower_id = user.id

            book_instance.due_date = form.cleaned_data['reservation_date'] + datetime.timedelta(weeks=3)

            #save the instance
            book_instance.save()

            return HttpResponseRedirect( reverse('my-borrowed') )

    else:

        valid_date = datetime.date.today() + datetime.timedelta(weeks = 3)
        context = {'book_instance': book_instance,
                   'valid_date'   : valid_date,}

        return render(request, 'catalog/reserve_book_user.html', context)

def return_book_user(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    datetime.date.today() + datetime.timedelta(weeks=3)

    #If this is a POST request then process the Form data
    if(request.method == 'POST'):

            # process the data i.e. update the object fields and save them

            # clear the 'due-date' field
            book_instance.due_back = None
        
            # clear the 'borrower-id' field
            book_instance.borrower_id = ''

            # change the book status to 'a'
            book_instance.status = 'a'
        
            book_instance.save()

            #redirect to a new URL:
            return HttpResponseRedirect( reverse('my-borrowed') )

    else:

        context = {
            'book_instance':book_instance,
}
        return render(request, 'catalog/book_return_user.html', context)

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


"""
def book_detail_view(request, primary_key):
    try:
        book = Book.objects.get(pk=primary_key)
    except Book.DoesNotExist:
        raise Http404('Book does not exist')

    return render(request, 'catalog/book_detail.html', context={'book': book})"""


def index(request):
    """View function for the home page of site"""
    
    #generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    #Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    #The 'all()' is implied by default.
    num_authors = Author.objects.count()

    #number of visits to the view, counted by the session variable
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books' : num_books,
        'num_instances' : num_instances,
        'num_instances_available' : num_instances_available,
        'num_authors' : num_authors,
        'num_visits' : num_visits,
    }

    #render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

