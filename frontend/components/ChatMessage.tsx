/**
 * components/ChatMessage.tsx
 * --------------------------
 * Renders a single chat message bubble.
 * Supports "user" and "assistant" roles with distinct styling.
 */

import React from "react";

export type MessageRole = "user" | "assistant";

export interface Message {
    id: string;
    role: MessageRole;
    content: string;
    timestamp: Date;
}

interface ChatMessageProps {
    message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
    const isUser = message.role === "user";

    return (
        <div className={`flex w-full mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
            {/* Avatar */}
            {!isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-700 flex items-center justify-center mr-3 mt-1 shadow-md">
                    <span className="text-white text-xs font-bold">AI</span>
                </div>
            )}

            <div className={`max-w-[75%] ${isUser ? "items-end" : "items-start"} flex flex-col`}>
                {/* Bubble */}
                <div
                    className={`rounded-2xl px-4 py-3 shadow-sm text-sm leading-relaxed whitespace-pre-wrap ${isUser
                            ? "bg-gradient-to-br from-violet-600 to-purple-700 text-white rounded-tr-sm"
                            : "bg-white/10 backdrop-blur-sm border border-white/10 text-gray-100 rounded-tl-sm"
                        }`}
                >
                    {message.content}
                </div>

                {/* Timestamp */}
                <span className="text-xs text-gray-500 mt-1 px-1">
                    {message.timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                    })}
                </span>
            </div>

            {/* User Avatar */}
            {isUser && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-sky-400 to-blue-600 flex items-center justify-center ml-3 mt-1 shadow-md">
                    <span className="text-white text-xs font-bold">You</span>
                </div>
            )}
        </div>
    );
}
