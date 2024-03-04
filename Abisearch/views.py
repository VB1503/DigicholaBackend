from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import ListAPIView
from django.db.models import Q
from rest_framework.response import Response
from accounts.serializers import BusinessDetailsSerializer
from accounts.models import  Category, BusinessDetails
from .serializer import CategorySerializer
class SearchView(APIView):
    def get(self, request, query_type, catcall=None):
        if query_type == 'search':
            search_query = request.GET.get('query')
            if not search_query:
                return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)

            category_ids = Category.objects.filter(
                Q(category__icontains=search_query) |
                Q(children__category__icontains=search_query)
            ).values_list('id', flat=True)

            # Perform the query on 'BusinessDetails' using the category IDs
            businesses = BusinessDetails.objects.filter(
                Q(category__id__in=category_ids) |
                Q(business_name__icontains=search_query) |
                Q(business_phone_number__icontains=search_query) |
                Q(description__icontains=search_query)
)

            serializer = BusinessDetailsSerializer(businesses, many=True)
            return Response(serializer.data)
        if query_type == 'categories':
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            if catcall:
                print(catcall)
                category_ids = Category.objects.filter(
                Q(category__icontains=catcall) |
                Q(children__category__icontains=catcall)
                ).values_list('id', flat=True)
                businesses = BusinessDetails.objects.filter( category__id__in=category_ids)
                serializer2 = BusinessDetailsSerializer(businesses, many=True)
                return Response(serializer2.data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({'error': 'Invalid query type'}, status=status.HTTP_400_BAD_REQUEST)  
        

    

