import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AvatarRobot, { type AvatarState } from './AvatarRobot';

const GREEN = '#5EB50D';
const BLUE  = '#3333B8';
const BG    = '#0d0d0d';

const API_BASE = '/api/v1';
const KIOSK_TOKEN = 'dev-kiosk-token';
const KIOSK_ID = 'kiosk-1';

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Kiosk-Token': KIOSK_TOKEN,
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API ${path} → ${res.status}: ${err}`);
  }
  return res.json() as Promise<T>;
}

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

// --- Teclado numérico táctil ---
function NumericKeyboard({
  onKey,
}: {
  onKey: (key: string) => void;
}) {
  const rows = [
    ['1', '2', '3'],
    ['4', '5', '6'],
    ['7', '8', '9'],
    ['K', '0', '⌫'],
  ];
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(3, 1fr)',
      gap: 10,
      marginTop: 20,
    }}>
      {rows.flat().map((key) => (
        <motion.button
          key={key}
          onPointerDown={(e) => { e.preventDefault(); onKey(key); }}
          whileTap={{ scale: 0.91 }}
          style={{
            padding: '24px 0',
            fontSize: key === '⌫' ? 28 : 32,
            fontWeight: key === '⌫' ? 400 : 700,
            fontFamily: '"Inter", -apple-system, sans-serif',
            background: key === '⌫'
              ? 'rgba(255,80,80,0.12)'
              : key === 'K'
              ? 'rgba(51,51,184,0.22)'
              : 'rgba(255,255,255,0.07)',
            color: key === '⌫' ? '#ff7875' : '#fff',
            border: key === '⌫'
              ? '1.5px solid rgba(255,80,80,0.25)'
              : key === 'K'
              ? `1.5px solid rgba(51,51,184,0.45)`
              : '1.5px solid rgba(255,255,255,0.10)',
            borderRadius: 14,
            cursor: 'pointer',
            userSelect: 'none',
            WebkitUserSelect: 'none',
            touchAction: 'manipulation',
          }}
        >
          {key}
        </motion.button>
      ))}
    </div>
  );
}

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
  const [rutRaw, setRutRaw]      = useState('');
  const [rutError, setRutError]  = useState('');
  // RUT formateado para mostrar: 12345678-9
  const rut = rutRaw.length >= 2
    ? rutRaw.slice(0, -1) + '-' + rutRaw.slice(-1)
    : rutRaw;
  const [step, setStep]          = useState(0);
  const [answers, setAnswers]    = useState<Record<string, string>>({});
  const [folio, setFolio]        = useState('');
  const [eta, setEta]            = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [apiError, setApiError]  = useState<string | null>(null);
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
    setSessionId(null);
    setApiError(null);
    setFolio('');
    setEta(0);
    setRutRaw('');
    setRutError('');
    setStep(0);
    setAnswers({});
    setAvatarState('idle');
    setAvatarMessage('Hola, soy Urbi. Saca tu número o inicia asesoría guiada.');
  }

  async function goToRut() {
    setApiError(null);
    setAvatarState('thinking');
    setAvatarMessage('Un momento...');
    try {
      const data = await apiPost<{ session_id: string; status: string }>('/sessions/', { kiosk_id: KIOSK_ID });
      setSessionId(data.session_id);
    } catch {
      // si la API no está disponible, dejamos sessionId=null y seguimos igual
    }
    setAvatarState('active');
    setAvatarMessage('Ingresa tu RUT para identificarte. Sin puntos, con guión.');
    setScreen('rut');
    setTimeout(() => rutInputRef.current?.focus(), 400);
  }

  async function submitRut() {
    if (rutRaw.length < 7) { setRutError('RUT demasiado corto.'); return; }
    setRutError('');
    setAvatarState('thinking');
    setAvatarMessage('Buscando tu perfil...');
    if (sessionId) {
      try {
        await apiPost('/sessions/' + sessionId + '/answers', {
          question_key: 'rut',
          answer_value: rut,
          answer_label: rut,
        });
      } catch { /* continuar aunque falle */ }
    }
    setTimeout(() => {
      setAvatarState('active');
      setAvatarMessage('¡Listo! Ahora cuéntame un poco sobre lo que buscas.');
      setStep(0);
      setScreen('questions');
    }, 900);
  }

  function handleVirtualKey(key: string) {
    setRutError('');
    if (key === '⌫') {
      setRutRaw((prev) => prev.slice(0, -1));
      return;
    }
    const char = key.toUpperCase();
    setRutRaw((prev) => {
      if (prev.length >= 9) return prev;
      return prev + char;
    });
  }

  async function handleAnswer(value: string) {
    const q = QUESTIONS[step];
    const label = q.options.find((o) => o.value === value)?.label ?? value;
    const newAnswers = { ...answers, [q.key]: value };
    setAnswers(newAnswers);

    if (sessionId) {
      try {
        await apiPost('/sessions/' + sessionId + '/answers', {
          question_key: q.key,
          answer_value: value,
          answer_label: label,
        });
      } catch { /* continuar aunque falle */ }
    }

    if (step < QUESTIONS.length - 1) {
      setAvatarMessage(QUESTIONS[step + 1].text);
      setStep(step + 1);
    } else {
      // Crear ticket en la cola
      setAvatarState('thinking');
      setAvatarMessage('Generando tu número de turno...');
      let ticketNumber = 'A-??';
      let etaMin = 0;
      if (sessionId) {
        try {
          const ticket = await apiPost<{ ticket_number: string; eta_minutes: number }>('/queue/tickets', {
            session_id: sessionId,
          });
          ticketNumber = ticket.ticket_number;
          etaMin = ticket.eta_minutes;
        } catch (e: unknown) {
          const msg = e instanceof Error ? e.message : String(e);
          setApiError(msg);
        }
      }
      setFolio(ticketNumber);
      setEta(etaMin);
      setAvatarState('success');
      setAvatarMessage(`Tu turno es el ${ticketNumber}. Un ejecutivo te atenderá pronto.`);
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
              <div style={{ ...cardStyle, textAlign: 'center' }}>
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
                <div style={{
                  width: '100%', boxSizing: 'border-box',
                  padding: '22px 24px', fontSize: 34, fontWeight: 700,
                  background: 'rgba(255,255,255,0.05)',
                  border: `2px solid ${rutError ? '#ff4d4f' : rutRaw.length > 0 ? GREEN : 'rgba(255,255,255,0.15)'}`,
                  borderRadius: 12, color: rutRaw.length > 0 ? '#fff' : '#555',
                  marginBottom: 10,
                  fontFamily: '"Inter", monospace',
                  letterSpacing: '0.10em',
                  minHeight: 80,
                  display: 'flex', alignItems: 'center',
                  transition: 'border-color 0.2s',
                }}>
                  {rutRaw.length > 0 ? rut : '12345678-9'}
                  {rutRaw.length > 0 && (
                    <motion.span
                      animate={{ opacity: [1, 0] }}
                      transition={{ repeat: Infinity, duration: 0.6 }}
                      style={{ color: GREEN, marginLeft: 2, fontWeight: 300 }}
                    >|</motion.span>
                  )}
                </div>
                {rutError && (
                  <div style={{ color: '#ff7875', fontSize: 15, marginBottom: 8 }}>{rutError}</div>
                )}
                <NumericKeyboard onKey={handleVirtualKey} />
                <div style={{ display: 'flex', gap: 14, marginTop: 18 }}>
                  <div style={{ flex: 1 }}>
                    <Btn variant="ghost" onClick={handleReset}>VOLVER</Btn>
                  </div>
                  <div style={{ flex: 2 }}>
                    <Btn onClick={submitRut} disabled={rutRaw.length < 7}>CONTINUAR</Btn>
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