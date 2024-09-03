from django.db import models

class TokenData(models.Model):
    access_token = models.TextField()
    authorization_code = models.TextField()
    token_type = models.CharField(max_length=50)
    expires_in = models.IntegerField()
    refresh_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token {self.id} - Expires in {self.expires_in} seconds"
