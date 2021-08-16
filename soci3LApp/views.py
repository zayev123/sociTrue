from soci3LApp.commonSrlzrs import BlockProfilesSerializer
from rest_framework.views import APIView

from soci3LApp.models import UserInfo

import base64
# Create your views here.
from .serializers import ActivitySerializer, ActivitySerializerforListView, ActivitySerializerforRetrieveView, ActvtyCmmntPgSrlzr, CategSerializer, CommentSerializer, JustId, ProfileListSerializer, HobbySerializer, ProfileSchedSrlzr, ProfileSerializer, ProfileUpdateSerializer, PrtcptActvtSrlzr, PrtcptfieldSrlzr, RmPrtcpSrlzr, SwapSrlzr, actDeleteSerializer
from .models import ActComment, ActiveParticipants, ActivityDetails, CategoryDetails, FriendRequest, HobbyDetails, PermaRemParticipants, UserFriend, WaitingParticipants

from rest_framework import generics, permissions


from rest_framework.response import Response

from soci_3_api.myHttpFunctions import createPostWithImage, getBlockedBys, getMyProfile, myBlockGetFunction, myBlocksOnlyFunction, myDefGetiIndividual, myDefGetList, myPost, putWithImage
import io
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from datetime import date, timedelta

import logging
log = logging.getLogger('lapview')


def decodeImage(data):
    try:
        data = base64.b64decode(data.encode('UTF-8'))
        buf = io.BytesIO(data)
        img = Image.open(buf)
        return img
    except:
        return None


class ActivitiesCreateView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = ActivitySerializer

    def post(self, request, *args, **kwargs):
        myuser = request.user
        myObject = ActivityDetails()
        mySerializer = ActivitySerializer(myObject, data=request.data)
        mySerializer.is_valid(raise_exception=True)

        copy = createPostWithImage(mySerializer, myObject, 'activity')
        if myObject.organizerDetails == None:
            myObject.organizerDetails = UserInfo.objects.get(
                email='anonymous@gmail.com')
            myObject.save()
        else:
            if copy['organizerDetails'] != myuser.id:
                myuser.activityDetails.add(myObject)
            myuser.participatedActivitiesList.add(myObject.id)
            myuser.save()

        copy['organizerDetails'] = myObject.organizerDetails.id
        myResponse = Response({'message': 'success', 'data': copy})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class ActivitiesListView(generics.ListAPIView):
    serializer_class = ActivitySerializerforListView

    def get(self, request, *args, **kwargs):
        today = date.today()
        query_name = request.GET.get('name')
        query_date = request.GET.get('date')
        query_past = request.GET.get('past')
        myActs = ActivityDetails.objects.exclude(
            organizerDetails__shadowUser=True).filter(forFriend=False)

        if query_date is not None:
            myActs = myActs.filter(dayDate=query_date)

        if query_date is None:
            if query_past == 'true':
                yesterday = today - timedelta(days=1)
                myActs = myActs.filter(dayDate__range=[
                    '2017-01-01', yesterday]).order_by('-dayDate')
            else:
                myActs = myActs.filter(
                    Q(dayDate__gte=today) | Q(dayDate=None))

        if query_name is not None:
            myActs = myActs.filter(name__contains=query_name)

        splitActs = []
        j = 0
        k = 0
        myLen = len(myActs)

        for i in range(myLen):
            if i != (myLen - 1):
                if myActs[i].dayDate != myActs[i+1].dayDate:
                    mySubList = {"onDate": str(myActs[i].dayDate), 'activities today': ActivitySerializerforListView(
                        myActs[k:i+1], many=True).data}
                    k = i+1
                    splitActs.insert(j, mySubList)
                    j = j+1
            else:
                mySubList = {"onDate": str(myActs[i].dayDate), 'activities today': ActivitySerializerforListView(
                    myActs[k:i+1], many=True).data}
                splitActs.insert(j, mySubList)

        myResponse = Response({'message': 'success', 'data': splitActs})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class ActivitiesListViewI(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ActivitySerializerforListView

    def get(self, request, *args, **kwargs):
        today = date.today()
        myUser = request.user
        mySelf = BlockProfilesSerializer(myUser)
        blockList = myBlockGetFunction(mySelf)
        query_name = request.GET.get('name')
        query_date = request.GET.get('date')
        query_past = request.GET.get('past')
        myActs = ActivityDetails.objects.exclude(
            organizerDetails__shadowUser=True).filter(
                Q(forFriend=False) | Q(organizerDetails__friends__id=myUser.id) | Q(organizerDetails__myFriends__id=myUser.id))

        if query_date is not None:
            myActs = myActs.filter(dayDate=query_date)

        if query_date is None:
            if query_past == 'true':
                yesterday = today - timedelta(days=1)
                myActs = myActs.filter(dayDate__range=[
                    '2017-01-01', yesterday]).order_by('-dayDate')
            else:
                myActs = myActs.filter(
                    Q(dayDate__gte=today) | Q(dayDate=None))

        if query_name is not None:
            myActs = myActs.filter(name__contains=query_name)

        if query_name is not None:
            myActs = myActs.filter(name__contains=query_name)
        if blockList:
            myActs = myActs.exclude(organizerDetails__in=blockList)

        splitActs = []
        j = 0
        k = 0
        myLen = len(myActs)

        for i in range(myLen):
            if i != (myLen - 1):
                if myActs[i].dayDate != myActs[i+1].dayDate:
                    mySubList = {"onDate": str(myActs[i].dayDate), 'activities today': ActivitySerializerforListView(
                        myActs[k:i+1], many=True).data}
                    k = i+1
                    splitActs.insert(j, mySubList)
                    j = j+1
            else:
                mySubList = {"onDate": str(myActs[i].dayDate), 'activities today': ActivitySerializerforListView(
                    myActs[k:i+1], many=True).data}
                splitActs.insert(j, mySubList)

        myResponse = Response({'message': 'success', 'data': splitActs})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class ActvtySchdView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        mySelf = BlockProfilesSerializer(request.user)
        allBlockList = myBlockGetFunction(mySelf)
        mySchdule = ProfileSchedSrlzr(
            myUser, context={'all_blocks': allBlockList})

        myActs = mySchdule.data['participatedActivitiesList']
        splitActs = []
        j = 0
        k = 0
        myLen = len(myActs)

        for i in range(myLen):
            if i != (myLen - 1):
                if myActs[i]['dayDate'] != myActs[i+1]['dayDate']:
                    mySubList = {"onDate": str(
                        myActs[i]['dayDate']), 'activities today': myActs[k:i+1]}
                    k = i+1
                    splitActs.insert(j, mySubList)
                    j = j+1
            else:
                mySubList = {"onDate": str(
                    myActs[i]['dayDate']), 'activities today': myActs[k:i+1]}
                splitActs.insert(j, mySubList)

        myResponse = Response({'message': 'success', 'data': splitActs})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class ActivitiesDetailView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request, *args, **kwargs):
        myUser = request.user
        # print(myUser.id)
        mySelf = BlockProfilesSerializer(myUser)
        blockList = myBlocksOnlyFunction(mySelf)
        blockByList = getBlockedBys(mySelf)
        myAct = ActivityDetails.objects.get(id=kwargs['pk'])
        myOrganizer = myAct.organizerDetails
        if myAct.forFriend:
            if myOrganizer.id != myUser.id:
                if myOrganizer.friends.all().filter(id=myUser.id).exists() or myOrganizer.myFriends.all().filter(id=myUser.id).exists():
                    None
                else:
                    myResponse = Response(
                        {'message': 'success', 'data': 'This activity is restricted to friends'})
                    if myResponse.status_code == 200:
                        return myResponse
                    else:
                        return Response({'message': 'Failed'})
        mySerializer = ActivitySerializerforRetrieveView(
            myAct, context={'block_list': blockList, 'blockedBy_list': blockByList})
        myResponse = Response(
            {'message': 'success', 'data': mySerializer.data})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class ActivitiesUpdateView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = ActivitySerializer

    def put(self, request, *args, **kwargs):
        myuser = request.user
        myObject = ActivityDetails.objects.get(id=kwargs['pk'])

        mySerializer = ActivitySerializer(myObject, data=request.data)
        mySerializer.is_valid(raise_exception=True)

        mySerializer.validated_data['organizerDetails'] = myuser
        putData = putWithImage(mySerializer, myObject, 'activity')
        actUsers = myObject.participants.all()
        waitingUsers = myObject.waiting_users.all()
        usrsLngth = len(actUsers)
        capacity = putData['capacity']
        if usrsLngth > capacity:
            myIdList = actUsers.values_list('pk', flat=True)[
                capacity:usrsLngth]
            extraPrtcpnts = UserInfo.objects.filter(id__in=myIdList)
            for prtcpnt in extraPrtcpnts:
                WaitingParticipants.objects.create(
                    pastPrtcnt=True,
                    prtcpntId=prtcpnt,
                    actId=myObject,
                )
                prtcpnt.participatedActivitiesList.remove(myObject.id)
        elif usrsLngth < capacity and waitingUsers:
            myIdList = waitingUsers.values_list('pk', flat=True)[
                0: capacity - usrsLngth]
            rmndrPrtcpnts = UserInfo.objects.filter(id__in=myIdList)
            for prtcpnt in rmndrPrtcpnts:
                prtcpnt.waitingPrtcpnts.remove(myObject.id)
                prtcpnt.participatedActivitiesList.add(myObject.id)
        myResponse = Response({'message': 'success', 'data': putData})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class DeleteActView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = actDeleteSerializer

    def post(self, request, *args, **kwargs):
        userid = request.user.id
        myObject = ActivityDetails.objects.get(id=kwargs['pk'])
        if userid == myObject.organizerDetails.id:
            myObject.delete()
            return Response({'message': 'success'})
        else:
            return Response({'message': 'credentials donot match organizer details'})


class ProfilesListView(APIView):

    serializer_class = ProfileListSerializer

    def get(self, request, *args, **kwargs):
        return myDefGetList(ProfileListSerializer, UserInfo)


class ProfileUpdateView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = ProfileUpdateSerializer

    def get(self, request, *args, **kwargs):
        return myDefGetiIndividual(ProfileUpdateSerializer, UserInfo, kwargs['pk'])

    def put(self, request, *args, **kwargs):
        myObject = request.user

        mySerializer = ProfileUpdateSerializer(myObject, data=request.data)
        mySerializer.is_valid(raise_exception=True)

        putData = putWithImage(mySerializer, myObject, 'profile')
        myResponse = Response({'message': 'success', 'data': putData})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class ProfileRetrieveView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        boolblockBy = False
        myUser = request.user
        friendStatus = ''
        mySelf = BlockProfilesSerializer(myUser)
        blockByList = getBlockedBys(mySelf)
        for theirId in blockByList:
            if theirId == kwargs['pk']:
                boolblockBy = True
                break
        if boolblockBy:
            myResponse = Response(
                {'message': 'success', 'data': 'blocked-not-allowed'})
        else:
            blockList = myBlocksOnlyFunction(mySelf)
            allBlockList = blockList + blockByList
            allBlockList.append(myUser.id)
            myProf = UserInfo.objects.get(id=kwargs['pk'])

            if myProf.id == myUser.id:
                friendStatus = 'myself'

            else:
                requests = FriendRequest.objects.filter(
                    (Q(myId=myUser.id) | Q(friendId=myUser.id)))
                myFriends = UserFriend.objects.filter(
                    Q(myId=myUser.id) | Q(friendId=myUser.id))
                if myFriends.filter(Q(myId=myProf.id) | Q(friendId=myProf.id)).exists():
                    friendStatus = 'friends'
                elif requests.filter(myId=myProf.id).exists():
                    friendStatus = 'request_received'
                elif requests.filter(friendId=myProf.id).exists():
                    friendStatus = 'request_sent'
                else:
                    friendStatus = 'not_friends'

            mySerializer = ProfileSerializer(
                myProf, context={'all_blocks': allBlockList, 'block_list': blockList, 'friend_Status': friendStatus})
            myResponse = Response(
                {'message': 'success', 'data': mySerializer.data})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class HobbiesListView(APIView):
    serializer_class = HobbySerializer

    def get(self, request, *args, **kwargs):
        return myDefGetList(HobbySerializer, HobbyDetails)

    def post(self, request, *args, **kwargs):
        return myPost(request, HobbyDetails, HobbySerializer)


class CategoryListView(APIView):
    serializer_class = CategSerializer

    def get(self, request, *args, **kwargs):
        return myDefGetList(CategSerializer, CategoryDetails)

    def post(self, request, *args, **kwargs):
        return myPost(request, CategoryDetails, CategSerializer)


class ParticipateView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = PrtcptfieldSrlzr

    def get(self, request, *args, **kwargs):
        myuser = request.user
        return getMyProfile(PrtcptActvtSrlzr, myuser)

    def put(self, request, *args, **kwargs):
        myActId = request.data['actId']
        myAct = ActivityDetails.objects.get(id=myActId)
        myuser = request.user
        if myuser.permaRemPrtcpnts.all().filter(id=myActId).exists():
            myResponse = Response(
                {'message': 'success', 'data': 'Not-allowed'})

        elif len(myAct.participants.all()) >= myAct.capacity:
            myuser.waitingPrtcpnts.add(myActId)
            myuser.save()

            myResponse = Response(
                {'message': 'success', 'data': 'waiting-list-entered'})
        else:
            myuser.participatedActivitiesList.add(myActId)
            myuser.save()
            myModelList = myuser.participatedActivitiesList.all()
            myJsonList = JustId(myModelList, many=True)

            myResponse = Response(
                {'message': 'success', 'data': myJsonList.data})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class UnParticipateView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = PrtcptfieldSrlzr

    def get(self, request, *args, **kwargs):
        myuser = request.user
        return getMyProfile(PrtcptActvtSrlzr, myuser)

    def put(self, request, *args, **kwargs):
        myActId = request.data['actId']
        myAct = ActivityDetails.objects.get(id=myActId)
        myuser = request.user
        myuser.participatedActivitiesList.remove(myActId)
        waiters = myAct.waiting_users.all()
        if waiters:
            waiterId = waiters[0].id
            waiter = UserInfo.objects.get(id=waiterId)
            waiter.waitingPrtcpnts.remove(myAct.id)
            waiter.participatedActivitiesList.add(myAct.id)
        myuser.save()

        myResponse = Response(
            {'message': 'success', 'data': 'unparticipated_done'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class RmPrtcpntView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = RmPrtcpSrlzr

    def put(self, request, *args, **kwargs):
        myuser = request.user
        myActId = request.data['actId']
        prtcpId = request.data['prtcpntId']
        myAct = ActivityDetails.objects.get(id=myActId)
        if myAct.organizerDetails.id == myuser.id or myuser.email == "admin@gmail.com":
            prtcp = UserInfo.objects.get(id=prtcpId)
            PermaRemParticipants.objects.create(
                prtcpntId=prtcp,
                actId=myAct,
            )
            myAct.participants.remove(prtcpId)
            waiters = myAct.waiting_users.all()
            if waiters:
                waiter = waiters[0]
                waiter.waitingPrtcpnts.remove(myActId)
                waiter.participatedActivitiesList.add(myActId)
            myAct.save()

            myResponse = Response({'message': 'success', 'data': 'removed'})
        else:
            myResponse = Response(
                {'message': 'success', 'data': 'Not-allowed'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class SwpPrtcpntView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = SwapSrlzr

    def put(self, request, *args, **kwargs):
        myuser = request.user
        myActId = request.data['actId']
        wantedId = request.data['wantedPrt']
        unwantedId = request.data['unwantedPrt']
        myAct = ActivityDetails.objects.get(id=myActId)
        if myAct.organizerDetails.id == myuser.id or myuser.email == "admin@gmail.com":
            wanted = myAct.waiting_users.all().get(id=wantedId)
            unwanted = myAct.participants.all().get(id=unwantedId)
            activeObj = ActiveParticipants.objects.filter(
                actId=myActId).filter(prtcpntId=unwantedId).first()
            waitingObj = WaitingParticipants.objects.filter(
                actId=myActId).filter(prtcpntId=wantedId).first()

            activeObj.prtcpntId = wanted
            activeObj.save()

            waitingObj.prtcpntId = unwanted
            waitingObj.save()

            myResponse = Response({'message': 'success', 'data': 'swaped'})
        else:
            myResponse = Response(
                {'message': 'success', 'data': 'Not-allowed'})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class CommentPageView(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = CommentSerializer

    def get(self, request, *args, **kwargs):
        return myDefGetiIndividual(ActvtyCmmntPgSrlzr, ActivityDetails, kwargs['pk'])

    def post(self, request, *args, **kwargs):
        # return myPost(request, ActComment, CommentSerializer)
        myuser = request.user
        myObject = ActComment()
        mySerializer = CommentSerializer(myObject, data=request.data)
        mySerializer.is_valid(raise_exception=True)
        mySerializer.validated_data['idOwner'] = myuser
        copy = createPostWithImage(mySerializer, myObject, 'comment')

        myResponse = Response({'message': 'success', 'data': copy})
        if myResponse.status_code == 200:
            return myResponse
        else:
            return Response({'message': 'Failed'})


class DeleteCommView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = JustId

    def post(self, request, *args, **kwargs):
        userid = request.user.id
        myObject = ActComment.objects.get(id=request.data['id'])

        if userid == myObject.idOwner.id:
            myObject.delete()
            return Response({'message': 'success'})
        else:
            return Response({'message': 'credentials donot match owner details'})
