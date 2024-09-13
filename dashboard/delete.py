from .models import MinistryArticle

# Delete all rows from the MinistryArticle table
MinistryArticle.objects.all().delete()
