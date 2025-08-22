from django.db import models

class Item(models.Model):
    item_id = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=120, unique=True)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome
    
    def __str_descricao__(self):
        return f'{self.nome} - {self.descricao}'