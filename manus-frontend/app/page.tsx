import ChatHistory from "./components/ChatHistory";
import ChatPage from "./components/ChatPage";

export default function Home() {
  return (
    <div className="h-screen w-screen grid grid-cols-[15vw_1fr_auto] grid-rows-1 items-stretch p-2 gap-2 font-[family-name:var(--font-geist-sans)] ">
      <ChatHistory />
      <ChatPage />

      {/* Column 3 (optional, fixed 200px) */}
      <div className="min-w-[33vw] hidden lg:block h-full bg-white rounded-2xl p-5 border border-gray-200">
        Manus Doc Viewer
      </div>
    </div>
  );
}
