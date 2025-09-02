import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Sidebar, type SidebarChat } from "./Sidebar";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";

type MobileSidebarProps = {
  chats: SidebarChat[];
  activeChatId?: string;
  onNewChat?: () => void;
  onSelectChat?: (id: string) => void;
};

export function MobileSidebar({ chats, activeChatId, onNewChat, onSelectChat }: MobileSidebarProps) {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon" className="md:hidden">
          <Menu className="h-5 w-5" />
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="p-0 w-80">
        <Sidebar
          chats={chats}
          activeChatId={activeChatId}
          collapsed={false}
          onNewChat={onNewChat}
          onSelectChat={onSelectChat}
        />
      </SheetContent>
    </Sheet>
  );
}

export default MobileSidebar;


