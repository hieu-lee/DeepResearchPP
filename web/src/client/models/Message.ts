/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Attachment } from './Attachment';
export type Message = {
    id: string;
    role: Message.role;
    content?: string;
    attachments?: Array<Attachment>;
};
export namespace Message {
    export enum role {
        SYSTEM = 'system',
        USER = 'user',
        ASSISTANT = 'assistant',
    }
}

