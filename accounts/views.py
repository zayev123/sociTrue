from soci3LApp.commonSrlzrs import BlockProfilesSerializer, BlockSerializer, BlockViewProfilesSerializer
from soci3LApp.serializers import JustId, PrtcptfieldSrlzr
from rest_framework import generics, permissions, status
from rest_framework.response import Response
#from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from knox.models import AuthToken
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, UserStatusSerializer, friendRqstSrlzr, friendSrlzr
from social_django.utils import load_backend, load_strategy
from social.exceptions import AuthAlreadyAssociated
from soci3LApp.models import ActivityDetails, FriendRequest, UserFriend, UserInfo, BlockedBy
from django.http import Http404
from django.contrib.auth.signals import user_logged_out
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from soci_3_api.myHttpFunctions import blockPost, getBlockedBys, getMyProfile, myBlockGetFunction

from soci_3_api.settings import GOOGLE_WEB_ID

# Register Api


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        myResponse = Response({
            "message": "success",
            'data': {"user": UserSerializer(
                user,
                context=self.get_serializer_context()
            ).data,
                "token": AuthToken.objects.create(user)[1]}
        })
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


# Login Api
class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        myResponse = Response({
            "message": "success",
            'data': {"user": UserSerializer(
                user,
                context=self.get_serializer_context()
            ).data,
                "token": AuthToken.objects.create(user)[1]}
        })
        if myResponse.status_code == 200:
            myUser = UserInfo.objects.get(email=request.data['email'])
            myUser.save()
            return myResponse
        else:
            return Response({'message': 'Failed'})


class Logout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        myUser = request.user
        request._auth.delete()
        tokenExists = AuthToken.objects.filter(user=myUser.id).exists()
        if not tokenExists:
            myUser.isLoggedIn = False
            myUser.save(update_fields=['isLoggedIn'])
        user_logged_out.send(sender=myUser.__class__,
                             request=request, user=myUser)
        myResponse = Response({
            "message": "success",
            'data': 'logged out'
        })
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


# Get User Api

#User = get_user_model()

class BlockView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = BlockSerializer

    def get(self, request, *args, **kwargs):
        return getMyProfile(BlockViewProfilesSerializer, request.user)

    def post(self, request, *args, **kwargs):
        return blockPost(request, BlockedBy, BlockSerializer)


class UnBlockView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = JustId

    def post(self, request, *args, **kwargs):
        userid = request.user.id
        myObject = BlockedBy.objects.filter(theManWhoBlocked=request.user.id).get(
            profileIdToBlock=request.data['id'])

        if userid == myObject.theManWhoBlocked.id:
            myObject.delete()
            return Response({'message': 'success'})
        else:
            return Response({'message': 'credentials donot match blocker details'})


class SocialSignUp(APIView):
    def get(self, request, *args, **kwargs):
        provider = request.headers['provider']
        access_token = request.headers['accessToken']
        strategy = load_strategy(request)
        backend = load_backend(
            strategy=strategy, name=provider, redirect_uri=None)
        platform = request.headers['platform']

        try:
            # if `authed_user` is None, python-social-auth will make a new user,
            # else this social account will be associated with the user you pass in
            if platform == 'googleWeb':
                user = backend.do_auth(
                    access_token, platform=platform, googleWebId=GOOGLE_WEB_ID)
            else:
                user = backend.do_auth(access_token, platform=platform)
            # '''
            myResponse = Response({
                "message": "success",
                'data': {
                    "user": UserSerializer(user).data,
                    "token": AuthToken.objects.create(user)[1],
                    'is_new': user.is_new
                },
            })

            if myResponse.status_code == 200:
                return myResponse
            else:
                return Response({'message': 'Failed'})
            # '''
            # return Response({'message': 'Failed'})

        except AuthAlreadyAssociated:
            # You can't associate a social account with more than user
            return Response({"message": "That social media account is already in use"},
                            status=status.HTTP_400_BAD_REQUEST)
# """


class ProfilesStatusView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = UserStatusSerializer

    def get(self, request, *args, **kwargs):
        myUser = request.user
        mySelf = BlockProfilesSerializer(myUser)
        allUsers = UserInfo.objects.all()
        totalUsers = len(allUsers)
        blockList = myBlockGetFunction(mySelf)
        blockList.append(myUser.id)
        myUsers = allUsers.exclude(id__in=blockList)

        myPage = kwargs['pageSize'] * kwargs['pageNumber']
        myData1 = UserStatusSerializer(myUsers.order_by(
            '-date_joined')[myPage:myPage + kwargs['pageSize']], many=True)
        myData2 = UserStatusSerializer(myUsers.filter(isLoggedIn=True).order_by(
            '-last_login')[myPage:myPage + kwargs['pageSize']], many=True)
        myResponse = Response({'message': 'success', 'data': {
                              'new_users': myData1.data, 'loggedIn_users': myData2.data, 'totalUsers': totalUsers}})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class SendFrnRqstView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = friendSrlzr

    def put(self, request, *args, **kwargs):
        mySelf = request.user
        friendId = request.data['friendId']
        mySelf.friendRequests.add(friendId)
        mySelf.save()
        myResponse = Response(
            {'message': 'success', 'data': 'Requested'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class AccptFrnRqstView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = friendRqstSrlzr

    def put(self, request, *args, **kwargs):
        mySelf = request.user
        friendId = request.data['friendId']
        friendship = request.data['friendship']
        mySelf.receivedRequests.remove(friendId)
        if friendship == 'accept':
            mySelf.friends.add(friendId)
            mySelf.save()
            myResponse = Response(
                {'message': 'success', 'data': 'Accepted'})
        else:
            mySelf.save()
            myResponse = Response(
                {'message': 'success', 'data': 'Denied'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class FrndLstView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        boolblockBy = False
        myUser = request.user
        mySelf = BlockProfilesSerializer(myUser)
        blockByList = myBlockGetFunction(mySelf)
        myProfId = kwargs['pk']
        for theirId in blockByList:
            if theirId == myProfId:
                boolblockBy = True
                break
        if boolblockBy:
            myResponse = Response(
                {'message': 'success', 'data': 'blocked-not-allowed'})
            if myResponse.status_code == 200:
                return myResponse
            else:
                return Response({'message': 'Failed'})
        myFriends = UserFriend.objects.filter(
            Q(myId=myProfId) | Q(friendId=myProfId))
        friendsList = []

        for friend in myFriends:
            if friend.myId.id == myProfId:
                friendsList.append(UserStatusSerializer(friend.friendId).data)
            else:
                friendsList.append(UserStatusSerializer(friend.myId).data)
        myResponse = Response({'message': 'success', 'data': friendsList})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class FrndRcvdRqLstView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        myFriendRcvdRqs = UserStatusSerializer(
            myUser.receivedRequests.all(), many=True)

        myResponse = Response(
            {'message': 'success', 'data': myFriendRcvdRqs.data})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class FrndSntRqLstView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        myFriendSntRqs = UserStatusSerializer(
            myUser.friendRequests.all(), many=True)

        myResponse = Response(
            {'message': 'success', 'data': myFriendSntRqs.data})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class RmvFriendView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = friendSrlzr

    def put(self, request, *args, **kwargs):
        mySelf = request.user
        friendId = request.data['friendId']
        mySelf.friends.remove(friendId)
        mySelf.myFriends.remove(friendId)
        myResponse = Response(
            {'message': 'success', 'data': 'Removed'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class RmvFrndRqstView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = friendSrlzr

    def put(self, request, *args, **kwargs):
        mySelf = request.user
        friendId = request.data['friendId']
        mySelf.friendRequests.remove(friendId)
        myResponse = Response(
            {'message': 'success', 'data': 'Removed'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class BcmOrgnzrView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = PrtcptfieldSrlzr

    def put(self, request, *args, **kwargs):
        mySelf = request.user
        myActId = request.data['actId']
        myAct = ActivityDetails.objects.get(id=myActId)
        if myAct.organizerDetails.email == 'anonymous@gmail.com':
            myAct.organizerDetails = mySelf
            myAct.participants.add(mySelf.id)
            myAct.save()
            myResponse = Response(
                {'message': 'success', 'data': 'You are now an organizer'})
        else:
            myResponse = Response(
                {'message': 'success', 'data': 'An organizer already exists'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})
