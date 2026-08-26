import { useState } from "react";

interface ProductImageZoomProps {
  imageUrl: string | null;
  zoomUrl?: string | null;
  alt: string;
}

interface MousePosition {
  x: number;
  y: number;
}

export function ProductImageZoom({
  imageUrl,
  zoomUrl,
  alt,
}: ProductImageZoomProps) {
  const [isHovering, setIsHovering] = useState(false);
  const [mousePosition, setMousePosition] = useState<MousePosition>({
    x: 50,
    y: 50,
  });

  if (!imageUrl) {
    return (
      <div className="flex h-52 w-full items-center justify-center bg-[#FFEEDC] px-6 text-center text-sm font-bold text-[#C41D85]">
        Imagen no disponible
      </div>
    );
  }

  const zoomImageUrl = zoomUrl ?? imageUrl;

  return (
    <div
      className="relative h-52 w-full overflow-hidden bg-[#FFEEDC]"
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
      onMouseMove={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 100;
        const y = ((event.clientY - rect.top) / rect.height) * 100;

        setMousePosition({ x, y });
      }}
    >
      <img
        alt={alt}
        className="h-full w-full object-cover transition duration-300 hover:scale-105"
        loading="lazy"
        src={imageUrl}
      />

      {isHovering && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute right-4 top-4 hidden h-28 w-28 rounded-full border-4 border-white bg-white shadow-xl md:block"
          style={{
            backgroundImage: `url(${zoomImageUrl})`,
            backgroundPosition: `${mousePosition.x}% ${mousePosition.y}%`,
            backgroundRepeat: "no-repeat",
            backgroundSize: "260%",
          }}
        />
      )}
    </div>
  );
}
