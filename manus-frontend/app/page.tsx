"use client";
import { useEffect, useState } from "react";
import ChatHistory from "./components/ChatHistory";
import ChatPage from "./components/ChatPage";
import { postData } from "@/lib/api";
import { paths } from "@/lib/openapi-types";
import DocViewer from "./components/DocViewer";

type ChatCreate =
  paths["/chats/"]["post"]["requestBody"]["content"]["application/json"];
type MessageResponse =
  paths["/messages/chat/{chat_id}"]["get"]["responses"]["200"]["content"]["application/json"];

export default function Home() {
  const [selectedChatId, setSelectedChatId] = useState<string>("");
  const [doc, setDoc] = useState<MessageResponse[number] | undefined>(undefined);

  useEffect(() => {
    const initChat = async () => {
      const storedId = localStorage.getItem("selectedChatId");
      if (storedId) {
        setSelectedChatId(storedId);
      } else {
        try {
          const newChat: ChatCreate = {
            title: "Untitled Chat",
          };
          const response = await postData("/chats/", newChat);
          setSelectedChatId(response.id);
          localStorage.setItem("selectedChatId", response.id);
        } catch (err) {
          console.error("Failed to create initial chat:", err);
        }
      }
    };
    initChat();
  }, []);

  useEffect(() => {
    if (selectedChatId) {
      localStorage.setItem("selectedChatId", selectedChatId);
      setDoc(undefined); // Reset doc when changing chat
    }
  }, [selectedChatId]);

  const handleAnalyseMessage = async (message: MessageResponse[number]) => {
    setDoc(message);
    await new Promise((res) => setTimeout(res, 5000));
  };

  return (
    <div className="h-screen w-screen grid grid-cols-[15vw_1fr_auto] grid-rows-1 items-stretch p-2 gap-2 font-[family-name:var(--font-geist-sans)] ">
      <ChatHistory onSelectChat={(id) => {
        setSelectedChatId(id);
        localStorage.setItem("selectedChatId", id);
      }} chat_id={selectedChatId} />
      <ChatPage chat_id={selectedChatId} onAnalyseMessage={handleAnalyseMessage} />
      <DocViewer doc={doc} onClose={() => setDoc(undefined)} />
    </div>
  );
}
