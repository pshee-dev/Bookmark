from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404

@api_view(['GET', 'POST'])
def library_book_list(request):
    pass

@api_view(['PATCH', 'DELETE'])
def library_book(request, library_id):
    pass