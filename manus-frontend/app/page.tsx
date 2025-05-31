"use client";
import { useQuery } from "@/lib/api";
import type { paths } from "@/lib/openapi-types";

type ChatResponse =
  paths["/chats/"]["get"]["responses"]["200"]["content"]["application/json"];

export default function Home() {
  const { data, error, isLoading } = useQuery("/chats/");
  const chats = data as ChatResponse;

  if (isLoading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        {chats?.map((item) => (
          <li key={item.id}>{item.title}</li>
        ))}
      </main>
    </div>
  );
}
