from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.core.exceptions import ObjectDoesNotExist
from .models import ChatMessage, Conversation
from .serializers import ChatMessageSerializer, ConversationSerializer
from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, streaming=True)
memory = ConversationBufferMemory()

# Load the tokenizer and model for title generation
tokenizer = AutoTokenizer.from_pretrained("czearing/article-title-generator")
model = AutoModelForSeq2SeqLM.from_pretrained("czearing/article-title-generator")

def generate_title(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=64, num_beams=5, early_stopping=True)
    generated_title = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_title

def retrieve_conversation(title, user):
    num_recent_conversations = 4
    try:
        conversation_obj = Conversation.objects.get(title=title, user=user)
        conversation_id = conversation_obj.id
        print(f"Retrieved conversation ID: {conversation_id}")

        conversation_context = ChatMessage.objects.filter(
            conversation_id=conversation_id
        ).order_by('-timestamp')[:num_recent_conversations]

        print(f"Retrieved conversation context: {conversation_context}")

        lst = []
        for msg in conversation_context:
            input_msg = msg.user_response
            output_msg = msg.ai_response
            lst.append({"input": input_msg, "output": output_msg})
    
        for x in lst:
            inputs = {"input": x["input"]}
            outputs = {"output": x["output"]}
            memory.save_context(inputs, outputs)
    
        retrieved_chat_history = ChatMessageHistory(
            messages=memory.chat_memory.messages
        )
        print(f"Retrieved chat history: {retrieved_chat_history}")

        return retrieved_chat_history
    except ObjectDoesNotExist:
        print("No conversation found for the given title and user.")
        return None


def store_message(user_response, ai_response, conversation_id):
    ChatMessage.objects.create(
        user_response=user_response,
        ai_response=ai_response,
        conversation_id=conversation_id,
    )

def store_title(title, user):
    Conversation.objects.create(
        title=title,
        user=user
    )

@api_view(['POST', 'GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat(request):
    try:
        if request.method == 'GET':
            provided_title = request.GET.get('title')
            user = request.user
            print(f"Received GET request for title: {provided_title} by user: {user}")
            
            if provided_title:
                try:
                    conversation_title = Conversation.objects.get(title=provided_title, user=user)
                    conversation_id = conversation_title.id
                    print(f"Found conversation ID: {conversation_id}")
                    
                    ChatObj = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('timestamp')
                    Chat = ChatMessageSerializer(ChatObj, many=True)
                    print(f"Fetched chat messages: {Chat.data}")
                    
                    return JsonResponse(Chat.data, safe=False)
                except Conversation.DoesNotExist:
                    print("Conversation does not exist.")
                    return JsonResponse({'error': 'Conversation not found'}, status=404)
            else:
                print("Title not provided in GET request.")
                return JsonResponse({'error': 'Title not provided'}, status=400)

        elif request.method == 'POST':
            prompt = request.data.get('prompt')
            user = request.user
            provided_title = request.data.get('title')

            if provided_title:
                # Continue an existing conversation
                print(f"Continuing conversation with title: {provided_title}")
                retrieved_chat_history = retrieve_conversation(provided_title, user)
                title = provided_title
            else:
                # Create a new conversation
                print("Creating a new conversation")
                memory.clear()
                retrieved_chat_history = ChatMessageHistory(messages=[])
                title = generate_title(prompt)
                store_title(title, user)

            reloaded_chain = ConversationChain(
                llm=llm,
                memory=ConversationBufferMemory(chat_memory=retrieved_chat_history),
                verbose=True
            )

            response = reloaded_chain.predict(input=prompt)

            conversation_title = Conversation.objects.get(title=title, user=user)
            conversation_id = conversation_title.id
            store_message(prompt, response, conversation_id)

            # Fetch updated messages after storing the new response
            chat_messages = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('timestamp')
            serialized_messages = ChatMessageSerializer(chat_messages, many=True)

            # Return AI response and updated chat messages
            return JsonResponse({'ai_response': response, 'messages': serialized_messages.data, 'title': title}, status=201)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return JsonResponse({'error': 'An error occurred'}, status=500)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_title(request):
    try:
        user = request.user
        titles = Conversation.objects.filter(user=user)
        serialized = ConversationSerializer(titles, many=True)
        return JsonResponse(serialized.data, safe=False)
    except Exception as e:
        print(f"Error in get_title: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def delete_conversation(request):
    try:
        user = request.user
        title = request.data.get('title')
        obj = Conversation.objects.get(user=user, title=title)
        obj.delete()
        return JsonResponse({"message": "Deleted successfully"}, safe=False)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred'}, status=500)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_data(request):
    try:
        provided_title = request.GET.get('title')
        user = request.user
        if provided_title:
            try:
                conversation_title = Conversation.objects.get(title=provided_title, user=user)
                conversation_id = conversation_title.id
                ChatObj = ChatMessage.objects.filter(conversation_id=conversation_id).order_by('timestamp')
                Chat = ChatMessageSerializer(ChatObj, many=True)
                return JsonResponse(Chat.data, safe=False)
            except Conversation.DoesNotExist:
                return JsonResponse({'error': 'Conversation not found'}, status=404)
        else:
            return JsonResponse({'error': 'Title not provided'}, status=400)
    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
