from rest_framework import serializers
from .models import ActComment, ActivityDetails, CategoryDetails, FriendRequest, PermaRemParticipants, UserFriend, UserInfo, HobbyDetails
from .commonSrlzrs import ActvtySrlzerForOtherLists, ParticipantsDetsSerializer, ParticipantsSerializer
from django.db.models import Q
from datetime import date


class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = HobbyDetails
        fields = "__all__"


class CategSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryDetails
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActComment
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['idOwner'] = ParticipantsSerializer(instance.idOwner).data
        return rep


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityDetails
        fields = "__all__"


class ActivitySerializerforRetrieveView(serializers.ModelSerializer):
    participantsList = ParticipantsDetsSerializer(
        many=True, read_only=True, source='participants')
    waitingPrtcpnts = ParticipantsDetsSerializer(
        many=True, read_only=True, source='waiting_users')

    class Meta:
        model = ActivityDetails
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['organizerDetails'] = ParticipantsSerializer(
            instance.organizerDetails).data
        rep['category'] = CategSerializer(instance.category).data
        return rep


class actDeleteSerializer(serializers.Serializer):
    actId = serializers.IntegerField()


class ActvtyCmmntPgSrlzr(serializers.ModelSerializer):
    commentsList = CommentSerializer(
        many=True, read_only=True, source='actComment')

    class Meta:
        model = ActivityDetails
        fields = ('id', 'name', 'image', 'commentsList')


class ActivitySerializerforListView(serializers.ModelSerializer):
    participantsList = ParticipantsSerializer(
        many=True, read_only=True, source='participants')

    class Meta:
        model = ActivityDetails
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['organizerDetails'] = ParticipantsSerializer(
            instance.organizerDetails).data
        rep['category'] = CategSerializer(instance.category).data
        rep['participantsList'] = len(rep['participantsList'])
        return rep


class ActvtySrlzerForOrganizer(serializers.ModelSerializer):
    participantsList = ParticipantsSerializer(
        many=True, read_only=True, source='participants')

    class Meta:
        model = ActivityDetails
        fields = ('id', 'name', 'image', 'city', 'dayDate',
                  'theTime', 'capacity', 'category', 'participantsList')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['category'] = CategSerializer(instance.category).data
        rep['participantsList'] = len(rep['participantsList'])
        return rep


class ProfileListSerializer(serializers.ModelSerializer):
    activityDetailsAsOrganizer = ActvtySrlzerForOrganizer(
        many=True, read_only=True, source='activityDetails')

    class Meta:
        model = UserInfo
        fields = (
            'id',
            'pseudo_name',
            'first_name',
            'last_name',
            'gender',
            'last_login',
            'date_joined',
            'image',
            'socialImageUrl',
            'aboutYourself',
            'birthDate',
            'personalHobbyList',
            'participatedActivitiesList',
            'activityDetailsAsOrganizer'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['personalHobbyList'] = instance.personalHobbyList.all().values_list()
        rep['participatedActivitiesList'] = len(
            rep['participatedActivitiesList'])
        return rep


class ProfileUpdateSerializer(serializers.ModelSerializer):
    activityDetailsAsOrganizer = ActvtySrlzerForOrganizer(
        many=True, read_only=True, source='activityDetails')

    class Meta:
        model = UserInfo
        fields = (
            'id',
            'pseudo_name',
            'first_name',
            'last_name',
            'gender',
            'last_login',
            'date_joined',
            'image',
            'bas64Image',
            'imageType',
            'phoneNumber',
            'birthDate',
            'socialImageUrl',
            'aboutYourself',
            'personalHobbyList',
            'participatedActivitiesList',
            'activityDetailsAsOrganizer'
        )


class ProfileSerializer(serializers.ModelSerializer):
    activityDetailsAsOrganizer = ActvtySrlzerForOrganizer(
        many=True, read_only=True, source='activityDetails')

    class Meta:
        model = UserInfo
        fields = (
            'id',
            'email',
            'pseudo_name',
            'first_name',
            'last_name',
            'last_login',
            'gender',
            'date_joined',
            'image',
            'phoneNumber',
            'socialImageUrl',
            'aboutYourself',
            'birthDate',
            'personalHobbyList',
            'participatedActivitiesList',
            'activityDetailsAsOrganizer',
            'friends',
            'friendStatus',
            'isBlocked',
        )

    def to_representation(self, instance):
        boolblock = False
        hisId = instance.id
        for theirId in self.context.get("block_list"):
            if theirId == hisId:
                boolblock = True
                break
        rep = super().to_representation(instance)
        rep['isBlocked'] = boolblock
        rep['personalHobbyList'] = HobbySerializer(
            instance.personalHobbyList.all(), many=True).data
        rep['participatedActivitiesList'] = ActvtySrlzerForOtherLists(instance.participatedActivitiesList.exclude(
            organizerDetails__in=self.context.get("all_blocks")).exclude(organizerDetails__shadowUser=True), many=True).data
        rep['friends'] = len(UserFriend.objects.filter(
            Q(myId=hisId) | Q(friendId=hisId)))
        rep['friendStatus'] = self.context.get("friend_Status")
        return rep


class ProfileSchedSrlzr(serializers.ModelSerializer):

    class Meta:
        model = UserInfo
        fields = (
            'participatedActivitiesList',
        )

    def to_representation(self, instance):
        today = date.today()
        rep = super().to_representation(instance)
        rep['participatedActivitiesList'] = ActvtySrlzerForOtherLists(instance.participatedActivitiesList.filter(
            Q(dayDate__gte=today) | Q(dayDate=None)).exclude(organizerDetails__in=self.context.get("all_blocks")).exclude(organizerDetails__shadowUser=True), many=True).data
        return rep


class PrtcptActvtSrlzr(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = (
            'participatedActivitiesList',
        )


class PrtcptfieldSrlzr(serializers.Serializer):
    actId = serializers.IntegerField()


class JustId(serializers.Serializer):
    id = serializers.IntegerField()


class RmPrtcpSrlzr(serializers.ModelSerializer):
    class Meta:
        model = PermaRemParticipants
        fields = "__all__"


class SwapSrlzr(serializers.Serializer):
    actId = serializers.IntegerField()
    wantedPrt = serializers.IntegerField()
    unwantedPrt = serializers.IntegerField()
