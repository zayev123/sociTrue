#from asgiref.sync import async_to_sync
#from channels.generic.websocket import WebsocketConsumer

import json
from soci3LApp.commonSrlzrs import ParticipantsSerializer
from soci_3_api.myHttpFunctions import rlTmeMsgImage

from rest_framework import HTTP_HEADER_ENCODING
from soci3LApp.models import ChatMessage, ChatModel, UserInfo
from channels.generic.websocket import AsyncWebsocketConsumer
from chatSoci.serializers import ChatSerializer, ChatUpdtSerializer, MessageSerializer
from channels.db import database_sync_to_async
from knox.auth import TokenAuthentication
# '''
knoxAuth = TokenAuthentication()


class MyChatsCnsmr(AsyncWebsocketConsumer):

    myUser = None
    myChats = None
    theKwargs = None
    personalRoom = None
    personalGroup = None
    chatRoom = None
    chatGroup = None
    theParticipants = None
    jsonPrtcpnts = None
    userIds = None

    theChat = None

    @database_sync_to_async
    def authcteUsr(self):
        try:
            self.myUser = UserInfo.objects.get(id=self.theKwargs['profId'])
        except Exception as e:
            print(e)

    @database_sync_to_async
    def fetch_my_chats(self):
        self.myChats = self.myUser.chatModels.all()
        myJsonChats = ChatSerializer(self.myChats, context={
                                     'myId': self.theKwargs['profId']}, many=True).data

        return myJsonChats

    @database_sync_to_async
    def fetch_my_chat(self, newMsg):
        myChat = self.theChat
        myJsonChat = ChatUpdtSerializer(myChat, context={
            'myId': self.theKwargs['profId'], 'new_msg': newMsg, 'prtcpnts': self.jsonPrtcpnts}).data

        return myJsonChat

    @database_sync_to_async
    def get_chat(self):
        chatId = self.chatRoom
        self.theChat = self.myChats.get(id=chatId)
        self.theParticipants = self.theChat.chatParticipants.all()
        self.jsonPrtcpnts = ParticipantsSerializer(
            self.theParticipants, many=True).data
        self.userIds = list(self.theParticipants.values('id'))

    @database_sync_to_async
    def fetch_messages(self, strtMssg, endMssg):
        messages = self.theChat.chatMessages.all()[strtMssg:endMssg]
        myJsonMessages = MessageSerializer(messages, many=True).data

        return myJsonMessages

    @database_sync_to_async
    def create_message(self, data):
        msgData = data['message']
        sender = self.theParticipants.get(id=msgData['author'])
        theNewMessage = ChatMessage.objects.create(
            author=sender,
            forChat=self.theChat,
            messageContent=msgData['messageContent'],
            imageType=msgData['imageType'],
            comLat=msgData['comLat'],
            comLong=msgData['comLong']
        )
        # i should fetch the chat and send the chat here instead
        rlTmeMsgImage(theNewMessage, msgData, 'mssg')
        myJsonMessage = MessageSerializer(theNewMessage).data
        for userId in self.userIds:
            self.theChat.newMessagesFor.add(userId['id'])
        self.theChat.save()
        return myJsonMessage

    @database_sync_to_async
    def create_Chat(self, data):
        chtData = data['chat']
        theNewChat = ChatModel.objects.create(
            chatName=chtData['chatName'],
            isGroup=chtData['isGroup'],
            imageType=chtData['imageType'],
        )
        rlTmeMsgImage(theNewChat, chtData, 'cht')
        for userId in chtData['chatParticipants']:
            theNewChat.chatParticipants.add(userId)
            theNewChat.newMessagesFor.add(userId)
        theNewChat.save()
        myJsonChat = ChatSerializer(theNewChat, context={
            'myId': self.theKwargs['profId']}).data
        return myJsonChat

    @database_sync_to_async
    def update_for_messages(self):
        self.theChat.newMessagesFor.remove(self.theKwargs['profId'])

    async def connect(self):
        self.theKwargs = self.scope['url_route']['kwargs']
        self.personalRoom = 'profChat' + str(self.theKwargs['profId'])
        self.personalGroup = 'myPrsnlChats_%s' % self.personalRoom
        await self.authcteUsr()

        # Join room group
        await self.channel_layer.group_add(
            self.personalGroup,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.personalGroup,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['command'] == 'fetch_my_chats':
            myData = await self.fetch_my_chats()
            await self.channel_layer.group_send(
                self.personalGroup,
                {
                    'type': 'load_chats',
                    'chats': myData
                }
            )
        elif data['command'] == 'create_chat_model':
            chtData = data['chat']
            myData = await self.create_Chat(data)
            for userId in chtData['chatParticipants']:
                prsnleRoom = 'profChat' + str(userId)
                prsnlGroup = 'myPrsnlChats_%s' % prsnleRoom
                await self.channel_layer.group_send(
                    prsnlGroup,
                    {
                        'type': 'new_chat',
                        'newChat': myData
                    }
                )
        elif data['command'] == 'enter_chat_room':
            self.chatRoom = data['chatId']
            self.chatGroup = 'chat_%s' % self.chatRoom
            await self.get_chat()
            await self.channel_layer.group_add(
                self.chatGroup,
                self.channel_name
            )
            strtMssg = 0
            endMssg = 10
            myData = await self.fetch_messages(strtMssg, endMssg)
            await self.channel_layer.group_send(
                self.personalGroup,
                {
                    'type': 'get_messages',
                    'msgs': myData
                }
            )
        elif data['command'] == 'create_message':
            myData = await self.create_message(data)
            chtData = await self.fetch_my_chat(myData)
            for userId in self.userIds:
                prsnleRoom = 'profChat' + str(userId['id'])
                prsnlGroup = 'myPrsnlChats_%s' % prsnleRoom
                await self.channel_layer.group_send(
                    prsnlGroup,
                    {
                        'type': 'update_chats',
                        'chat': chtData
                    }
                )
        elif data['command'] == 'leave_room':
            await self.update_for_messages()
            await self.channel_layer.group_discard(
                self.chatGroup,
                self.channel_name
            )

    # Receive message from room group
    async def new_chat(self, event):
        myData = event['newChat']
        await self.send(text_data=json.dumps({'type': 'new_chat', 'newChats': [myData]}))

    async def update_chats(self, event):
        myData = event['chat']
        await self.send(text_data=json.dumps({'type': 'update_chats', 'chats': [myData]}))

    async def load_chats(self, event):
        myData = event['chats']
        await self.send(text_data=json.dumps({'type': 'fetch_my_chats', 'chats': myData}))

    async def get_messages(self, event):
        myData = event['msgs']
        await self.send(text_data=json.dumps({'type': 'get_messages', 'chtMessages': myData}))

    async def new_message(self, event):
        myData = [event['message']]
        await self.send(text_data=json.dumps({'type': 'new_message', 'chtMessages': myData}))
