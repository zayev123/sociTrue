from django.contrib import admin


from .models import ActComment, ActiveParticipants, ActivityDetails, BlockedBy, CategoryDetails, ChatMessage, ChatModel, FriendRequest, HobbyDetails, PermaRemParticipants, UserFriend, UserInfo, WaitingParticipants
from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from datetime import date


def nextDate(today, jump):
    nextMon = today.month + jump
    if nextMon > 12:
        myNextDate = today.replace(year=today.year + 1, month=nextMon - 12)
        return myNextDate
    elif nextMon <= 0:
        myNextDate = today.replace(year=today.year - 1, month=12 + nextMon)
        return myNextDate
    else:
        myNextDate = today.replace(month=nextMon)
        return myNextDate


class futureDatesFilter(admin.SimpleListFilter):
    title = "extra-date-filters"
    parameter_name = "pages"  # you can put anything here

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        return [
            ("from_last_month", "From_last_month"),
            ("from_last_year", "From_last_year"),
            ("uptill_next_month", "Uptill_next_month"),
            ("uptill_next_3_months", "Uptill_next_3_months"),
            ("uptill_next_6_months", "Uptill_next_6_months"),
            ("uptill_next_year", "Uptill_next_year"),
        ]

    def queryset(self, request, queryset):
        # This is where you process parameters selected by use via filter options:
        today = date.today()
        nextDay = date.today()
        if self.value() == "uptill_next_month":
            # Get websites that don't have any pages.
            # return queryset.distinct().order_by('dayDate',)
            return queryset.distinct().filter(dayDate__range=[today, nextDate(nextDay, 1)])
        if self.value() == "uptill_next_3_months":
            # Get websites that have at least one page.
            return queryset.distinct().filter(dayDate__range=[today, nextDate(nextDay, 3)])
        if self.value() == "uptill_next_6_months":
            # Get websites that have at least one page.
            return queryset.distinct().filter(dayDate__range=[today, nextDate(nextDay, 6)])
        if self.value() == "uptill_next_year":
            # Get websites that have at least one page.
            return queryset.distinct().filter(dayDate__range=[today, nextDate(nextDay, 12)])
        if self.value() == "from_last_month":
            # Get websites that have at least one page.
            return queryset.distinct().filter(dayDate__range=[nextDate(nextDay, -1), today])
        if self.value() == "from_last_year":
            # Get websites that have at least one page.
            return queryset.distinct().filter(dayDate__range=[nextDate(nextDay, -12), today])


@admin.register(ActivityDetails)
class ActivityDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'dayDate']
    list_filter = (futureDatesFilter,)
    search_fields = ['name', 'dayDate']


@admin.register(ActiveParticipants)
class ActiveParticipantsAdmin(admin.ModelAdmin):
    list_display = ['id', 'prtcpntId', 'actId']
    search_fields = ['prtcpntId__email', 'actId__name']


@admin.register(WaitingParticipants)
class WaitingParticipantsAdmin(admin.ModelAdmin):
    list_display = ['id', 'prtcpntId', 'actId']
    search_fields = ['prtcpntId__email', 'actId__name']


@admin.register(PermaRemParticipants)
class PermaRemParticipantsAdmin(admin.ModelAdmin):
    list_display = ['id', 'prtcpntId', 'actId']
    search_fields = ['prtcpntId__email', 'actId__name']


@admin.register(UserFriend)
class UserFriendAdmin(admin.ModelAdmin):
    list_display = ['id', 'myId', 'friendId']
    search_fields = ['myId__email', 'friendId__email']


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'myId', 'friendId']
    search_fields = ['myId__email', 'friendId__email']


@admin.register(HobbyDetails)
class HobbyDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'hobbyName', ]


@admin.register(CategoryDetails)
class CategoryDetailsAdmin(admin.ModelAdmin):
    list_display = ['id', 'categoryName', ]


@admin.register(ActComment)
class ActCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'forActivity', 'idOwner']
    search_fields = ['forActivity__name',
                     'idOwner__first_name', 'idOwner__pseudo_name']


@admin.register(BlockedBy)
class BlockedByAdmin(admin.ModelAdmin):
    list_display = ['id', 'theManWhoBlocked', 'profileIdToBlock']
    search_fields = ['theManWhoBlocked__first_name',
                     'profileIdToBlock__first_name']


@admin.register(ChatModel)
class ChatModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'chatName']
    search_fields = ['chatName']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'forChat']
    search_fields = ['author', 'forChat__name']


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = UserInfo
        fields = ('email',)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = UserInfo
        fields = ('email', 'pseudo_name', 'password', 'first_name',
                  'last_name', 'is_active', 'is_admin', 'image')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('pseudo_name',
         'first_name', 'last_name', 'is_new', 'image')}),
        ('Social info', {'fields': ('socialImageUrl', 'aboutYourself',
         'personalHobbyList')}),
        ('Permissions', {'fields': ('is_admin', 'shadowUser', 'isAnonymous')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'pseudo_name', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'pseudo_name')
    ordering = ('email',)
    filter_horizontal = ()
    list_display = ['id', 'email', 'first_name', 'pseudo_name']


# Now register the new UserAdmin...
admin.site.register(UserInfo, UserAdmin)

# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
