from soci3LApp.models import ChatModel, UserInfo
from chatSoci.serializers import ChatSerializer, ProfileChatSerializer
from rest_framework.views import APIView
from soci_3_api.myHttpFunctions import myDefGetiIndividual, myPost

# Create your views here.


class CreateChat(APIView):
    serializer_class = ChatSerializer

    def post(self, request, *args, **kwargs):
        return myPost(request, ChatModel, ChatSerializer)


class RetreiveChatsOfProfile(APIView):
    serializer_class = ProfileChatSerializer

    def get(self, request, *args, **kwargs):
        return myDefGetiIndividual(ProfileChatSerializer, UserInfo, kwargs['pk'])
