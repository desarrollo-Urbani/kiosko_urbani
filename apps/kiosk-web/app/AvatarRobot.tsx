import React, { useState, useEffect, useRef } from 'react';
import {
  motion,
  useMotionValue,
  useTransform,
  AnimatePresence,
  type TargetAndTransition,
  type Transition,
} from 'framer-motion';

export type AvatarState = 'idle' | 'active' | 'thinking' | 'success';

export interface AvatarRobotProps {
  state?: AvatarState;
  message?: string;
  onMessageComplete?: () => void;
  size?: number;
}

// --- Speech Bubble ---
function SpeechBubble({
  text,
  visible,
  onComplete,
}: {
  text: string;
  visible: boolean;
  onComplete?: () => void;
}) {
  const [displayed, setDisplayed] = useState('');

  useEffect(() => {
    if (!visible || !text) { setDisplayed(''); return; }
    setDisplayed('');
    let i = 0;
    const id = window.setInterval(() => {
      i++;
      setDisplayed(text.slice(0, i));
      if (i >= text.length) { clearInterval(id); onComplete?.(); }
    }, 28);
    return () => clearInterval(id);
  }, [text, visible, onComplete]);

  return (
    <AnimatePresence>
      {visible && text && (
        <motion.div
          initial={{ opacity: 0, x: 14, scale: 0.9 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          exit={{ opacity: 0, x: 6, scale: 0.95 }}
          transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
          style={{
            position: 'absolute',
            left: 'calc(100% + 20px)',
            top: '4%',
            width: 290,
            background: 'rgba(10, 18, 38, 0.96)',
            backdropFilter: 'blur(18px)',
            WebkitBackdropFilter: 'blur(18px)',
            border: '1px solid rgba(94,181,13,0.28)',
            borderRadius: 20,
            padding: '18px 22px',
            color: '#e2e8f0',
            fontSize: 19,
            lineHeight: 1.6,
            fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
            fontWeight: 400,
            boxShadow: '0 8px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04)',
            zIndex: 20,
            whiteSpace: 'pre-wrap',
            pointerEvents: 'none',
          }}
        >
          <div style={{
            position: 'absolute',
            left: -7, top: 20,
            width: 0, height: 0,
            borderTop: '6px solid transparent',
            borderBottom: '6px solid transparent',
            borderRight: '7px solid rgba(10, 18, 38, 0.96)',
          }} />
          {displayed}
          {displayed.length < text.length && (
            <motion.span
              animate={{ opacity: [1, 0] }}
              transition={{ repeat: Infinity, duration: 0.55 }}
              style={{ color: '#5EB50D' }}
            >|</motion.span>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// --- Screen Content ---
function ScreenContent({ state }: { state: AvatarState }) {
  if (state === 'thinking') {
    return (
      <>
        {[0, 1, 2].map((i) => (
          <motion.circle
            key={i} cx={76 + i * 24} cy={196} r={5}
            fill="#3333B8" opacity={0.85}
            animate={{ cy: [196, 185, 196], opacity: [0.25, 1, 0.25] }}
            transition={{ duration: 0.72, repeat: Infinity, delay: i * 0.22, ease: 'easeInOut' }}
          />
        ))}
      </>
    );
  }
  if (state === 'success') {
    return (
      <motion.path
        d="M 70 198 L 92 217 L 132 172"
        stroke="#5EB50D" strokeWidth={5}
        strokeLinecap="round" strokeLinejoin="round" fill="none"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      />
    );
  }
  const bars = [
    { y: 170, maxW: 80 }, { y: 182, maxW: 58 }, { y: 194, maxW: 88 },
    { y: 206, maxW: 64 }, { y: 218, maxW: 74 },
  ];
  const color = state === 'active' ? '#5EB50D' : '#3333B8';
  return (
    <>
      {bars.map((b, i) => (
        <motion.rect
          key={i} x={52} y={b.y} height={6} rx={3}
          fill={color} opacity={0.7}
          initial={{ width: b.maxW * 0.4 }}
          animate={{ width: [b.maxW * 0.3, b.maxW, b.maxW * 0.5] }}
          transition={{ duration: 2.4, repeat: Infinity, repeatType: 'mirror', delay: i * 0.28, ease: 'easeInOut' }}
        />
      ))}
    </>
  );
}

function ThinkingParticles() {
  return (
    <>
      {[0, 1, 2, 3].map((i) => (
        <motion.circle
          key={i} cx={66 + i * 22} cy={36} r={2.5 - i * 0.15}
          fill="#3333B8"
          initial={{ opacity: 0, y: 0 }}
          animate={{ opacity: [0, 0.8, 0], y: [-4, -20, -38] }}
          transition={{ duration: 1.1, repeat: Infinity, delay: i * 0.25, ease: 'easeOut' }}
        />
      ))}
    </>
  );
}

export default function AvatarRobot({
  state = 'idle',
  message,
  onMessageComplete,
  size = 220,
}: AvatarRobotProps) {
  const [blinkCount, setBlinkCount] = useState(0);
  const [isTalking, setIsTalking] = useState(false);
  const blinkTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const rotateY = useTransform(mouseX, [-600, 600], [-5, 5]);
  const rotateX = useTransform(mouseY, [-600, 600], [4, -4]);

  useEffect(() => {
    if (message) setIsTalking(true);
  }, [message]);

  useEffect(() => {
    const schedule = () => {
      blinkTimerRef.current = setTimeout(() => {
        setBlinkCount((c: number) => c + 1);
        schedule();
      }, 2600 + Math.random() * 3800);
    };
    schedule();
    return () => { if (blinkTimerRef.current) clearTimeout(blinkTimerRef.current); };
  }, []);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      mouseX.set(e.clientX - (rect.left + rect.width / 2));
      mouseY.set(e.clientY - (rect.top + rect.height / 2));
    };
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, [mouseX, mouseY]);

  const floatAnimate = ((): TargetAndTransition => {
    switch (state) {
      case 'thinking': return { y: [0, -4, 0] as number[], rotate: [-1.2, 1.2, -1.2] as number[] };
      case 'success':  return { y: [0, -14, 0] as number[], scale: [1, 1.06, 1] as number[] };
      case 'active':   return { y: [0, -7, 0] as number[], scale: [1, 1.03, 1] as number[] };
      default:         return { y: [0, -6, 0] as number[], scale: [1, 1.05, 1] as number[] };
    }
  })();

  const floatTransition = ((): Transition => {
    switch (state) {
      case 'thinking': return { duration: 0.85, repeat: Infinity, ease: 'easeInOut' };
      case 'success':  return { duration: 0.65, repeat: 2, ease: 'easeInOut' };
      case 'active':   return { duration: 2.4, repeat: Infinity, ease: 'easeInOut' };
      default:         return { duration: 3.6, repeat: Infinity, ease: 'easeInOut' };
    }
  })();

  const glowCfg = {
    idle:     { spread: 28, opacity: 0.55, rgb: '94,181,13' },
    active:   { spread: 40, opacity: 0.75, rgb: '94,181,13' },
    thinking: { spread: 32, opacity: 0.6,  rgb: '51,51,184' },
    success:  { spread: 44, opacity: 0.85, rgb: '94,181,13' },
  }[state];

  const glowFilter = `drop-shadow(0 0 ${glowCfg.spread}px rgba(${glowCfg.rgb},${glowCfg.opacity})) drop-shadow(0 8px 20px rgba(${glowCfg.rgb},0.35)) drop-shadow(0 2px 6px rgba(0,0,0,0.8))`;
  const svgH = Math.round(size * 1.44);

  return (
    <div
      ref={containerRef}
      style={{ position: 'relative', display: 'inline-block', width: size, height: svgH }}
    >
      {(state === 'active' || state === 'success') && (
        <>
          <motion.div
            animate={{ scale: [0.85, 1.15, 0.85], opacity: [0.18, 0.38, 0.18] }}
            transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut' }}
            style={{
              position: 'absolute', top: '50%', left: '50%',
              transform: 'translate(-50%, -50%)',
              width: size * 1.45, height: size * 1.45,
              borderRadius: '50%',
              border: `1.5px solid ${state === 'success' ? 'rgba(94,181,13,0.6)' : 'rgba(94,181,13,0.4)'}`,
              pointerEvents: 'none',
            }}
          />
          <motion.div
            animate={{ scale: [0.75, 1.25, 0.75], opacity: [0.1, 0.22, 0.1] }}
            transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut', delay: 0.9 }}
            style={{
              position: 'absolute', top: '50%', left: '50%',
              transform: 'translate(-50%, -50%)',
              width: size * 1.72, height: size * 1.72,
              borderRadius: '50%',
              border: '1px solid rgba(51,51,184,0.25)',
              pointerEvents: 'none',
            }}
          />
        </>
      )}
      {state === 'thinking' && (
        <motion.div
          animate={{ scale: [0.9, 1.1, 0.9], opacity: [0.12, 0.3, 0.12] }}
          transition={{ duration: 0.85, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            position: 'absolute', top: '50%', left: '50%',
            transform: 'translate(-50%, -50%)',
            width: size * 1.35, height: size * 1.35,
            borderRadius: '50%',
            border: '1.5px solid rgba(51,51,184,0.45)',
            pointerEvents: 'none',
          }}
        />
      )}

      <motion.div style={{ rotateX, rotateY, transformPerspective: 1200 }}>
        <motion.div
          animate={floatAnimate}
          transition={floatTransition}
          style={{ filter: glowFilter, transition: 'filter 0.9s ease' }}
        >
          <svg viewBox="0 0 200 270" width={size} height={svgH} style={{ display: 'block', overflow: 'visible' }}>
            <defs>
              <radialGradient id="urbi-head" cx="60" cy="56" r="90" gradientUnits="userSpaceOnUse">
                <stop offset="0%"   stopColor="#3a6fcc" />
                <stop offset="52%"  stopColor="#1e4490" />
                <stop offset="100%" stopColor="#112260" />
              </radialGradient>
              <radialGradient id="urbi-body" cx="62" cy="160" r="98" gradientUnits="userSpaceOnUse">
                <stop offset="0%"   stopColor="#2e58b0" />
                <stop offset="58%"  stopColor="#1a3575" />
                <stop offset="100%" stopColor="#0e1f55" />
              </radialGradient>
              <radialGradient id="urbi-iris-l" cx="63" cy="76" r="17" gradientUnits="userSpaceOnUse">
                <stop offset="0%"   stopColor="#e0fff0" />
                <stop offset="28%"  stopColor="#7fff60" />
                <stop offset="52%"  stopColor="#5EB50D" />
                <stop offset="78%"  stopColor="#3333B8" />
                <stop offset="100%" stopColor="#0a1a3a" />
              </radialGradient>
              <radialGradient id="urbi-iris-r" cx="123" cy="76" r="17" gradientUnits="userSpaceOnUse">
                <stop offset="0%"   stopColor="#e0fff0" />
                <stop offset="28%"  stopColor="#7fff60" />
                <stop offset="52%"  stopColor="#5EB50D" />
                <stop offset="78%"  stopColor="#3333B8" />
                <stop offset="100%" stopColor="#0a1a3a" />
              </radialGradient>
              <linearGradient id="urbi-limb-l" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%"   stopColor="#2d5aaa" />
                <stop offset="100%" stopColor="#112258" />
              </linearGradient>
              <linearGradient id="urbi-limb-r" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%"   stopColor="#2d5aaa" />
                <stop offset="100%" stopColor="#112258" />
              </linearGradient>
              <linearGradient id="urbi-screen" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%"   stopColor="#0d2244" stopOpacity="0.96" />
                <stop offset="100%" stopColor="#04091a" stopOpacity="0.99" />
              </linearGradient>
              <radialGradient id="urbi-orb" cx="38%" cy="32%" r="65%">
                <stop offset="0%"   stopColor="#9cffc2" />
                <stop offset="55%"  stopColor="#5EB50D" />
                <stop offset="100%" stopColor="#145c30" />
              </radialGradient>
              <linearGradient id="urbi-neck" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%"   stopColor="#0e2050" />
                <stop offset="50%"  stopColor="#2a4e9a" />
                <stop offset="100%" stopColor="#0e2050" />
              </linearGradient>
              <linearGradient id="urbi-rim" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%"   stopColor="rgba(255,255,255,0.60)" />
                <stop offset="50%"  stopColor="rgba(255,255,255,0.05)" />
                <stop offset="100%" stopColor="rgba(255,255,255,0)" />
              </linearGradient>
              <filter id="urbi-glow-eye" x="-60%" y="-60%" width="220%" height="220%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="2.8" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {state === 'thinking' && <ThinkingParticles />}

            {/* Antenna */}
            <rect x={97} y={22} width={6} height={22} rx={3} fill="url(#urbi-neck)" opacity={0.9} />
            <motion.circle
              cx={100} cy={18} r={15} fill="none" stroke="#5EB50D" strokeWidth={1}
              animate={{ r: [14, 22, 14], opacity: [0.22, 0, 0.22] }}
              transition={{ duration: 2.8, repeat: Infinity, ease: 'easeOut' }}
            />
            <motion.circle
              cx={100} cy={18} r={10} fill="url(#urbi-orb)"
              animate={{ r: [9, 11.5, 9], opacity: [0.75, 1, 0.75] }}
              transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut' }}
            />
            <ellipse cx={97} cy={15} rx={3} ry={2} fill="rgba(255,255,255,0.55)" />

            {/* Head */}
            <rect x={26} y={42} width={148} height={88} rx={20} fill="url(#urbi-head)" />
            <rect x={26} y={42} width={148} height={44} rx={20} fill="url(#urbi-rim)" opacity={0.45} />
            <rect x={26} y={42} width={148} height={88} rx={20} fill="none"
              stroke="rgba(255,255,255,0.30)" strokeWidth={1.5} />
            <rect x={26} y={42} width={148} height={88} rx={20} fill="none"
              stroke="rgba(94,181,13,0.55)" strokeWidth={2} />
            <ellipse cx={100} cy={46} rx={58} ry={6} fill="rgba(255,255,255,0.18)" />

            {/* Eye sockets */}
            <circle cx={70} cy={83} r={24} fill="#081530" />
            <circle cx={130} cy={83} r={24} fill="#081530" />
            <circle cx={70} cy={83} r={22} fill="#0f2048" stroke="rgba(255,255,255,0.14)" strokeWidth={1.5} />
            <circle cx={130} cy={83} r={22} fill="#0f2048" stroke="rgba(255,255,255,0.14)" strokeWidth={1.5} />

            {/* Left iris */}
            <motion.ellipse
              key={"bl-" + blinkCount}
              cx={70} cy={83} rx={15} ry={15}
              fill="url(#urbi-iris-l)" filter="url(#urbi-glow-eye)"
              animate={{ ry: [15, 0.5, 15] }} initial={{ ry: 15 }}
              transition={{ duration: 0.13, times: [0, 0.5, 1], ease: 'easeInOut' }}
            />
            <motion.circle cx={70} cy={83} r={6} fill="#020810"
              animate={{ cx: [70, 73, 70], cy: [83, 81, 83] }}
              transition={{ duration: 4.8, repeat: Infinity, ease: 'easeInOut', delay: 0.4 }}
            />
            <ellipse cx={74} cy={77} rx={4.5} ry={2.8} fill="rgba(255,255,255,0.92)" />
            <circle cx={65} cy={88} r={1.8} fill="rgba(255,255,255,0.32)" />

            {/* Right iris */}
            <motion.ellipse
              key={"br-" + blinkCount}
              cx={130} cy={83} rx={15} ry={15}
              fill="url(#urbi-iris-r)" filter="url(#urbi-glow-eye)"
              animate={{ ry: [15, 0.5, 15] }} initial={{ ry: 15 }}
              transition={{ duration: 0.13, times: [0, 0.5, 1], ease: 'easeInOut' }}
            />
            <motion.circle cx={130} cy={83} r={6} fill="#020810"
              animate={{ cx: [130, 127, 130], cy: [83, 81, 83] }}
              transition={{ duration: 4.8, repeat: Infinity, ease: 'easeInOut', delay: 0.9 }}
            />
            <ellipse cx={134} cy={77} rx={4.5} ry={2.8} fill="rgba(255,255,255,0.92)" />
            <circle cx={125} cy={88} r={1.8} fill="rgba(255,255,255,0.32)" />

            {(state === 'active' || state === 'success') && (
              <>
                <motion.circle cx={70} cy={83} r={22} fill="none"
                  stroke="#5EB50D" strokeWidth={1.2}
                  animate={{ opacity: [0.12, 0.55, 0.12], r: [21, 27, 21] }}
                  transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
                />
                <motion.circle cx={130} cy={83} r={22} fill="none"
                  stroke="#5EB50D" strokeWidth={1.2}
                  animate={{ opacity: [0.12, 0.55, 0.12], r: [21, 27, 21] }}
                  transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut', delay: 0.35 }}
                />
              </>
            )}

            {/* Mouth */}
            {isTalking ? (
              <motion.ellipse
                cx={100} cy={115} rx={17}
                animate={{ ry: [2, 7, 3, 6, 2] }}
                transition={{ duration: 0.3, repeat: Infinity, ease: 'easeInOut' }}
                fill="#020810"
                stroke="#5EB50D" strokeWidth={1.5}
              />
            ) : state === 'thinking' ? (
              <path d="M 80 114 Q 100 112 120 114"
                stroke="#3333B8" strokeWidth={2} strokeLinecap="round" fill="none" opacity={0.7} />
            ) : state === 'success' ? (
              <motion.path d="M 78 112 Q 100 121 122 112"
                stroke="#5EB50D" strokeWidth={2.5} strokeLinecap="round" fill="none"
                initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              />
            ) : (
              <path d="M 82 113 Q 100 118 118 113"
                stroke="rgba(255,255,255,0.30)" strokeWidth={2} strokeLinecap="round" fill="none" />
            )}

            {/* Neck */}
            <rect x={86} y={130} width={28} height={20} rx={7} fill="url(#urbi-neck)" />
            <rect x={86} y={130} width={28} height={20} rx={7} fill="none"
              stroke="rgba(255,255,255,0.08)" strokeWidth={1} />

            {/* Body */}
            <rect x={28} y={148} width={144} height={98} rx={18} fill="url(#urbi-body)" />
            <rect x={28} y={148} width={144} height={40} rx={18} fill="url(#urbi-rim)" opacity={0.32} />
            <rect x={28} y={148} width={144} height={98} rx={18} fill="none"
              stroke="rgba(255,255,255,0.22)" strokeWidth={1.5} />
            <rect x={28} y={148} width={144} height={98} rx={18} fill="none"
              stroke="rgba(94,181,13,0.45)" strokeWidth={2} />
            <ellipse cx={100} cy={152} rx={54} ry={6} fill="rgba(255,255,255,0.18)" />

            {/* Screen */}
            <rect x={48} y={160} width={104} height={72} rx={10} fill="url(#urbi-screen)" />
            <rect x={48} y={160} width={104} height={72} rx={10} fill="none"
              stroke="rgba(94,181,13,0.50)" strokeWidth={1.5} />
            <rect x={50} y={162} width={100} height={9} rx={4} fill="rgba(255,255,255,0.04)" />
            <ScreenContent state={state} />

            {/* LED indicators */}
            <motion.circle cx={42} cy={162} r={4.5} fill="#5EB50D"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1.7, repeat: Infinity, ease: 'easeInOut' }}
            />
            <motion.circle cx={158} cy={162} r={4.5} fill="#6666ff"
              animate={{ opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 1.7, repeat: Infinity, ease: 'easeInOut', delay: 0.85 }}
            />

            {/* Left arm */}
            <motion.rect x={6} y={153} width={20} height={64} rx={10}
              fill="url(#urbi-limb-l)"
              style={{ transformOrigin: '16px 153px' }}
              animate={state === 'thinking' ? { rotate: [0, -7, 0] as number[] } : {}}
              transition={{ duration: 1.0, repeat: Infinity, ease: 'easeInOut' }}
            />
            <rect x={6} y={153} width={20} height={64} rx={10} fill="none"
              stroke="rgba(255,255,255,0.22)" strokeWidth={1.5} />
            <circle cx={16} cy={225} r={9} fill="url(#urbi-limb-l)" />
            <circle cx={16} cy={225} r={9} fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth={1} />
            <ellipse cx={13} cy={222} rx={2.5} ry={1.5} fill="rgba(255,255,255,0.45)" />

            {/* Right arm */}
            <motion.rect x={174} y={153} width={20} height={64} rx={10}
              fill="url(#urbi-limb-r)"
              style={{ transformOrigin: '184px 153px' }}
              animate={state === 'thinking' ? { rotate: [0, 7, 0] as number[] } : {}}
              transition={{ duration: 1.0, repeat: Infinity, ease: 'easeInOut', delay: 0.3 }}
            />
            <rect x={174} y={153} width={20} height={64} rx={10} fill="none"
              stroke="rgba(255,255,255,0.22)" strokeWidth={1.5} />
            <circle cx={184} cy={225} r={9} fill="url(#urbi-limb-r)" />
            <circle cx={184} cy={225} r={9} fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth={1} />
            <ellipse cx={187} cy={222} rx={2.5} ry={1.5} fill="rgba(255,255,255,0.45)" />

            {/* Feet */}
            <rect x={54} y={246} width={36} height={22} rx={10} fill="url(#urbi-limb-l)" />
            <rect x={54} y={246} width={36} height={22} rx={10} fill="none"
              stroke="rgba(255,255,255,0.16)" strokeWidth={1} />
            <circle cx={65} cy={262} r={2.5} fill="#5EB50D" opacity={0.5} />

            <rect x={110} y={246} width={36} height={22} rx={10} fill="url(#urbi-limb-r)" />
            <rect x={110} y={246} width={36} height={22} rx={10} fill="none"
              stroke="rgba(255,255,255,0.16)" strokeWidth={1} />
            <circle cx={135} cy={262} r={2.5} fill="#3333B8" opacity={0.5} />

            <motion.rect x={28} y={148} width={144} height={98} rx={18}
              fill="rgba(94,181,13,0.06)"
              animate={{ opacity: [0, 1, 0] }}
              transition={{ duration: 3.6, repeat: Infinity, ease: 'easeInOut' }}
            />
          </svg>
        </motion.div>
      </motion.div>

      <SpeechBubble
        text={message ?? ''}
        visible={!!message}
        onComplete={() => { setIsTalking(false); onMessageComplete?.(); }}
      />
    </div>
  );
}