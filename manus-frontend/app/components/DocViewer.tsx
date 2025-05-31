import { paths } from '@/lib/openapi-types';
import mammoth from 'mammoth';
import { parse } from 'path';
import React, { useEffect, useRef, useState } from 'react'

type MessageResponse =
    paths["/messages/chat/{chat_id}"]["get"]["responses"]["200"]["content"]["application/json"];

type Props = {
    doc: MessageResponse[number] | undefined;
    onClose: () => void;
};

const ParseData = (doc) => {
    let parsed: any;
    try {
        if (typeof doc?.content === "string") {
            let raw = doc.content;

            // Escape lone backslashes
            raw = raw.replace(/\\/g, '\\\\');

            // Replace single-quoted keys with double-quoted keys
            raw = raw.replace(/([{,]\s*)'([^']+?)'\s*:/g, '$1"$2":');

            // Replace single-quoted string values with double-quoted ones
            raw = raw.replace(/:\s*'([^']*?)'(?=[,}])/g, ': "$1"');

            parsed = JSON.parse(raw);
        } else {
            parsed = doc?.content;
        }
    } catch (e) {
        console.error("Failed to parse doc.content:", e);
        parsed = {}; // or a safe fallback
    }
    return parsed;
}

const DocViewer = ({ doc, onClose }: Props) => {
    const [docText, setDocText] = useState<string | null>(null);
    const [renderKey, setRenderKey] = useState<number>(0);
    const highlightRef = useRef<HTMLSpanElement>(null);
    const [documentName, setDocumentName] = useState<string | null>(null);

    useEffect(() => {
        const parsed = ParseData(doc);

        setDocumentName(parsed?.document_name || null);
        const filepath = '/data-room/' + parsed?.document_name;

        const loadDocx = async () => {
            try {
                const res = await fetch(filepath);
                const blob = await res.blob();
                const arrayBuffer = await blob.arrayBuffer();
                const { value } = await mammoth.extractRawText({ arrayBuffer });
                setDocText(value);

                // Trigger a remount of scroll content
                setTimeout(() => setRenderKey(prev => prev + 1), 0);
            } catch (error) {
                console.error("Failed to load .docx:", error);
            }
        };

        if (parsed?.document_type === "docx") {
            loadDocx();
        }
    }, [doc]);

    useEffect(() => {
        if (docText && highlightRef.current) {
            setTimeout(() => {
                highlightRef.current?.scrollIntoView({
                    behavior: "smooth",
                    block: "center",
                });
            }, 100);
        }
    }, [renderKey]);

    const parsed = ParseData(doc);


    const start = parsed?.start_char_index ?? 0;
    const end = parsed?.end_char_index ?? 0;

    let pre = "", highlight = "", post = "";
    if (docText) {
        pre = docText.slice(0, start);
        highlight = docText.slice(start, end);
        post = docText.slice(end);
    }

    return (
        <div
            className={`relative max-w-[33vw] h-full bg-white rounded-2xl p-5 border border-gray-200 ${doc?.chunk_id ? "lg:block" : "hidden"}`}
        >
            <button
                suppressHydrationWarning
                onClick={onClose}
                className="absolute top-3 right-5 text-gray-500 hover:text-gray-700 text-2xl"
                aria-label="Close Doc Viewer"
            >
                ×
            </button>

            <h2 className="text-lg font-semibold mb-4">Doc Viewer</h2>
            {documentName && (
                <div className="text-sm text-gray-600 mb-2">
                    Document: <b>{documentName}</b>
                </div>
            )}

            {docText ? (
                <div
                    key={renderKey}
                    className="text-sm text-gray-800 whitespace-pre-wrap overflow-y-auto max-h-[calc(100%-5rem)] pr-2"
                >
                    {pre}
                    <span ref={highlightRef} className="bg-yellow-300 font-semibold">
                        {highlight}
                    </span>
                    {post}
                </div>
            ) : (
                <p>Loading document...</p>
            )}
        </div>
    );
};

export default DocViewer;