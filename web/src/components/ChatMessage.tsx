import { useEffect, useState } from "react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import type { Attachment } from "@/client/models/Attachment";
import { X } from "lucide-react";

export type Message = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  attachments?: Attachment[];
};

type ChatMessageProps = {
  message: Message;
  pending?: boolean;
};

export function ChatMessage({ message, pending = false }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [mounted, setMounted] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);
  const [activeImage, setActiveImage] = useState<Attachment | null>(null);
  useEffect(() => {
    const id = requestAnimationFrame(() => setMounted(true));
    return () => cancelAnimationFrame(id);
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setViewerOpen(false);
    };
    if (viewerOpen) {
      document.addEventListener("keydown", onKey);
    }
    return () => document.removeEventListener("keydown", onKey);
  }, [viewerOpen]);
  return (
    <div className={cn("w-full", isUser ? "" : "bg-muted/30")}> 
      <div
        className={cn(
          "mx-auto max-w-3xl px-4 py-6 flex gap-4 transition-all duration-300 ease-out",
          mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
        )}
      > 
        <Avatar className="h-7 w-7">
          <AvatarFallback>{isUser ? "U" : "G"}</AvatarFallback>
        </Avatar>
        <div className="flex-1">
          {(message.content && (window as any)?.marked) ? (
            <div
              className={cn(
                "prose max-w-none text-sm dark:prose-invert",
                pending && "text-muted-foreground animate-pulse"
              )}
              dangerouslySetInnerHTML={{ __html: (window as any).marked.parse(message.content) }}
            />
          ) : (
            <div
              className={cn(
                "prose max-w-none text-sm dark:prose-invert whitespace-pre-wrap",
                pending && "text-muted-foreground animate-pulse"
              )}
            >
              {message.content}
            </div>
          )}
          {!!message.attachments?.length && (
            <div className="mt-3 flex flex-wrap gap-2">
              {message.attachments.map((att) => (
                <button
                  key={att.id}
                  type="button"
                  className="group relative"
                  onClick={() => {
                    setActiveImage(att);
                    setViewerOpen(true);
                  }}
                >
                  <img
                    src={(att as any).data_url || (typeof window !== 'undefined' ? (att as any)._local_preview_url : '')}
                    alt={att.filename}
                    className="h-40 w-40 object-cover rounded-md border transition-transform group-hover:scale-[1.02]"
                  />
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {viewerOpen && activeImage && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center" onClick={() => setViewerOpen(false)}>
          <button
            type="button"
            aria-label="Close"
            className="absolute top-4 right-4 h-9 w-9 inline-flex items-center justify-center rounded-full bg-background text-foreground shadow"
            onClick={(e) => {
              e.stopPropagation();
              setViewerOpen(false);
            }}
          >
            <X className="h-5 w-5" />
          </button>
          <img
            src={activeImage.data_url}
            alt={activeImage.filename}
            className="max-h-[90vh] max-w-[90vw] object-contain rounded-lg"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}

export default ChatMessage;


