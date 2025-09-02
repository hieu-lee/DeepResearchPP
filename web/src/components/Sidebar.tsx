import { useMemo } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import {
  Plus,
  PanelLeftClose,
  PanelLeftOpen,
  MessageSquareText,
} from "lucide-react";
import { Trash2 } from "lucide-react";

export type SidebarChat = {
  id: string;
  title: string;
};

type SidebarProps = {
  chats: SidebarChat[];
  activeChatId?: string;
  collapsed?: boolean;
  onCollapseToggle?: () => void;
  onNewChat?: () => void;
  onSelectChat?: (id: string) => void;
  titleOverrides?: Record<string, string>;
  onDeleteChat?: (id: string) => void;
  deletingIds?: Record<string, boolean>;
};

export function Sidebar(props: SidebarProps) {
  const {
    chats,
    activeChatId,
    collapsed = false,
    onCollapseToggle,
    onNewChat,
    onSelectChat,
    titleOverrides = {},
    onDeleteChat,
    deletingIds = {},
  } = props;

  const widthClass = collapsed ? "w-16" : "w-72";

  useMemo(() => {
    // compute whenever active changes (no-op placeholder to emphasize effect)
    chats.find((c) => c.id === activeChatId)?.title;
  }, [activeChatId, chats]);

  return (
    <aside
      className={`h-screen border-r bg-card ${widthClass} flex flex-col transition-[width] duration-300 ease-in-out`}>
      <div className="p-2 flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={onCollapseToggle}
          aria-label="Toggle sidebar"
        >
          {collapsed ? (
            <PanelLeftOpen className="h-5 w-5" />
          ) : (
            <PanelLeftClose className="h-5 w-5" />
          )}
        </Button>
        {!collapsed && (
          <Button
            className="gap-2 flex-1"
            variant="secondary"
            onClick={onNewChat}
          >
            <Plus className="h-4 w-4" /> New chat
          </Button>
        )}
        {collapsed && (
          <Button variant="secondary" size="icon" onClick={onNewChat}>
            <Plus className="h-4 w-4" />
          </Button>
        )}
      </div>
      <Separator />

      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {chats.map((chat) => {
            const isActive = chat.id === activeChatId;
            const displayTitle = titleOverrides[chat.id] ?? chat.title;
            return (
              <div
                key={chat.id}
                className={`group grid grid-cols-[1fr_auto] items-center gap-1 overflow-hidden transition-all duration-300 ease-in-out ${
                  deletingIds[chat.id] ? "opacity-0 -translate-y-1 max-h-0 py-0 my-0" : "opacity-100 max-h-12"
                }`}
              >
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={`w-full text-left ${collapsed ? "px-2" : "px-3"} overflow-hidden`}
                  onClick={() => onSelectChat?.(chat.id)}
                >
                  <div className="flex items-start gap-2 w-full min-w-0">
                    <MessageSquareText className="h-4 w-4 flex-shrink-0 mt-0.5" />
                    {!collapsed && (
                      <span className="block min-w-0 truncate">{displayTitle}</span>
                    )}
                  </div>
                </Button>
                {!collapsed && (
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete chat"
                    className="self-center flex-shrink-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteChat?.(chat.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      </ScrollArea>

      {/* Footer removed for single-user setup */}
    </aside>
  );
}

export default Sidebar;


