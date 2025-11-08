import { useEffect } from "react";
import { useLocation } from "wouter";

export function useKeyboardShortcuts() {
  const [, setLocation] = useLocation();

  useEffect(() => {
    let secondKeyHandler: ((event: KeyboardEvent) => void) | null = null;
    let timeoutId: NodeJS.Timeout | null = null;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "g" && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const activeEl = document.activeElement;
        if (activeEl?.tagName === "INPUT" || activeEl?.tagName === "TEXTAREA") {
          return;
        }

        secondKeyHandler = (event: KeyboardEvent) => {
          event.preventDefault();
          const key = event.key;
          
          switch (key) {
            case "d":
              setLocation("/");
              break;
            case "i":
              setLocation("/ingest");
              break;
            case "l":
              setLocation("/learn");
              break;
            case "p":
              setLocation("/practice");
              break;
            case "m":
              setLocation("/mock");
              break;
            case "c":
              setLocation("/placement");
              break;
            case "f":
              setLocation("/flashcards");
              break;
          }
          
          if (secondKeyHandler) {
            document.removeEventListener("keydown", secondKeyHandler);
            secondKeyHandler = null;
          }
          if (timeoutId) {
            clearTimeout(timeoutId);
            timeoutId = null;
          }
        };

        document.addEventListener("keydown", secondKeyHandler);
        
        timeoutId = setTimeout(() => {
          if (secondKeyHandler) {
            document.removeEventListener("keydown", secondKeyHandler);
            secondKeyHandler = null;
          }
          timeoutId = null;
        }, 1000);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      if (secondKeyHandler) {
        document.removeEventListener("keydown", secondKeyHandler);
      }
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [setLocation]);
}
