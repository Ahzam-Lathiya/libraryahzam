from . import views
from django.urls import path

urlpatterns = [
    path('',                                 views.index,                               name='index'),
    path('books/',                           views.BookListView.as_view(),              name='books'),
    path('book/<int:pk>',                    views.BookDetailView.as_view(),            name='book-detail'),
    path('book/get/<uuid:pk>',               views.get_book_user,                       name='get-book-user'),
    path('book/reserve/<uuid:pk>',           views.reserve_book_user,                   name='reserve-book-user'),
    path('authors/',                         views.AuthorListView.as_view(),            name='authors'),
    path('author/<int:pk>',                  views.AuthorDetailView.as_view(),          name='author-detail'),
    path('mybooks/',                         views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path('pdf_view/<uuid:pk>',                views.ViewPDF.as_view(),                   name='pdf_view'),
    path(r'borrowed/',                       views.LoanedBooksAllListView.as_view(),    name='all-borrowed'),
    path('book/<uuid:pk>/renew/',            views.renew_book_librarian,                name='renew-book-librarian'),
    path('book/<uuid:pk>/return/',           views.return_book_user,                    name='return-book-user'),
    path('author/create/',                   views.AuthorCreate.as_view(),              name='author_create'),
    path('author/<int:pk>/update',           views.AuthorUpdate.as_view(),              name='author_update'),
    path('author/<int:pk>/delete',           views.AuthorDelete.as_view(),              name='author_delete'),
    path('book/create/',                     views.BookCreate.as_view(),                name='book_create'),
    path('book/<int:pk>/update',             views.BookUpdate.as_view(),                name='book_update'),
    path('book/<int:pk>/delete',             views.BookDelete.as_view(),                name='book_delete'),
]
