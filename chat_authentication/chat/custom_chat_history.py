# chat/custom_chat_history.py

from langchain_core.chat_history import BaseChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from .models import Conversation, ChatMessage


class DjangoChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, conversation_id: int):
        """
        Initialize the DjangoChatMessageHistory with a conversation ID.
        
        Args:
            conversation_id (int): The ID of the conversation to retrieve and store messages.
        """
        self.conversation_id = conversation_id
        self.conversation = Conversation.objects.get(id=conversation_id)

    @property
    def messages(self) -> list[BaseMessage]:
        """
        Retrieve all messages for the conversation from the database.
        
        Returns:
            List[BaseMessage]: A list of chat messages.
        """
        # Fetch all messages related to this conversation from the database
        messages = ChatMessage.objects.filter(conversation=self.conversation).order_by('timestamp')
        chat_history = []

        for message in messages:
            if message.user_response:
                chat_history.append(HumanMessage(content=message.user_response))
            if message.ai_response:
                chat_history.append(AIMessage(content=message.ai_response))

        return chat_history

    def add_message(self, message: BaseMessage) -> None:
        """
        Add a message to the conversation history in the database.
        
        Args:
            message (BaseMessage): A message object, either from the human or the AI.
        """
        if isinstance(message, HumanMessage):
            ChatMessage.objects.create(conversation=self.conversation, user_response=message.content)
        elif isinstance(message, AIMessage):
            ChatMessage.objects.create(conversation=self.conversation, ai_response=message.content)

    def clear(self) -> None:
        """
        Clear all messages from the conversation history in the database.
        """
        ChatMessage.objects.filter(conversation=self.conversation).delete()
