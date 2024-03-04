from rest_framework import serializers
from accounts.models import  Category



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'category', 'categoryImage', 'parent')
