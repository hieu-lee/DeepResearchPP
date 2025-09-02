import { useEffect, useRef, useState } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ArrowUp, Image, StopCircle, X } from "lucide-react";

type ChatComposerProps = {
  value: string;
  isGenerating?: boolean;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onStop?: () => void;
  onAttach?: (files: FileList) => void;
  hasAttachments?: boolean;
  attachedFiles?: File[];
  onRemoveAttachment?: (index: number) => void;
};

export function ChatComposer({ value, onChange, onSubmit, isGenerating, onStop, onAttach, hasAttachments = false, attachedFiles = [], onRemoveAttachment }: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [previews, setPreviews] = useState<string[]>([]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "0px";
    const next = Math.min(textarea.scrollHeight, 200);
    textarea.style.height = `${next}px`;
  }, [value]);

  useEffect(() => {
    if (!attachedFiles || attachedFiles.length === 0) {
      setPreviews([]);
      return;
    }
    const urls = attachedFiles.map((f) => URL.createObjectURL(f));
    setPreviews(urls);
    return () => {
      urls.forEach((u) => URL.revokeObjectURL(u));
    };
  }, [attachedFiles]);

  const submit = () => {
    if (isGenerating) return;
    if (!value.trim() && !hasAttachments) return;
    onSubmit();
  };

  return (
    <div className="mt-4 mx-auto w-full max-w-3xl px-4 pb-6">
      <div className="rounded-xl border bg-card p-2 shadow-sm">
        {previews.length > 0 && (
          <div className="flex flex-wrap gap-2 p-2">
            {previews.map((src, i) => (
              <div key={i} className="relative">
                <img
                  src={src}
                  alt="attachment preview"
                  className="h-20 w-20 object-cover rounded-lg border"
                />
                <div className="absolute top-1 right-1 flex gap-1">
                  <button
                    type="button"
                    aria-label="Remove image"
                    onClick={() => onRemoveAttachment?.(i)}
                    className="h-6 w-6 inline-flex items-center justify-center rounded-full bg-background/80 text-foreground shadow border hover:bg-background"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                </div>
                {/* removed paperclip overlay icon */}
              </div>
            ))}
          </div>
        )}
        <div className="flex items-end gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => {
              const files = e.target.files;
              if (files && files.length > 0) {
                onAttach?.(files);
              }
              // reset so selecting the same file again still triggers change
              if (fileInputRef.current) fileInputRef.current.value = "";
            }}
          />
          <TooltipProvider delayDuration={0}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Attach photo"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Image className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Attach photo</TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <Textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Message ChatGPT"
            className="min-h-[44px] max-h-[200px] resize-none flex-1 border-0 focus-visible:ring-0 pl-3 pr-0"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
          />

          {!isGenerating ? (
            <TooltipProvider delayDuration={0}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    size="icon"
                    className="rounded-lg"
                    aria-label="Send"
                    onClick={submit}
                  >
                    <ArrowUp className="h-5 w-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Send</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          ) : (
            <TooltipProvider delayDuration={0}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="secondary"
                    size="icon"
                    className="rounded-lg"
                    aria-label="Stop"
                    onClick={onStop}
                  >
                    <StopCircle className="h-5 w-5" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>Stop generating</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}

        </div>
      </div>
    </div>
  );
}

export default ChatComposer;


