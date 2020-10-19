from django.shortcuts import render
from rest_framework import status

from .models import *
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from . import serializers


class IndexPage(TemplateView):

    def get(self,request,**kwargs):

        article_data = []
        all_articles = Article.objects.all().order_by('-created_at')[:9]

        for article in all_articles:
            article_data.append({
                'title' : article.title,
                'cover' : article.cover.url,
                'category' : article.category.title,
                'created_at' : article.created_at.date(),
            })

        promote_data = []
        all_promote_articles =Article.objects.filter(promote=True)
        for promote_article in all_promote_articles:
            promote_data.append({
                'category':promote_article.category.title,
                'title' : promote_article.title,
                'author': promote_article.author.user.first_name +' '+ promote_article.author.user.last_name,
                'avatar':promote_article.author.avatar.url if promote_article.author.avatar else None,
                'cover': promote_article.cover.url if promote_article.cover else None,
                'created_at' : promote_article.created_at.date(),
            })

        context = {
            'article_data' : article_data,
            'promote_article_data': promote_data,
        }
        return render(request,'index.html',context)


## contact page
class ContactPage(TemplateView):
    template_name = "page-contact.html"


class AllArticleAPIView(APIView):
    def get(self,request,format=None):

        try:
            all_articles = Article.objects.all().order_by('-created_at')[:11]
            data = []
            for article in all_articles:
                data.append({
                    'title':article.title,
                    'cover':article.cover.url if article.cover else None,
                    'content': article.content,
                    'created_at':article.created_at,
                    'category':article.category.title,
                    'author':article.author.user.first_name+' '+article.author.user.last_name,
                    'promote':article.promote,
                })
            return Response({'data':data},status=status.HTTP_200_OK)

        except:
            return Response({'status':"internal server error, we'll check it later"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SingleArticleAPIView(APIView):
    def get(self,request, format=None):

        try:
            #article_title = request.query_params.get('article_title')
            article_title = request.query_params.get('article_title')
            article = Article.objects.filter(title__contains=article_title)
            print(article)
            serialized_data= serializers.SingleArticleSerializer(article,many=True)
            data=serialized_data.data
            print(article)
            return Response({'data':data}, status=status.HTTP_200_OK)
        except:
            return Response({'status':"Internal Server error"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        #except Exception as e:
        #     print(e)

class SrearchArticleAPIView(APIView):
    def get(self,request, format=None):
        try:
            from django.db.models import Q
            query=request.GET['query']
            articles=Article.objects.filter(Q(content__icontains=query))
            data=[]

            for article in articles:
                data.append({
                    "title":article.title,
                    "cover":article.cover.url if article.cover else None,
                    "content":article.content,
                    "created_at":article.created_at,
                    "category":article.category.title,
                    "author":article.author.user.first_name+ ' '+article.author.user.last_name,
                    "promote":article.promote,

                })
            return Response({'data':data}, status=status.HTTP_200_OK)
        except:
            return Response({'status': "Internal Server error,search"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SubmitArticleAPIView(APIView):
    def post(self,request,format=None):
        try:
            serializer=serializers.SubmitArticleSerializer(data=request.data)
            if serializer.is_valid():
                title=serializer.data.get('title')
                cover=request.FILES['cover']
                content=serializer.data.get('content')
                category_id=serializer.data.get('category_id')
                authory_id=serializer.data.get('author_id')
                promote=serializer.data.get('promote')
            else:
                return Response({'status':'bad request.'},status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.get(id=authory_id)
            author= UserProfile.objects.get(user=user)
            category=Category.objects.get(id=category_id)

            article=Article()
            article.title=title
            article.cover=cover
            article.content=content
            article.category=category
            article.author=author
            article.promote=promote
            article.save()

            return Response({'status':'OK'},status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server error,submit"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UpdateArticleAPIView(APIView):
    def post(self,request,format=None):
        try:
            serializer=serializers.UpdateArticleCoverSerializer(data=request.data)

            if serializer.is_valid():
                article_id=serializer.data.get('article_id')
                cover=request.FILES['cover']
            else:
                return Response({'status':'Bad reuest'}, status=status.HTTP_400_BAD_REQUEST)
            Article.objects.filter(id=article_id).update(cover=cover)

            return Response({'status':'OK'},status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server error,update"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteArticleAPIView(APIView):
    def post(self,request,format=None):
        try:
            serializer=serializers.DeleteArticleSerializer(data=request.data)
            if serializer.is_valid():
                article_id=serializer.data.get('article_id')

            else:
                return Response({'status':'bad request'},status=status.HTTP_400_BAD_REQUEST)
            Article.objects.filter(id=article_id).delete()
            return Response({'stats':'OK'},status=status.HTTP_200_OK)
        except:
            return Response({'status': "Internal Server error,delete"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

