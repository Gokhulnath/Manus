"use client";
import { useQuery } from "@/lib/api";
import type { paths } from "@/lib/openapi-types";
import React, { useState, useRef, useEffect } from "react";

type MessageResponse =
    paths["/messages/chat/{chat_id}"]["get"]["responses"]["200"]["content"]["application/json"];

const ChatPage = ({ chat_id = "f6dadbb4-ac52-48e1-973d-f8f6c6b1043b" }: { chat_id?: string }) => {
    const [messages, setMessages] = useState<MessageResponse>([]);
    const chatRef = useRef<HTMLDivElement>(null);

    const { data, isLoading } = useQuery("/messages/chat/{chat_id}", {
        params: {
            path: { chat_id },
        },
    });

    useEffect(() => {
        if (data) {
            setMessages(data as MessageResponse);
        }
    }, [data]);

    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSendMessage = (text: string) => {
        console.log("Sending message:", text);
    };

    return (
        <main className="flex flex-col h-full w-full max-h-screen">
            {/* Chat Area */}
            <div
                ref={chatRef}
                className={`flex-1 overflow-y-auto px-4 w-full max-w-4xl mx-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent ${messages.length === 0 ? "flex items-center justify-center" : "pt-10 pb-6"
                    }`}
            >
                {/* Loading spinner */}
                {isLoading ? (
                    <div className="w-full h-full flex items-center justify-center">
                        <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
                    </div>
                ) : messages.length === 0 ? (
                    <div className="text-center w-full">
                        <h1 className="text-2xl font-semibold mb-4">What can I help with?</h1>
                        <div className="relative max-w-[600px] mx-auto">
                            <input
                                type="text"
                                placeholder="Ask anything"
                                className="bg-white border border-gray-200 px-4 py-3 pr-12 rounded-2xl w-full"
                                onKeyDown={(e) => {
                                    if (e.key === "Enter" && e.currentTarget.value.trim()) {
                                        const value = e.currentTarget.value;
                                        handleSendMessage(value);
                                        e.currentTarget.value = "";
                                    }
                                }}
                                id="chat-input"
                            />
                            <button
                                onClick={() => {
                                    const input = document.getElementById("chat-input") as HTMLInputElement;
                                    if (input?.value.trim()) {
                                        handleSendMessage(input.value);
                                        input.value = "";
                                    }
                                }}
                                className="absolute right-2 top-1/2 -translate-y-1/2 bg-white border border-gray-300 rounded-full w-8 h-8 flex items-center justify-center hover:bg-gray-100 transition"
                                aria-label="Send"
                            >
                                <span className="text-sm">↑</span>
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col gap-4 pb-2">
                        {messages.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`p-4 rounded-xl max-w-[80%] border text-sm ${msg.role === "user"
                                        ? "bg-blue-50 border-blue-200 self-end text-right"
                                        : "bg-gray-100 border-gray-200 self-start text-left"
                                    }`}
                            >
                                {msg.content}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Input at bottom */}
            {!isLoading && messages.length > 0 && (
                <div className="w-full px-4 py-4">
                    <div className="relative max-w-[600px] mx-auto">
                        <input
                            type="text"
                            placeholder="Ask anything"
                            className="bg-white border border-gray-200 px-4 py-3 pr-12 rounded-2xl w-full"
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && e.currentTarget.value.trim()) {
                                    const value = e.currentTarget.value;
                                    handleSendMessage(value);
                                    e.currentTarget.value = "";
                                }
                            }}
                            id="chat-input"
                        />
                        <button
                            onClick={() => {
                                const input = document.getElementById("chat-input") as HTMLInputElement;
                                if (input?.value.trim()) {
                                    handleSendMessage(input.value);
                                    input.value = "";
                                }
                            }}
                            className="absolute right-2 top-1/2 -translate-y-1/2 bg-white border border-gray-300 rounded-full w-8 h-8 flex items-center justify-center hover:bg-gray-100 transition"
                            aria-label="Send"
                        >
                            <span className="text-sm">↑</span>
                        </button>
                    </div>
                </div>
            )}
        </main>
    );
};

export default ChatPage;
