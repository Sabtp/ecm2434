from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import math

# Define database models here
class CustomAccountManager(BaseUserManager):
    # Override default user table
    def create_superuser(self, username, email, password, **other_fields):
        # Create a superuser with admin privileges
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_staff', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.'
            )
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.'
            )
        return self.create_user(username, email, password, **other_fields)
    
    def create_user(self, username, email, password, **other_fields):
        # Create a user with username, email and password fields required
        if not username:
            raise ValueError('Must provide a username')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    # The database model for a user in the app
    username = models.CharField('username', max_length=30, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, blank=True)
    xp = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    bottles = models.PositiveIntegerField(default=0)
    one_time_code = models.CharField(max_length=6, default=123456)
    has_been_verified = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Calculate the level of a user from their XP gained
    @property
    def level(self):
        return 10*(math.log(1-((self.xp*(1-(2**(1/10))))/10) ,2))
    
    # Calculate the XP remainder from a user's level
    @property
    def xpLeft(self):
        return self.xp - ((10*(1-(2**(self.level/10)))) / (1-(2**(1/10))))
    
    objects = CustomAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    def __str__(self):
        return self.username

class Building(models.Model):
    # The database model for a building in the app
    name = models.CharField(max_length=30)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.FloatField()
    image = models.ImageField(blank=True, upload_to='static/buildings/')
    
    def __str__(self):
        return self.name

class Question(models.Model):
    # The database model for a question in the app
    text = models.CharField(max_length=255)
    
    def __str__(self):
        return self.text

class Answer(models.Model):
    # The database model for an answer to a question in the app
    text = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    
    def __str__(self):
        return self.text

class HasAnswered(models.Model):
    # The database model for a question that has been answered by a user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.user.username + ', ' + self.question.text

class Leaderboard(models.Model):
    # The database model for a user in a leaderboard in a building
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_points_in_building = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.building.name + ', ' + self.user.username + ', ' + str(self.user_points_in_building)

class Achievement(models.Model):
    # The database model for an achievement in the app
    name = models.CharField(max_length=255, default="")
    challenge = models.CharField(max_length=255)
    xp_reward = models.PositiveIntegerField()
    points_reward = models.PositiveIntegerField()
    
    def __str__(self):
        return self.challenge

class UserAchievement(models.Model):
    # The database model for an achievement achieved by a user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username + ', ' + self.achievement.challenge

class Fountain(models.Model):
    # The database model for a fountain in the app
    location = models.CharField(max_length=255)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.building.name + ', ' + self.location
    
class BuildingFloor(models.Model):
    # The database model for a floor in a building
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, upload_to='static/floors/')
    floorNumber = models.IntegerField()
    
    def __str__(self):
        return self.building.name + ',' + self.floorNumber
    
class FilledBottle(models.Model):
    # The database model for a bottle being filled by a user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    day = models.DateTimeField()

    def __str__(self):
        return self.user.username + ', ' + self.building.name + ', ' + str(self.day)

class ShopItem(models.Model):
    # The database model for an item in the shop for the app
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    cost = models.PositiveIntegerField()
    image = models.ImageField(blank=True, upload_to='static/shop_items/')

    def __str__(self):
        return self.name + ', ' + self.type

class UserItem(models.Model):
    # The database model for an item that is owned by a user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)

    def __str__(self) :
        return self.user.username + ', ' + self.item.name
