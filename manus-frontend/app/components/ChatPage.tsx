"use client";
import { fetcher, postData } from "@/lib/api";
import type { paths } from "@/lib/openapi-types";
import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import useSWR from "swr";

type Props = {
    chat_id: string;
    onAnalyseMessage?: (message: MessageResponse[number]) => Promise<void>;
};

type MessageResponse =
    paths["/messages/chat/{chat_id}"]["get"]["responses"]["200"]["content"]["application/json"];

type MessageCreate = paths["/messages/"]["post"]["requestBody"]["content"]["application/json"];

const ChatPage = ({ chat_id, onAnalyseMessage }: Props) => {
    const [messages, setMessages] = useState<MessageResponse>([]);
    const chatRef = useRef<HTMLDivElement>(null);
    const [isProcessing, setIsProcessing] = useState(false);

    const { data, isLoading, mutate } = useSWR(`/messages/chat/${chat_id}`, fetcher);

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

    const handleSendMessage = async (text: string) => {
        const newMessage: MessageCreate = {
            chat_id,
            content: text,
            role: "user",
            task: "chat",
            status: "pending",
        };

        try {
            setIsProcessing(true);

            // Send the user's message
            const response = await postData("/messages/", newMessage);
            setMessages((prev) => [...prev, response]);

            const waitForMessages = async () => {
                const res = await fetcher(`/messages/chat/${chat_id}`) as MessageResponse;

                // Find the last user message index
                const lastUserIndex = res
                    .map((m) => m.role)
                    .lastIndexOf("user");

                // Only messages after the last user message are relevant
                const newAssistantMessages = res.slice(lastUserIndex + 1);

                const analyseMessages = newAssistantMessages.filter(
                    (msg) => msg.task === "analyse" && msg.status === "completed"
                );

                const summarizeMessage = newAssistantMessages.find(
                    (msg) => msg.task === "summarize" && msg.status === "completed"
                );

                // Process analyse messages one-by-one
                for (const msg of analyseMessages) {
                    setMessages((prev) => [...prev, msg]);
                    if (onAnalyseMessage) {
                        await onAnalyseMessage(msg);
                    }
                }

                // Process summarize message only after all analyse messages
                if (summarizeMessage) {
                    setMessages((prev) => [...prev, summarizeMessage]);
                    setIsProcessing(false);
                    mutate();
                } else {
                    // Retry after short delay
                    setTimeout(waitForMessages, 500);
                }
            };
            waitForMessages();
        } catch (error) {
            console.error("Error sending message:", error);
            setIsProcessing(false);
        }
    };



    const renderMessages = () => {
        return messages.map((msg, idx) => {
            const isAssistant = msg.role === "assistant";
            const isAnalyseCompleted = msg.task === "analyse" && msg.status === "completed";

            let contentToRender;

            if (isAssistant && isAnalyseCompleted) {
                let docName = '';
                try {
                    const parsed = typeof msg.content === 'string'
                        ? JSON.parse(msg.content.replace(/'/g, '"'))
                        : msg.content;
                    docName = parsed?.document_name || "document";
                } catch (e) {
                    console.error("Error", e);
                    docName = "document";
                }

                contentToRender = (
                    <div
                        className="italic text-gray-700 rounded flex items-center gap-2 cursor-pointer transition-colors"
                        onClick={() => {
                            if (onAnalyseMessage) {
                                onAnalyseMessage(msg);
                            }
                        }}
                    >
                        <span>Analysed <strong>{docName}</strong></span>
                        <span className="text-gray-700 text-sm">➔</span>
                    </div>
                );
            } else {
                contentToRender = isAssistant
                    ? <ReactMarkdown>{msg.content}</ReactMarkdown>
                    : msg.content;
            }

            return (
                <div
                    key={idx}
                    className={`p-4 rounded-xl max-w-[80%] border text-sm text-left ${isAssistant
                        ? "bg-gray-100 border-gray-200 self-start"
                        : "bg-blue-50 border-blue-200 self-end"
                        }`}
                >
                    {contentToRender}
                </div>
            );
        });
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
                                disabled={isProcessing}
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
                                disabled={isProcessing}
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
                        {renderMessages()}
                    </div>
                )}
            </div>

            {/* Input at bottom */}
            {!isLoading && messages.length > 0 && (
                <div className="w-full px-4 py-4">
                    <div className="relative max-w-[600px] mx-auto">
                        <input
                            disabled={isProcessing}
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
                            disabled={isProcessing}
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
