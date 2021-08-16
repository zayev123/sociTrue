from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.auth.hashers import make_password

from soci_3_api.myStorage import OverwriteStorage
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile


class HobbyDetails(models.Model):
    hobbyName = models.CharField(max_length=60)
    hobImage = models.ImageField(
        upload_to='hobby_images', blank=True, null=True, storage=OverwriteStorage())

    def __str__(self):
        return str(self.id)


class CategoryDetails(models.Model):
    categoryName = models.CharField(max_length=60)
    catImage = models.ImageField(
        upload_to='category_images', blank=True, null=True, storage=OverwriteStorage())

    def __str__(self):
        return str(self.id)


class UserInfoManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class UserInfo(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    pseudo_name = models.CharField(max_length=200, blank=True, null=True)
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to='profile_images', blank=True, null=True, storage=OverwriteStorage())
    bas64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    phoneNumber = models.CharField(max_length=30, blank=True, null=True)
    isLoggedIn = models.BooleanField(default=True)
    socialImageUrl = models.CharField(max_length=500, blank=True, null=True)
    aboutYourself = models.TextField(blank=True, null=True)
    personalHobbyList = models.ManyToManyField(
        HobbyDetails, related_name='userInfo', blank=True)
    participatedActivitiesList = models.ManyToManyField(
        'ActivityDetails', through='ActiveParticipants', related_name='participants', blank=True)
    shadowUser = models.BooleanField(default=False)
    birthDate = models.DateField(blank=True, null=True)
    isBlocked = models.BooleanField(default=False)
    waitingPrtcpnts = models.ManyToManyField(
        'ActivityDetails', through='WaitingParticipants', related_name='waiting_users', blank=True)
    permaRemPrtcpnts = models.ManyToManyField(
        'ActivityDetails', through='PermaRemParticipants', related_name='rem_users', blank=True)
    isPrivate = models.BooleanField(default=False)
    friends = models.ManyToManyField('self', through='UserFriend', related_name='myFriends', blank=True,
                                     symmetrical=False)
    friendRequests = models.ManyToManyField('self', through='FriendRequest', related_name='receivedRequests', blank=True,
                                            symmetrical=False)
    friendStatus = models.CharField(max_length=30, blank=True, null=True)
    isAnonymous = models.BooleanField(default=False)

    objects = UserInfoManager()

    USERNAME_FIELD = 'email'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class BlockedBy(models.Model):
    theManWhoBlocked = models.ForeignKey(
        UserInfo, related_name='blocker', on_delete=models.CASCADE)
    profileIdToBlock = models.ForeignKey(
        UserInfo, related_name='blockedBy', on_delete=models.CASCADE)


class ActivityDetails(models.Model):
    name = models.CharField(max_length=100)
    actDescription = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='activity_images', blank=True, null=True, storage=OverwriteStorage())
    bas64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    category = models.ForeignKey(
        CategoryDetails, related_name='activityDetails', on_delete=models.CASCADE)
    dayDate = models.DateField(blank=True, null=True)
    theTime = models.CharField(max_length=100, blank=True, null=True)
    actDuration = models.IntegerField(blank=True, null=True)
    isAdress = models.BooleanField(default=True)
    isOnline = models.BooleanField(default=False)
    isAdduRsl = models.BooleanField(default=False)
    city = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=800, blank=True, null=True)
    locLatitude = models.CharField(max_length=300, blank=True, null=True)
    locLongitude = models.CharField(max_length=300, blank=True, null=True)
    howToFind = models.TextField(blank=True, null=True)
    orgaNote = models.TextField(blank=True, null=True)
    mndtryPrty = models.BooleanField(default=False)
    cnclAdrs = models.BooleanField(default=False)
    capacity = models.IntegerField(blank=True, null=True)
    ticketuRsl = models.CharField(max_length=400, blank=True, null=True)
    whatsapUrl = models.CharField(max_length=200, blank=True, null=True)
    organizerDetails = models.ForeignKey(
        UserInfo, related_name='activityDetails', blank=True, null=True, on_delete=models.CASCADE)
    forFriend = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['dayDate']


class WaitingParticipants(models.Model):
    pastPrtcnt = models.BooleanField(default=False)
    prtcpntId = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE)
    actId = models.ForeignKey(
        ActivityDetails, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-pastPrtcnt']


class PermaRemParticipants(models.Model):
    prtcpntId = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE)
    actId = models.ForeignKey(
        ActivityDetails, on_delete=models.CASCADE)


class ActiveParticipants(models.Model):
    prtcpntId = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE)
    actId = models.ForeignKey(
        ActivityDetails, on_delete=models.CASCADE)


class UserFriend(models.Model):
    myId = models.ForeignKey(
        UserInfo, related_name='mySelf', on_delete=models.CASCADE)
    friendId = models.ForeignKey(
        UserInfo, related_name='myFriend', on_delete=models.CASCADE)


class FriendRequest(models.Model):
    myId = models.ForeignKey(
        UserInfo, related_name='myId', on_delete=models.CASCADE)
    friendId = models.ForeignKey(
        UserInfo, related_name='friendId', on_delete=models.CASCADE)


class ActComment(models.Model):
    commentText = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='comment_images', blank=True, null=True)
    bas64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    comLat = models.CharField(max_length=300, blank=True, null=True)
    comLong = models.CharField(max_length=300, blank=True, null=True)
    idOwner = models.ForeignKey(
        UserInfo, related_name='actComment', on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    forActivity = models.ForeignKey(
        ActivityDetails, related_name='actComment', on_delete=models.CASCADE)


class ChatModel(models.Model):
    chatName = models.CharField(max_length=100)
    chatParticipants = models.ManyToManyField(
        UserInfo, related_name='chatModels', blank=True)
    lastMessage = models.TextField(blank=True, null=True)
    isGroup = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to='chat_images', blank=True, null=True)
    bas64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    lastUpdate = models.DateTimeField(auto_now=True)
    newMessagesFor = models.ManyToManyField(
        UserInfo, related_name='myNewChats', blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-lastUpdate']


class ChatMessage(models.Model):
    author = models.ForeignKey(
        UserInfo, related_name='chatMessages', on_delete=models.CASCADE)
    forChat = models.ForeignKey(
        ChatModel, related_name='chatMessages', on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)
    messageContent = models.TextField()
    image = models.ImageField(
        upload_to='message_images', blank=True, null=True)
    bas64Image = models.TextField(blank=True, null=True)
    imageType = models.CharField(max_length=10, blank=True, null=True)
    comLat = models.CharField(max_length=300, blank=True, null=True)
    comLong = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        ordering = ['-createdAt']
