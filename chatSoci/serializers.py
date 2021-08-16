from soci3LApp.commonSrlzrs import ParticipantsSerializer
from rest_framework import serializers
from soci3LApp.models import ChatMessage, ChatModel, UserInfo


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatModel
        fields = "__all__"

    def to_representation(self, instance):
        isNew = False
        myId = self.context.get("myId")
        for theirId in list(instance.newMessagesFor.values('id')):
            if myId == theirId['id']:
                isNew = True
                break
        rep = super().to_representation(instance)
        msgs = instance.chatMessages.all()
        if msgs:
            lastMsg = MessageSerializer(msgs.first()).data
        else:
            lastMsg = {'messageContent': ''}
        rep['lastMessage'] = lastMsg
        rep['newMessagesFor'] = isNew
        rep['chatParticipants'] = ParticipantsSerializer(
            instance.chatParticipants.all(), many=True).data
        return rep


class ChatUpdtSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatModel
        fields = "__all__"

    def to_representation(self, instance):
        isNew = False
        myjson = self.context
        myId = myjson['myId']
        newMsg = myjson['new_msg']
        prtcpnts = myjson['prtcpnts']
        for theirId in list(instance.newMessagesFor.values('id')):
            if myId == theirId['id']:
                isNew = True
                break
        rep = super().to_representation(instance)
        rep['lastMessage'] = newMsg
        rep['newMessagesFor'] = isNew
        rep['chatParticipants'] = prtcpnts
        return rep


class ProfileChatSerializer(serializers.ModelSerializer):
    myChats = ChatSerializer(many=True, read_only=True, source='chatModels')

    class Meta:
        model = UserInfo
        fields = (
            'id',
            'pseudo_name',
            'first_name',
            'last_name',
            'myChats',
        )
