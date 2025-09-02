/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_send_message_api_chats__chat_id__messages_post } from '../models/Body_send_message_api_chats__chat_id__messages_post';
import type { Chat } from '../models/Chat';
import type { CreateChatResponse } from '../models/CreateChatResponse';
import type { ListChatsResponse } from '../models/ListChatsResponse';
import type { Message } from '../models/Message';
import type { SendMessageResponse } from '../models/SendMessageResponse';
import type { UpdateTitleRequest } from '../models/UpdateTitleRequest';
import type { UpdateTitleResponse } from '../models/UpdateTitleResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ChatsService {
    /**
     * List Chats
     * @returns ListChatsResponse Successful Response
     * @throws ApiError
     */
    public static listChatsApiChatsGet({
        xDeviceId,
    }: {
        xDeviceId?: (string | null),
    }): CancelablePromise<ListChatsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/chats',
            headers: {
                'x-device-id': xDeviceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Chat
     * @returns CreateChatResponse Successful Response
     * @throws ApiError
     */
    public static createChatApiChatsPost({
        xDeviceId,
    }: {
        xDeviceId?: (string | null),
    }): CancelablePromise<CreateChatResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/chats',
            headers: {
                'x-device-id': xDeviceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Chat
     * @returns Chat Successful Response
     * @throws ApiError
     */
    public static getChatApiChatsChatIdGet({
        chatId,
        xDeviceId,
    }: {
        chatId: string,
        xDeviceId?: (string | null),
    }): CancelablePromise<Chat> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/chats/{chat_id}',
            path: {
                'chat_id': chatId,
            },
            headers: {
                'x-device-id': xDeviceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Chat
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteChatApiChatsChatIdDelete({
        chatId,
        xDeviceId,
    }: {
        chatId: string,
        xDeviceId?: (string | null),
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/chats/{chat_id}',
            path: {
                'chat_id': chatId,
            },
            headers: {
                'x-device-id': xDeviceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Set Title
     * @returns UpdateTitleResponse Successful Response
     * @throws ApiError
     */
    public static setTitleApiChatsChatIdTitlePost({
        chatId,
        requestBody,
        xDeviceId,
    }: {
        chatId: string,
        requestBody: UpdateTitleRequest,
        xDeviceId?: (string | null),
    }): CancelablePromise<UpdateTitleResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/chats/{chat_id}/title',
            path: {
                'chat_id': chatId,
            },
            headers: {
                'x-device-id': xDeviceId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Messages
     * @returns Message Successful Response
     * @throws ApiError
     */
    public static getMessagesApiChatsChatIdMessagesGet({
        chatId,
        xDeviceId,
    }: {
        chatId: string,
        xDeviceId?: (string | null),
    }): CancelablePromise<Array<Message>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/chats/{chat_id}/messages',
            path: {
                'chat_id': chatId,
            },
            headers: {
                'x-device-id': xDeviceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Send Message
     * @returns SendMessageResponse Successful Response
     * @throws ApiError
     */
    public static sendMessageApiChatsChatIdMessagesPost({
        chatId,
        xDeviceId,
        formData,
    }: {
        chatId: string,
        xDeviceId?: (string | null),
        formData?: Body_send_message_api_chats__chat_id__messages_post,
    }): CancelablePromise<SendMessageResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/chats/{chat_id}/messages',
            path: {
                'chat_id': chatId,
            },
            headers: {
                'x-device-id': xDeviceId,
            },
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
