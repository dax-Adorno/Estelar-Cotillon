import { useEffect, useState } from "react";

interface CursorPosition {
  x: number;
  y: number;
}

export function BrandCursor() {
  const [position, setPosition] = useState<CursorPosition>({
    x: -100,
    y: -100,
  });

  useEffect(() => {
    function handleMouseMove(event: MouseEvent): void {
      setPosition({
        x: event.clientX,
        y: event.clientY,
      });
    }

    window.addEventListener("mousemove", handleMouseMove);
    document.body.classList.add("estelart-custom-cursor");

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      document.body.classList.remove("estelart-custom-cursor");
    };
  }, []);

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed z-9999 hidden h-8 w-8 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-[#C41D85] bg-[#FFBA1F]/20 mix-blend-multiply transition-transform duration-75 md:block"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    />
  );
}
