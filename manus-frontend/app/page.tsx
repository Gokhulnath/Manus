import ChatHistory from "./components/ChatHistory";

export default function Home() {
  return (
    <div className="h-screen w-screen grid grid-cols-[15vw_1fr_auto] grid-rows-1 items-stretch p-2 gap-2 font-[family-name:var(--font-geist-sans)] ">
      <ChatHistory />

      {/* Column 2 (flex-grow) */}
      <main className="flex flex-col gap-[32px] col-start-2 items-center sm:items-start h-full p-5">
        hello world
      </main>

      {/* Column 3 (optional, fixed 200px) */}
      <div className="min-w-[33vw] hidden lg:block h-full bg-white rounded-2xl p-5 border border-gray-200">
        Optional right panel
      </div>
    </div>
  );
}
