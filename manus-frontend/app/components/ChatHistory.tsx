"use client";
import type { paths } from "@/lib/openapi-types";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPlus, faSpinner } from "@fortawesome/free-solid-svg-icons";
import useSWR from "swr";
import { fetcher, postData } from "@/lib/api";
import { useEffect } from "react";

type Props = {
  chat_id: string;
  onSelectChat: (id: string) => void;
};

type ChatResponse =
  paths["/chats/"]["get"]["responses"]["200"]["content"]["application/json"];

type ChatCreate =
  paths["/chats/"]["post"]["requestBody"]["content"]["application/json"];

const ChatHistory = ({ chat_id, onSelectChat }: Props) => {
  const { data, error, isLoading, mutate } = useSWR("/chats/", fetcher,
    {
      revalidateOnFocus: true,
      revalidateOnReconnect: true,
      refreshInterval: 2000,
      onError: (error) => {
        console.error("Error fetching messages:", error);
      }
    }
  );
  const chats = data as ChatResponse;

  useEffect(() => {
    mutate();
  }, [chat_id, mutate]);

  const handleNewChat = async () => {
    const newChat: ChatCreate = {
      title: "Untitled Chat",
    };

    try {
      const response = await postData("/chats/", newChat);
      onSelectChat(response.id);
      mutate();
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  if (error) return <p>Error: {error.message}</p>;

  return (
    <aside className="w-full h-full bg-white rounded-2xl p-5 border border-gray-200">
      <h1 className="text-center text-xl font-extrabold">Manus Clone</h1>
      <hr className="border-gray-200 mx-2 my-4" />

      <button
        suppressHydrationWarning
        onClick={handleNewChat}
        className="w-full text-left px-4 py-4 rounded-lg hover:bg-gray-100 font-medium text-sm bg-transparent transition-colors flex items-center gap-2"
      >
        <span className="w-4 h-4 flex items-center justify-center">
          <FontAwesomeIcon icon={faPlus} className="text-sm" />
        </span>
        New Chat
      </button>

      <h1 className="w-full text-left px-4 py-3 font-medium text-sm text-gray-500">
        History
      </h1>

      <div className="flex flex-col gap-2">
        {isLoading ? (
          <div className="flex justify-center items-center py-4 text-gray-400">
            <span className="w-6 h-6 flex items-center justify-center">
              <FontAwesomeIcon icon={faSpinner} spin className="mr-2" />
            </span>
            Loading chats...
          </div>
        ) : (
          chats.map((chat) => (
            <button
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className={`w-full text-left px-4 py-2 rounded-lg font-medium text-sm transition-colors ${chat.id === chat_id
                ? "bg-gray-100"
                : "bg-transparent hover:bg-gray-100"
                }`}
            >
              {chat.title || "Untitled Chat"}
            </button>
          ))
        )}
      </div>
    </aside>
  );
};

export default ChatHistory;
