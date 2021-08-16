from soci3LApp.models import UserInfo
from rest_framework.response import Response
from base64 import b64decode
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from datetime import date


def myBlockGetFunction(mySelf):
    blockedByRawList = mySelf.data['blockedBys']
    blockerRawList = mySelf.data['blocked']
    if blockedByRawList or blockerRawList:
        blockedByList = []
        if blockedByRawList:
            for blockedBy in blockedByRawList:
                blockedByList.append(blockedBy['theManWhoBlocked'])
        blockerList = []
        if blockerRawList:
            for blocker in blockerRawList:
                blockerList.append(blocker['profileIdToBlock'])
        block = blockedByList + blockerList
        return block
    else:
        return []


def myBlocksOnlyFunction(mySelf):
    blockerRawList = mySelf.data['blocked']
    blockerList = []
    if blockerRawList:
        for blocker in blockerRawList:
            blockerList.append(blocker['profileIdToBlock'])
        return blockerList
    else:
        return []


def getBlockedBys(mySelf):
    blockedByRawList = mySelf.data['blockedBys']
    blockedByList = []
    if blockedByRawList:
        for blocker in blockedByRawList:
            blockedByList.append(blocker['theManWhoBlocked'])
        return blockedByList
    else:
        return []


def changeParticipantsList(blockList, partsList):
    if blockList:
        if partsList:
            for i in range(len(partsList)):
                for blockId in blockList:
                    if partsList[i]['id'] == blockId:
                        del partsList[i]
                        break


def myDefGetList(mySrlzr, myClass):
    myData = mySrlzr(myClass.objects.all(), many=True)
    myResponse = Response({'message': 'success', 'data': myData.data})
    if myResponse.status_code == 200:
        return myResponse
    else:
        return Response({'message': 'Failed'})


def myDefGetiIndividual(mySerlzr, myClass, myInt):
    mySerializer = mySerlzr(myClass.objects.get(id=myInt))
    myResponse = Response({'message': 'success', 'data': mySerializer.data})
    if myResponse.status_code == 200:
        return myResponse
    else:
        return Response({'message': 'Failed'})


def getMyProfile(mySerlzr, myUser):
    mySerializer = mySerlzr(myUser)
    myResponse = Response({'message': 'success', 'data': mySerializer.data})
    if myResponse.status_code == 200:
        return myResponse
    else:
        return Response({'message': 'Failed'})


def myPost(request, myClass, laSerializer):
    myObject = myClass()
    mySerializer = laSerializer(myObject, data=request.data)
    mySerializer.is_valid(raise_exception=True)
    mySerializer.save()
    myResponse = Response({'message': 'success', 'data': mySerializer.data})
    if myResponse.status_code == 200:
        return myResponse
    else:
        return Response({'message': 'Failed'})


def blockPost(request, myClass, laSerializer):
    myUser = request.user
    myObject = myClass()
    mySerializer = laSerializer(myObject, data=request.data)
    mySerializer.is_valid(raise_exception=True)
    mySerializer.validated_data['theManWhoBlocked'] = myUser
    blockedId = mySerializer.validated_data['profileIdToBlock']
    mySerializer.save()

    blockedId = mySerializer.data['profileIdToBlock']
    myUser.friends.remove(blockedId)
    myUser.myFriends.remove(blockedId)

    today = date.today()
    myActs = myUser.activityDetails.all().filter(
        Q(dayDate__gte=today) | Q(dayDate=None)).filter(Q(participants__pk=blockedId) | Q(waiting_users__pk=blockedId))

    if myActs:
        blockedUser = UserInfo.objects.get(id=blockedId)
        blockedUser.participatedActivitiesList.remove(*myActs)
        blockedUser.waitingPrtcpnts.remove(*myActs)
        for myAct in myActs:
            waiters = myAct.waiting_users.all()
            if waiters:
                waiter = waiters[0]
                waiter.waitingPrtcpnts.remove(myAct.id)
                waiter.participatedActivitiesList.add(myAct.id)

    myResponse = Response({'message': 'success', 'data': mySerializer.data})
    if myResponse.status_code == 200:
        return myResponse
    else:
        return Response({'message': 'Failed'})


def myPut(request, myClass, myId, mySrlzr):
    myObject = myClass.objects.get(id=myId)
    mySerializer = mySrlzr(myObject, data=request.data)
    mySerializer.is_valid(raise_exception=True)
    mySerializer.save()
    myResponse = Response({'message': 'success', 'data': mySerializer.data})
    if myResponse.status_code == 200:
        return myResponse
    else:
        return Response({'message': 'Failed'})


def decodeImage(data):
    try:
        data = b64decode(data.encode('UTF-8'))
        buf = BytesIO(data)
        return buf
    except:
        return None


def createPostWithImage(mySerializer, myObject, imgName):
    imgCheck = False

    if 'bas64Image' in mySerializer.validated_data and 'imageType' in mySerializer.validated_data:
        if mySerializer.validated_data['imageType'] == 'PNG':
            formatType = 'PNG'
            ext = ".png"
            contentType = 'image/png'
        elif mySerializer.validated_data['imageType'] == 'JPEG':
            formatType = 'JPEG'
            ext = ".jpg"
            contentType = 'image/jpeg'

        imgCheck = True
        img = decodeImage(mySerializer.validated_data['bas64Image'])

    mySerializer.validated_data['bas64Image'] = ''
    mySerializer.save()
    copy = mySerializer.data

    if imgCheck:
        myImage = InMemoryUploadedFile(img, field_name=None, name=imgName + str(
            mySerializer.data['id']) + ext, content_type=contentType, size=img.tell, charset=None)
        myObject.image = myImage
        myObject.save(update_fields=['image'])
        copy['image'] = myObject.image.url

    return copy


def putWithImage(mySerializer, myObject, imgName):
    if 'bas64Image' in mySerializer.validated_data and 'imageType' in mySerializer.validated_data:
        if mySerializer.validated_data['imageType'] == 'PNG':
            formatType = 'PNG'
            ext = ".png"
            contentType = 'image/png'
        elif mySerializer.validated_data['imageType'] == 'JPEG':
            formatType = 'JPEG'
            ext = ".jpg"
            contentType = 'image/jpeg'

        imgCheck = True
        img = decodeImage(mySerializer.validated_data['bas64Image'])
        myObject.image = InMemoryUploadedFile(img, field_name=None, name=imgName + str(
            myObject.id) + ext, content_type=contentType, size=img.tell, charset=None)

    mySerializer.validated_data['bas64Image'] = ''
    mySerializer.save()
    srData = mySerializer.data

    return srData


def rlTmeMsgImage(myObject, msgData, imgFlder):
    if msgData['base64Image'] != '' and msgData['imageType'] != '':
        if msgData['imageType'] == 'PNG':
            ext = ".png"
            contentType = 'image/png'
        elif msgData['imageType'] == 'JPEG':
            ext = ".jpg"
            contentType = 'image/jpeg'

        img = decodeImage(msgData['base64Image'])
        myObject.image = InMemoryUploadedFile(img, field_name=None, name='Z9E0U5s41ApP' + imgFlder + str(
            myObject.id) + ext, content_type=contentType, size=img.tell, charset=None)
        myObject.save()
