import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AvatarRobot, { type AvatarState } from './AvatarRobot';

const GREEN = '#5EB50D';
const BLUE  = '#3333B8';
const BG    = '#0d0d0d';

type Screen = 'home' | 'rut' | 'questions' | 'done';

const QUESTIONS = [
  {
    key: 'objetivo',
    text: '¿Buscas para vivir o invertir?',
    options: [
      { label: 'QUIERO MI HOGAR',  value: 'vivir' },
      { label: 'QUIERO INVERTIR',  value: 'invertir' },
    ],
  },
  {
    key: 'tipo',
    text: '¿Qué tipo de propiedad te interesa?',
    options: [
      { label: 'Departamento', value: 'dept' },
      { label: 'Casa',        value: 'casa' },
      { label: 'Oficina',     value: 'oficina' },
    ],
  },
  {
    key: 'zona',
    text: '¿En qué comuna o sector buscas?',
    options: [
      { label: 'Vitacura', value: 'vitacura' },
      { label: 'Providencia', value: 'providencia' },
      { label: 'Las Condes', value: 'lascondes' },
      { label: 'Ñuñoa',   value: 'nunoa' },
    ],
  },
  {
    key: 'presupuesto',
    text: '¿Cuál es tu presupuesto estimado?',
    options: [
      { label: 'Hasta 3.000 UF',  value: '3000' },
      { label: 'Hasta 6.000 UF',  value: '6000' },
      { label: 'Más de 6.000 UF', value: '6001' },
    ],
  },
];

function Btn({
  children, onClick, variant = 'green', disabled = false,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'green' | 'outline' | 'ghost';
  disabled?: boolean;
}) {
  const styles: React.CSSProperties = {
    display: 'block',
    width: '100%',
    padding: '26px 32px',
    fontSize: 22,
    fontWeight: 700,
    fontFamily: '"Inter", -apple-system, sans-serif',
    letterSpacing: '0.07em',
    border: 'none',
    borderRadius: 14,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.45 : 1,
    transition: 'opacity 0.2s, transform 0.12s',
    ...(variant === 'green'
      ? { background: GREEN, color: '#fff' }
      : variant === 'outline'
      ? { background: 'transparent', color: GREEN, border: `2px solid ${GREEN}` }
      : { background: 'rgba(255,255,255,0.06)', color: '#ccc' }),
  };
  return (
    <motion.button
      style={styles}
      onClick={disabled ? undefined : onClick}
      whileTap={{ scale: disabled ? 1 : 0.97 }}
      whileHover={{ opacity: disabled ? 0.45 : 0.88 }}
    >
      {children}
    </motion.button>
  );
}

const screenVariants = {
  initial:  { opacity: 0, y: 28 },
  animate:  { opacity: 1, y: 0,  transition: { duration: 0.45, ease: [0.25, 0.1, 0.25, 1] } },
  exit:     { opacity: 0, y: -18, transition: { duration: 0.28, ease: 'easeIn' } },
};

export default function KioskScreen() {
  const [screen, setScreen]      = useState<Screen>('home');
  const [rut, setRut]            = useState('');
  const [rutError, setRutError]  = useState('');
  const [step, setStep]          = useState(0);
  const [answers, setAnswers]    = useState<Record<string, string>>({});
  const [folio]                  = useState('A-12');
  const [eta]                    = useState(5);
  const [countdown, setCountdown] = useState(6);
  const [avatarState, setAvatarState]     = useState<AvatarState>('idle');
  const [avatarMessage, setAvatarMessage] = useState('Hola, soy Urbi. Saca tu número o inicia asesoría guiada.');
  const rutInputRef = useRef<HTMLInputElement>(null);

  // Countdown on done screen
  useEffect(() => {
    if (screen !== 'done') return;
    setCountdown(6);
    const tick = setInterval(() => {
      setCountdown((c) => {
        if (c <= 1) {
          clearInterval(tick);
          handleReset();
          return 0;
        }
        return c - 1;
      });
    }, 1000);
    return () => clearInterval(tick);
  }, [screen]);

  function handleReset() {
    setScreen('home');
    setRut('');
    setRutError('');
    setStep(0);
    setAnswers({});
    setAvatarState('idle');
    setAvatarMessage('Hola, soy Urbi. Saca tu número o inicia asesoría guiada.');
  }

  function goToRut() {
    setAvatarState('active');
    setAvatarMessage('Ingresa tu RUT para identificarte. Sin puntos, con guión.');
    setScreen('rut');
    setTimeout(() => rutInputRef.current?.focus(), 400);
  }

  function submitRut() {
    if (rut.length < 7) { setRutError('RUT demasiado corto.'); return; }
    setRutError('');
    setAvatarState('thinking');
    setAvatarMessage('Buscando tu perfil...');
    setTimeout(() => {
      setAvatarState('active');
      setAvatarMessage('¡Listo! Ahora cuéntame un poco sobre lo que buscas.');
      setStep(0);
      setScreen('questions');
    }, 1400);
  }

  function handleRutInput(value: string) {
    // Format RUT: remove non-alphanumeric, auto-insert dash
    const clean = value.replace(/[^0-9kK]/g, '').slice(0, 9);
    if (clean.length >= 2) {
      setRut(clean.slice(0, -1) + '-' + clean.slice(-1));
    } else {
      setRut(clean);
    }
    setRutError('');
  }

  function handleAnswer(value: string) {
    const key = QUESTIONS[step].key;
    const newAnswers = { ...answers, [key]: value };
    setAnswers(newAnswers);
    if (step < QUESTIONS.length - 1) {
      setAvatarMessage(QUESTIONS[step + 1].text);
      setStep(step + 1);
    } else {
      setAvatarState('success');
      setAvatarMessage(`Tu turno es el ${folio}. Un ejecutivo te atenderá pronto.`);
      setScreen('done');
    }
  }

  const cardStyle: React.CSSProperties = {
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.09)',
    borderRadius: 20,
    padding: '36px 40px',
    width: '100%',
    maxWidth: 860,
    boxSizing: 'border-box',
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: BG,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '60px 48px 80px',
      fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
      color: '#fff',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background aura */}
      <div style={{
        position: 'absolute', top: '18%', left: '50%',
        transform: 'translateX(-50%)',
        width: 800, height: 800,
        borderRadius: '50%',
        background: `radial-gradient(circle, rgba(94,181,13,0.08) 0%, rgba(51,51,184,0.06) 50%, transparent 72%)`,
        pointerEvents: 'none',
        zIndex: 0,
      }} />

      {/* Logo */}
      <div style={{ position: 'relative', zIndex: 1, textAlign: 'center', marginBottom: 10 }}>
        <div style={{
          fontSize: 80, fontWeight: 900, letterSpacing: '-0.02em',
          display: 'inline-flex', alignItems: 'baseline', gap: 2,
        }}>
          <span style={{ color: '#fff' }}>urbani</span>
          <span style={{ color: GREEN, fontSize: '1.05em' }}>.</span>
        </div>
        <div style={{
          margin: '6px auto 0',
          width: 72, height: 6, borderRadius: 3,
          background: `linear-gradient(90deg, ${GREEN}, ${BLUE})`,
        }} />
        <div style={{ fontSize: 18, color: '#888', letterSpacing: '0.28em', marginTop: 14 }}>
          ASISTENTE DE ATENCIÓN
        </div>
      </div>

      {/* Avatar */}
      <div style={{ position: 'relative', zIndex: 2, marginBottom: 16 }}>
        <AvatarRobot state={avatarState} message={avatarMessage} size={560} />
      </div>

      {/* Turno badge */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        style={{
          ...cardStyle,
          display: 'flex', alignItems: 'center', justifyContent: 'space-around',
          marginBottom: 28, zIndex: 1,
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 14, color: '#888', letterSpacing: '0.18em', marginBottom: 4 }}>TURNO</div>
          <div style={{ fontSize: 120, fontWeight: 900, color: GREEN, lineHeight: 1 }}>{folio}</div>
        </div>
        <div style={{ width: 1, height: 100, background: 'rgba(255,255,255,0.10)' }} />
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 14, color: '#888', letterSpacing: '0.18em', marginBottom: 4 }}>ESPERA EST.</div>
          <div style={{ fontSize: 88, fontWeight: 800, color: '#fff', lineHeight: 1 }}>
            {eta}
            <span style={{ fontSize: 32, fontWeight: 400, color: '#888', marginLeft: 6 }}>min</span>
          </div>
        </div>
      </motion.div>

      {/* Screens */}
      <div style={{ width: '100%', maxWidth: 860, position: 'relative', zIndex: 1 }}>
        <AnimatePresence mode="wait">

          {/* HOME */}
          {screen === 'home' && (
            <motion.div key="home" variants={screenVariants} initial="initial" animate="animate" exit="exit">
              <div style={cardStyle}>
                <div style={{ fontSize: 13, color: GREEN, letterSpacing: '0.22em', marginBottom: 10 }}>
                  ASESORÍA PERSONALIZADA
                </div>
                <div style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
                  Encuentra tu <span style={{ color: GREEN }}>hogar</span> o inversión ideal
                </div>
                <div style={{ fontSize: 17, color: '#999', marginBottom: 32 }}>
                  Saca tu número y te guiamos según tu perfil
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <Btn onClick={goToRut}>TOMAR NÚMERO DE ATENCIÓN</Btn>
                  <Btn variant="outline" onClick={goToRut}>INICIAR ASESORÍA GUIADA</Btn>
                </div>
              </div>
            </motion.div>
          )}

          {/* RUT */}
          {screen === 'rut' && (
            <motion.div key="rut" variants={screenVariants} initial="initial" animate="animate" exit="exit">
              <div style={cardStyle}>
                <div style={{ fontSize: 13, color: GREEN, letterSpacing: '0.22em', marginBottom: 14 }}>
                  IDENTIFICACIÓN
                </div>
                <div style={{ fontSize: 26, fontWeight: 700, marginBottom: 24 }}>
                  Ingresa tu RUT
                </div>
                <input
                  ref={rutInputRef}
                  value={rut}
                  onChange={(e) => handleRutInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && submitRut()}
                  placeholder="12345678-9"
                  style={{
                    width: '100%', boxSizing: 'border-box',
                    padding: '22px 24px', fontSize: 34, fontWeight: 700,
                    background: 'rgba(255,255,255,0.05)',
                    border: `2px solid ${rutError ? '#ff4d4f' : 'rgba(255,255,255,0.15)'}`,
                    borderRadius: 12, color: '#fff',
                    outline: 'none', marginBottom: 10,
                    fontFamily: '"Inter", monospace',
                    letterSpacing: '0.08em',
                  }}
                />
                {rutError && (
                  <div style={{ color: '#ff7875', fontSize: 15, marginBottom: 16 }}>{rutError}</div>
                )}
                <div style={{ display: 'flex', gap: 14, marginTop: 18 }}>
                  <div style={{ flex: 1 }}>
                    <Btn variant="ghost" onClick={handleReset}>VOLVER</Btn>
                  </div>
                  <div style={{ flex: 2 }}>
                    <Btn onClick={submitRut} disabled={rut.length < 5}>CONTINUAR</Btn>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* QUESTIONS */}
          {screen === 'questions' && (
            <motion.div key={`q-${step}`} variants={screenVariants} initial="initial" animate="animate" exit="exit">
              <div style={cardStyle}>
                {/* Progress */}
                <div style={{ display: 'flex', gap: 8, marginBottom: 28 }}>
                  {QUESTIONS.map((_, i) => (
                    <div key={i} style={{
                      flex: 1, height: 4, borderRadius: 2,
                      background: i <= step ? GREEN : 'rgba(255,255,255,0.12)',
                      transition: 'background 0.3s',
                    }} />
                  ))}
                </div>
                <div style={{ fontSize: 13, color: '#888', letterSpacing: '0.18em', marginBottom: 12 }}>
                  PREGUNTA {step + 1} DE {QUESTIONS.length}
                </div>
                <div style={{ fontSize: 28, fontWeight: 700, marginBottom: 30 }}>
                  {QUESTIONS[step].text}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {QUESTIONS[step].options.map((opt) => (
                    <Btn key={opt.value} variant="outline" onClick={() => handleAnswer(opt.value)}>
                      {opt.label}
                    </Btn>
                  ))}
                </div>
                <div style={{ marginTop: 20 }}>
                  <Btn variant="ghost" onClick={handleReset}>CANCELAR</Btn>
                </div>
              </div>
            </motion.div>
          )}

          {/* DONE */}
          {screen === 'done' && (
            <motion.div key="done" variants={screenVariants} initial="initial" animate="animate" exit="exit">
              <div style={{ ...cardStyle, textAlign: 'center' }}>
                <motion.div
                  initial={{ scale: 0.4, opacity: 0 }}
                  animate={{ scale: 1,   opacity: 1 }}
                  transition={{ type: 'spring', stiffness: 260, damping: 18 }}
                  style={{
                    width: 88, height: 88, borderRadius: '50%',
                    background: `radial-gradient(circle, ${GREEN}33, ${GREEN}11)`,
                    border: `3px solid ${GREEN}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    margin: '0 auto 24px',
                    fontSize: 40,
                  }}
                >✓</motion.div>
                <div style={{ fontSize: 36, fontWeight: 800, marginBottom: 12 }}>
                  Tu turno: <span style={{ color: GREEN }}>{folio}</span>
                </div>
                <div style={{ fontSize: 22, color: '#ccc', marginBottom: 28, lineHeight: 1.6 }}>
                  Un ejecutivo te atenderá en aprox{' '}
                  <strong style={{ color: '#fff' }}>{eta} minuto{eta !== 1 ? 's' : ''}</strong>.
                </div>
                {/* Countdown bar */}
                <div style={{
                  height: 5, borderRadius: 3,
                  background: 'rgba(255,255,255,0.12)',
                  overflow: 'hidden', marginBottom: 16,
                }}>
                  <motion.div
                    initial={{ width: '100%' }}
                    animate={{ width: '0%' }}
                    transition={{ duration: 6, ease: 'linear' }}
                    style={{ height: '100%', background: GREEN, borderRadius: 3 }}
                  />
                </div>
                <div style={{ fontSize: 15, color: '#666' }}>
                  Volviendo al inicio en {countdown}s…
                </div>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}