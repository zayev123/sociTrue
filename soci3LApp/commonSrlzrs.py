from rest_framework import serializers
from .models import ActivityDetails, BlockedBy, CategoryDetails, UserInfo
from django.db.models import Q
from datetime import date


class MyCategSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryDetails
        fields = "__all__"


class ParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ('id', 'pseudo_name', 'first_name', 'last_name',
                  'gender', 'image', 'socialImageUrl', 'isAnonymous')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return rep
#############################


class FilteredPrtcpntsSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.exclude(id__in=self.context.get("blockedBy_list"))
        return super(FilteredPrtcpntsSerializer, self).to_representation(data)


class ParticipantsDetsSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = FilteredPrtcpntsSerializer
        model = UserInfo
        fields = ('id', 'pseudo_name', 'first_name', 'last_name',
                  'gender', 'image', 'socialImageUrl', 'isBlocked')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        boolblock = False
        myId = instance.id
        for theirId in self.context.get("block_list"):
            if theirId == myId:
                boolblock = True
                break
        rep['isBlocked'] = boolblock
        return rep
######################################


class ActvtySrlzerForOtherLists(serializers.ModelSerializer):
    participantsList = ParticipantsSerializer(
        many=True, read_only=True, source='participants')

    class Meta:
        model = ActivityDetails
        fields = ('id', 'name', 'image', 'city', 'dayDate', 'theTime',
                  'capacity', 'category', 'organizerDetails', 'participantsList')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['organizerDetails'] = ParticipantsSerializer(
            instance.organizerDetails).data
        rep['category'] = MyCategSerializer(instance.category).data
        rep['participantsList'] = len(rep['participantsList'])
        return rep


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedBy
        fields = "__all__"


class BlockViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedBy
        fields = "__all__"

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['theManWhoBlocked'] = ParticipantsSerializer(
            instance.theManWhoBlocked).data
        rep['profileIdToBlock'] = ParticipantsSerializer(
            instance.profileIdToBlock).data
        return rep


class BlockProfilesSerializer(serializers.ModelSerializer):
    blocked = BlockSerializer(many=True, read_only=True, source='blocker')
    blockedBys = BlockSerializer(many=True, read_only=True, source='blockedBy')

    class Meta:
        model = UserInfo
        fields = (
            'id',
            'blocked',
            'blockedBys',
        )


class BlockViewProfilesSerializer(serializers.ModelSerializer):
    blocked = BlockViewSerializer(many=True, read_only=True, source='blocker')
    blockedBys = BlockViewSerializer(
        many=True, read_only=True, source='blockedBy')

    class Meta:
        model = UserInfo
        fields = (
            'id',
            'blocked',
            'blockedBys',
        )
