from django.db import models


# TODO will associate(o2o) this with Django User model
class ZidUser(models.Model):
    user_id = models.CharField(max_length=50, null=True, blank=True)
    user_uuid = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    authorization_code = models.TextField(null=True, blank=True)
    token_type = models.CharField(max_length=50, null=True, blank=True)
    expires_in = models.IntegerField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

    def get_access_token(self):
        return self.access_token


class ZidUserStore(models.Model):
    zid_user = models.ForeignKey(ZidUser, on_delete=models.CASCADE)
    store_id = models.CharField(max_length=50, null=True, blank=True)
    store_uuid = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# class TokenData(models.Model):
#     zid_user = models.ForeignKey(ZidUser, on_delete=models.CASCADE)
#     access_token = models.TextField()
#     authorization_code = models.TextField()
#     token_type = models.CharField(max_length=50)
#     expires_in = models.IntegerField()
#     refresh_token = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Token {self.id} - Expires in {self.expires_in} seconds"
