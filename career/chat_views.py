
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction

from .models import ChatConversation, ChatMessage
from .services import generate_career_chat_response


logger = logging.getLogger(__name__)


@login_required
def chat_home(request):

    conversations = ChatConversation.objects.filter(
        user=request.user
    )

    return render(request, 'career/chat.html', {
        'conversations': conversations,
        'active_conversation': None,
        'chat_messages': [],
    })


@login_required
def chat_conversation(request, pk):

    conversation = get_object_or_404(
        ChatConversation,
        pk=pk,
        user=request.user
    )

    conversations = ChatConversation.objects.filter(
        user=request.user
    )

    chat_messages = conversation.messages.all()

    return render(request, 'career/chat.html', {
        'conversations': conversations,
        'active_conversation': conversation,
        'chat_messages': chat_messages,
    })


@login_required
@require_POST
def create_conversation(request):

    conversation = ChatConversation.objects.create(
        user=request.user,
        title='New Career Conversation'
    )

    return redirect(
        'career:chat_conversation',
        pk=conversation.pk
    )


@login_required
@require_POST
def send_chat_message(request, pk):

    is_ajax = (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )

    conversation = get_object_or_404(
        ChatConversation,
        pk=pk,
        user=request.user
    )

    user_message = request.POST.get('message', '').strip()

    # Validate message
    if not user_message:

        error_message = 'Please enter a message.'

        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)

        messages.error(request, error_message)

        return redirect(
            'career:chat_conversation',
            pk=conversation.pk
        )

    if len(user_message) > 5000:

        error_message = 'Message must not exceed 5000 characters.'

        if is_ajax:
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=400)

        messages.error(request, error_message)

        return redirect(
            'career:chat_conversation',
            pk=conversation.pk
        )

    try:

        # Generate Gemini response outside database transaction.
        ai_response = generate_career_chat_response(
            user=request.user,
            message=user_message,
            conversation=conversation
        )

        # Save messages only after successful AI generation.
        with transaction.atomic():

            conversation = ChatConversation.objects.select_for_update().get(
                pk=pk,
                user=request.user
            )

            is_first_message = not conversation.messages.exists()

            user_chat = ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_message
            )

            assistant_chat = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=ai_response
            )

            if is_first_message:
                conversation.title = user_message[:60]

            conversation.save()

        # AJAX response: no page reload
        if is_ajax:

            return JsonResponse({
                'success': True,

                'user_message': {
                    'content': user_chat.content,
                    'time': user_chat.created_at.strftime('%I:%M %p')
                },

                'assistant_message': {
                    'content': assistant_chat.content,
                    'time': assistant_chat.created_at.strftime('%I:%M %p')
                },

                'conversation_title': conversation.title,
            })

        # Normal form submission fallback
        return redirect(
            'career:chat_conversation',
            pk=conversation.pk
        )

    except Exception:

        logger.exception(
            'Career assistant message generation failed.'
        )

        error_message = (
            'Unable to generate an AI response right now. '
            'Please try again.'
        )

        if is_ajax:

            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=500)

        messages.error(request, error_message)

        return redirect(
            'career:chat_conversation',
            pk=conversation.pk
        )


@login_required
@require_POST
def delete_conversation(request, pk):

    conversation = get_object_or_404(
        ChatConversation,
        pk=pk,
        user=request.user
    )

    conversation.delete()

    messages.success(
        request,
        'Conversation deleted successfully.'
    )

    return redirect('career:chat_home')
