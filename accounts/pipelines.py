from soci3LApp.models import UserInfo
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile


def get_remote_image(myUser):
    if myUser.socialImageUrl and not myUser.image:
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(urlopen(myUser.socialImageUrl).read())
        img_temp.flush()
        myUser.image.save(f"profile{myUser.id}", File(img_temp))
        myUser.socialImageUrl = None
    myUser.save()


def create_custom_user(backend, user, is_new, response, *args, **kwargs):
    # print('isResponse')
    # '''
    if user:
        user.is_new = False
        user.save(update_fields=['is_new'])
        return {'is_new': False}

    if backend.name == 'google-oauth2':
        if 'picture' in response:
            myImage = response['picture'].split("=")
            myUrl = myImage[0] + '=s300-c'
        else:
            myUrl = None

        myUser = UserInfo.objects.create(
            email=response['email'],
            first_name=response['given_name'],
            last_name=response['family_name'],
            pseudo_name=response['name'],
            is_active=True,
            is_new=False,
            socialImageUrl=myUrl,
        )
        get_remote_image(myUser)
        return {
            'user': myUser
        }
    # '''
    # '''
    elif backend.name == 'facebook':
        myUser = UserInfo.objects.create(
            email=response['id'] + '@' + backend.name,
            first_name=response['first_name'],
            last_name=response['last_name'],
            pseudo_name=response['name'],
            is_active=True,
            is_new=False,
            socialImageUrl=response['picture']['data']['url'],
        )
        get_remote_image(myUser)
        return {
            'user': myUser
        }
        # '''
