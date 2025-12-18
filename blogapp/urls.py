# blogapp/urls.py
from django.urls import path
from . import views

app_name = 'blogapp'

urlpatterns = [
    path('', views.accueil_view, name='accueil'),
    path('inscription/', views.inscription_view, name='inscription'),
    path('connexion/', views.connexion_view, name='connexion'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    
    # URLs pour les articles
    path('article/creer/', views.creer_article_view, name='creer_article'),
    path('article/<int:article_id>/', views.detail_article_view, name='detail_article'),
    path('article/<int:article_id>/modifier/', views.modifier_article_view, name='modifier_article'),
    path('article/<int:article_id>/supprimer/', views.supprimer_article_view, name='supprimer_article'),
    
    # URL pour ajouter un commentaire
    path('article/<int:article_id>/ajouter_commentaire/', views.ajouter_commentaire_view, name='ajouter_commentaire'),
    
    # URL pour le profil utilisateur
    path('profil/<str:username>/', views.profil_utilisateur_view, name='profil_utilisateur'),
]