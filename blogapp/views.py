# blogapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .models import Article, Commentaire
from .forms import ArticleForm, CommentaireForm


def accueil_view(request):
    tous_les_articles = Article.objects.all().order_by('-date_creation')
    
    # Configuration de la pagination
    paginator = Paginator(tous_les_articles, 5)  # Affiche 5 articles par page
    page_numero = request.GET.get('page')  # Récupère le numéro de page depuis l'URL (ex: ?page=2)
    
    try:
        articles_pages = paginator.page(page_numero)
    except PageNotAnInteger:
        # Si 'page' n'est pas un entier, afficher la première page.
        articles_pages = paginator.page(1)
    except EmptyPage:
        # Si 'page' est hors limites (ex: page 9999), afficher la dernière page de résultats.
        articles_pages = paginator.page(paginator.num_pages)
    
    context = {
        'articles_a_afficher': articles_pages,  # On passe l'objet Page au template
    }
    return render(request, 'blogapp/accueil.html', context)


def inscription_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Sauvegarde le nouvel utilisateur
            login(request, user)  # Connecte l'utilisateur
            return redirect('blogapp:accueil')  # Redirige vers l'accueil
    else:
        form = UserCreationForm()

    return render(request, 'blogapp/inscription.html', {'form': form})


def connexion_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('blogapp:accueil')
    else:
        form = AuthenticationForm()

    return render(request, 'blogapp/connexion.html', {'form': form})


def deconnexion_view(request):
    if request.method == 'POST':  # C'est une bonne pratique de faire la déconnexion sur un POST
        logout(request)
        return redirect('blogapp:accueil')
    else:
        # Version simplifiée pour GET (pour débutant)
        # Dans une vraie application, on afficherait un formulaire de confirmation
        logout(request)
        return redirect('blogapp:accueil')


# Stubs pour éviter les erreurs si les templates/listes ne sont pas présents.
def liste_articles(request):
    """Stub: redirige vers l'accueil si la page liste n'est pas encore implémentée."""
    return redirect('blogapp:accueil')


def detail_article_view(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    commentaire_form = CommentaireForm()  # Crée une instance vide du formulaire
    
    # Récupérer les commentaires (déjà accessible via article.commentaires.all dans le template)
    # commentaires = article.commentaires.all()  # Pas besoin de le passer explicitement si on utilise le related_name
    
    context = {
        'article': article,
        'commentaire_form': commentaire_form,  # Passe le formulaire au template
        # 'commentaires': commentaires,  # Optionnel, on peut utiliser article.commentaires.all directement
    }
    return render(request, 'blogapp/detail_article.html', context)


@login_required
def modifier_article_view(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    
    # Vérifier si l'utilisateur connecté est l'auteur de l'article
    if article.auteur != request.user:
        # Rediriger ou afficher une erreur "Permission non accordée"
        # Pour la simplicité, on redirige vers le détail de l'article
        return redirect('blogapp:detail_article', article_id=article.pk)  # Ou une page d'erreur 403 Forbidden

    if request.method == 'POST':
        titre = request.POST.get('titre')
        contenu = request.POST.get('contenu')
        if titre and contenu:
            article.titre = titre
            article.contenu = contenu
            article.save()
            return redirect('blogapp:detail_article', article_id=article.pk)
        # Si données manquantes, afficher le formulaire avec un message d'erreur
        context = {
            'form': ArticleForm(instance=article),
            'action': 'Modifier',
            'article': article,
            'error': 'Tous les champs sont requis.'
        }
        return render(request, 'blogapp/creer_modifier_article.html', context)

    # GET : afficher le formulaire de modification
    form = ArticleForm(instance=article)
    context = {
        'form': form,
        'action': 'Modifier',
        'article': article,
    }
    return render(request, 'blogapp/creer_modifier_article.html', context)


@login_required
def supprimer_article_view(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    
    if article.auteur != request.user:
        return redirect('blogapp:detail_article', article_id=article.pk)  # Ou erreur 403
    
    if request.method == 'POST':  # Si l'utilisateur a confirmé la suppression
        article.delete()
        return redirect('blogapp:accueil')  # Redirige vers l'accueil après suppression
    
    # Si c'est une requête GET, on affiche la page de confirmation
    context = {
        'article': article
    }
    return render(request, 'blogapp/confirmer_suppression_article.html', context)


@login_required
def creer_article_view(request):
    """Création d'un Article avec formulaire."""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.auteur = request.user
            article.save()
            return redirect('blogapp:detail_article', article_id=article.pk)
        # Si le formulaire n'est pas valide, afficher les erreurs
        context = {
            'form': form,
            'action': 'Créer',
        }
        return render(request, 'blogapp/creer_modifier_article.html', context)

    # GET -> afficher le formulaire de création
    form = ArticleForm()
    context = {
        'form': form,
        'action': 'Créer',
    }
    return render(request, 'blogapp/creer_modifier_article.html', context)


@login_required  # Seuls les utilisateurs connectés peuvent commenter
def ajouter_commentaire_view(request, article_id):  # article_id est l'ID de l'article à commenter
    article = get_object_or_404(Article, pk=article_id)
    
    # Règle : L'auteur de l'article ne peut pas commenter son propre article
    # (Comme demandé : "seulement les autre utilisateurs peut commenter")
    # Si vous voulez que l'auteur puisse commenter, retirez cette condition.
    if article.auteur == request.user:
        # On pourrait afficher un message d'erreur avec django.contrib.messages
        # Pour la simplicité "bébé", on redirige simplement sans rien faire.
        return redirect('blogapp:detail_article', article_id=article.pk)
    
    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.article = article
            commentaire.auteur = request.user  # L'auteur du commentaire est l'utilisateur connecté
            commentaire.save()
            return redirect('blogapp:detail_article', article_id=article.pk)  # Redirige vers la page de l'article
        else:
            # Si le formulaire n'est pas valide, afficher le détail avec les erreurs
            commentaire_form = form
            context = {
                'article': article,
                'commentaire_form': commentaire_form,
            }
            return render(request, 'blogapp/detail_article.html', context)
    else:
        # GET : afficher le détail de l'article avec le formulaire vierge
        commentaire_form = CommentaireForm()
        context = {
            'article': article,
            'commentaire_form': commentaire_form,
        }
        return render(request, 'blogapp/detail_article.html', context)


def profil_utilisateur_view(request, username):
    # Récupère l'utilisateur par son nom d'utilisateur ou renvoie une erreur 404
    utilisateur_profil = get_object_or_404(User, username=username)
    
    # Récupère tous les articles écrits par cet utilisateur, triés par date de création
    articles_utilisateur = Article.objects.filter(auteur=utilisateur_profil).order_by('-date_creation')
    
    context = {
        'utilisateur_profil': utilisateur_profil,
        'articles_utilisateur': articles_utilisateur,
    }
    return render(request, 'blogapp/profil_utilisateur.html', context)