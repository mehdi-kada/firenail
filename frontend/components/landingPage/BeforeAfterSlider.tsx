"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import Image from "next/image";
import { GripVertical } from "lucide-react";

interface BeforeAfterSliderProps {
    beforeImage: string;
    afterImage: string;
    beforeAlt?: string;
    afterAlt?: string;
}

export default function BeforeAfterSlider({
    beforeImage,
    afterImage,
    beforeAlt = "Before",
    afterAlt = "After",
}: BeforeAfterSliderProps) {
    const [sliderPosition, setSliderPosition] = useState(50);
    const [isResizing, setIsResizing] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const handleMouseDown = useCallback(() => {
        setIsResizing(true);
    }, []);

    const handleMouseUp = useCallback(() => {
        setIsResizing(false);
    }, []);

    const handleMouseMove = useCallback(
        (e: MouseEvent) => {
            if (!isResizing || !containerRef.current) return;

            const rect = containerRef.current.getBoundingClientRect();
            const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
            const percentage = (x / rect.width) * 100;

            setSliderPosition(percentage);
        },
        [isResizing]
    );

    const handleTouchMove = useCallback(
        (e: TouchEvent) => {
            if (!isResizing || !containerRef.current) return;

            const rect = containerRef.current.getBoundingClientRect();
            const touch = e.touches[0];
            const x = Math.max(0, Math.min(touch.clientX - rect.left, rect.width));
            const percentage = (x / rect.width) * 100;

            setSliderPosition(percentage);
        },
        [isResizing]
    );

    useEffect(() => {
        document.addEventListener("mousemove", handleMouseMove);
        document.addEventListener("mouseup", handleMouseUp);
        document.addEventListener("touchmove", handleTouchMove);
        document.addEventListener("touchend", handleMouseUp);

        return () => {
            document.removeEventListener("mousemove", handleMouseMove);
            document.removeEventListener("mouseup", handleMouseUp);
            document.removeEventListener("touchmove", handleTouchMove);
            document.removeEventListener("touchend", handleMouseUp);
        };
    }, [handleMouseMove, handleMouseUp, handleTouchMove]);

    return (
        <div
            ref={containerRef}
            className="relative w-full aspect-video rounded-xl overflow-hidden select-none cursor-ew-resize border border-white/10 shadow-2xl bg-black"
        >
            {/* After Image (Background) */}
            <Image
                src={afterImage}
                alt={afterAlt}
                fill
                className="object-cover"
                priority
            />

            <div className="absolute top-4 right-4 bg-black/60 backdrop-blur-md text-white text-xs font-bold px-3 py-1 rounded-full border border-white/10 z-10 pointer-events-none">
                AFTER
            </div>

            {/* Before Image (Foreground - Clipped) */}
            <div
                className="absolute inset-0 overflow-hidden"
                style={{ width: `${sliderPosition}%` }}
            >
                <Image
                    src={beforeImage}
                    alt={beforeAlt}
                    fill
                    className="object-cover object-left"
                    priority
                />
                <div className="absolute top-4 left-4 bg-black/60 backdrop-blur-md text-white text-xs font-bold px-3 py-1 rounded-full border border-white/10 z-10 pointer-events-none">
                    BEFORE
                </div>
            </div>

            {/* Slider Handle */}
            <div
                className="absolute top-0 bottom-0 w-1 bg-white cursor-ew-resize z-20"
                style={{ left: `${sliderPosition}%` }}
                onMouseDown={handleMouseDown}
                onTouchStart={handleMouseDown}
            >
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                    <GripVertical className="w-4 h-4 text-black" />
                </div>
            </div>
        </div>
    );
}
