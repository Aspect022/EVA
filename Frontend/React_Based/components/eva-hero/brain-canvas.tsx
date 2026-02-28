"use client";

import { useRef, useEffect, useCallback } from "react";
import type { ModeVariant } from "./hero-config";

interface BrainCanvasProps {
  scrollProgress: number;
  activeMode: ModeVariant;
  className?: string;
}

interface Node {
  x: number;
  y: number;
  baseX: number;
  baseY: number;
  radius: number;
  phase: number;
  speed: number;
  layer: number;
}

function hexToRgb(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return { r, g, b };
}

function createNodes(count: number, w: number, h: number): Node[] {
  const nodes: Node[] = [];
  const cx = w * 0.5;
  const cy = h * 0.5;
  const maxR = Math.min(w, h) * 0.42;

  for (let i = 0; i < count; i++) {
    // Distribute in a brain-like elliptical cluster
    const angle = Math.random() * Math.PI * 2;
    const dist = Math.random() * maxR * (0.3 + Math.random() * 0.7);
    const xStretch = 1.15; // slightly wider than tall
    const x = cx + Math.cos(angle) * dist * xStretch;
    const y = cy + Math.sin(angle) * dist;
    const layer = Math.floor(Math.random() * 3); // 0=deep, 1=mid, 2=surface
    nodes.push({
      x,
      y,
      baseX: x,
      baseY: y,
      radius: 1.5 + Math.random() * 2.5,
      phase: Math.random() * Math.PI * 2,
      speed: 0.3 + Math.random() * 0.7,
      layer,
    });
  }
  return nodes;
}

export function BrainCanvas({
  scrollProgress,
  activeMode,
  className,
}: BrainCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Node[]>([]);
  const animFrameRef = useRef<number>(0);
  const prevModeRef = useRef(activeMode.id);
  const sizeRef = useRef({ w: 0, h: 0 });
  const rippleRef = useRef<{
    active: boolean;
    radius: number;
    maxRadius: number;
  }>({
    active: false,
    radius: 0,
    maxRadius: 0,
  });

  // Regenerate nodes when canvas size changes (fixed count for consistency across modes)
  const regenerateNodes = useCallback((w: number, h: number) => {
    nodesRef.current = createNodes(150, w, h);
    sizeRef.current = { w, h };
  }, []);

  // ResizeObserver for canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resize = () => {
      const parent = canvas.parentElement;
      if (!parent) return;
      const dpr = window.devicePixelRatio || 1;
      const w = parent.clientWidth;
      const h = parent.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      canvas.style.width = `${w}px`;
      canvas.style.height = `${h}px`;
      regenerateNodes(w * dpr, h * dpr);
    };

    const observer = new ResizeObserver(resize);
    if (canvas.parentElement) observer.observe(canvas.parentElement);
    resize();

    return () => observer.disconnect();
  }, [regenerateNodes]);

  const spinMultiplierRef = useRef<number>(1);

  // Speed up spin on mode change (don't regenerate nodes to keep structure identical)
  useEffect(() => {
    if (prevModeRef.current !== activeMode.id) {
      prevModeRef.current = activeMode.id;
      spinMultiplierRef.current = 8; // Temporary speed boost

      // Trigger explosion ripple
      rippleRef.current = {
        active: true,
        radius: 0,
        maxRadius: Math.max(sizeRef.current.w, sizeRef.current.h) * 1.5,
      };
    }
  }, [activeMode.id]);

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let time = 0;
    const { r: ar, g: ag, b: ab } = hexToRgb(activeMode.accent);

    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;

      // Decay the spin multiplier back down to 1 smoothly
      spinMultiplierRef.current =
        spinMultiplierRef.current + (1 - spinMultiplierRef.current) * 0.05;

      time += 0.016 * activeMode.visual.pulseSpeed * spinMultiplierRef.current;

      // Clear
      ctx.clearRect(0, 0, w, h);

      // Central glow
      const cx = w * 0.5;
      const cy = h * 0.5;
      const glowRadius = Math.min(w, h) * 0.45;
      const grd = ctx.createRadialGradient(cx, cy, 0, cx, cy, glowRadius);
      grd.addColorStop(0, activeMode.visual.innerGlow);
      grd.addColorStop(0.5, `rgba(${ar}, ${ag}, ${ab}, 0.04)`);
      grd.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = grd;
      ctx.fillRect(0, 0, w, h);

      const nodes = nodesRef.current;
      const progress = scrollProgress;

      // Ripple expansion logic
      let rippleSpeed = 0;
      if (rippleRef.current.active) {
        rippleRef.current.radius += 20; // 20px per frame outward wave speed
        rippleSpeed = rippleRef.current.radius;

        if (rippleRef.current.radius >= rippleRef.current.maxRadius) {
          rippleRef.current.active = false;
        }
      }

      // Animate node positions
      for (const node of nodes) {
        const drift =
          Math.sin(time * node.speed + node.phase) * (6 + node.layer * 4);
        const driftY =
          Math.cos(time * node.speed * 0.7 + node.phase) * (4 + node.layer * 3);
        // Scroll-based expansion: nodes expand outward as scroll progresses
        const scrollPush = progress * (20 + node.layer * 15);
        const angleFromCenter = Math.atan2(node.baseY - cy, node.baseX - cx);

        // Explode Push: Nodes push outward briefly when the ripple reaches them
        let explodePush = 0;
        if (rippleRef.current.active) {
          const distFromCenter = Math.sqrt(
            Math.pow(node.baseX - cx, 2) + Math.pow(node.baseY - cy, 2),
          );
          const distToRipple = Math.abs(distFromCenter - rippleSpeed);

          // If node is within the ripple wave (e.g. 100px thick), give it a push
          if (distToRipple < 100) {
            explodePush = (100 - distToRipple) * 0.4; // max 40px push
          }
        }

        node.x =
          node.baseX +
          drift +
          Math.cos(angleFromCenter) * (scrollPush + explodePush);
        node.y =
          node.baseY +
          driftY +
          Math.sin(angleFromCenter) * (scrollPush + explodePush);
      }

      // Draw connections
      const maxConnDist =
        Math.min(w, h) * activeMode.visual.connectionDensity * 0.35;
      ctx.lineWidth = 0.5;

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < maxConnDist) {
            const alpha =
              (1 - dist / maxConnDist) *
              0.35 *
              (0.5 + 0.5 * Math.sin(time * 2 + i * 0.1));
            ctx.strokeStyle = `rgba(${ar}, ${ag}, ${ab}, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      for (const node of nodes) {
        const pulse = 0.6 + 0.4 * Math.sin(time * 3 + node.phase);
        const alpha = 0.4 + 0.6 * pulse;
        const r = node.radius * (0.8 + 0.2 * pulse);

        // Glow
        ctx.shadowColor = `rgba(${ar}, ${ag}, ${ab}, ${alpha * 0.5})`;
        ctx.shadowBlur = r * 4;

        ctx.fillStyle = `rgba(${ar}, ${ag}, ${ab}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
        ctx.fill();

        // Core white dot
        ctx.shadowBlur = 0;
        ctx.fillStyle = `rgba(255, 255, 255, ${alpha * 0.7})`;
        ctx.beginPath();
        ctx.arc(node.x, node.y, r * 0.35, 0, Math.PI * 2);
        ctx.fill();
      }

      // Pulse rings from center on scroll
      if (progress > 0.05) {
        const ringCount = 3;
        for (let i = 0; i < ringCount; i++) {
          const ringProgress = (progress * 5 + i * 0.33) % 1;
          const ringR = glowRadius * 0.2 + ringProgress * glowRadius * 0.8;
          const ringAlpha = (1 - ringProgress) * 0.15;
          ctx.strokeStyle = `rgba(${ar}, ${ag}, ${ab}, ${ringAlpha})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.arc(cx, cy, ringR, 0, Math.PI * 2);
          ctx.stroke();
        }
      }

      animFrameRef.current = requestAnimationFrame(draw);
    };

    animFrameRef.current = requestAnimationFrame(draw);
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [scrollProgress, activeMode]);

  return (
    <div className={className}>
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  );
}
