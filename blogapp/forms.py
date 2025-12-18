# blogapp/forms.py
from django import forms
from .models import Article, Commentaire

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['titre', 'contenu']  # Seuls ces champs seront dans le formulaire
        # L'auteur sera défini automatiquement dans la vue
        # Les dates sont gérées automatiquement par le modèle


class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['contenu']  # L'utilisateur ne remplit que le contenu
        widgets = {  # Optionnel : pour personnaliser l'apparence du champ
            'contenu': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Laissez votre commentaire ici...'}),
        }
