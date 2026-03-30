import React, { useState } from 'react';

export default function KioskScreen() {
  const [hasTicket, setHasTicket] = useState(false);
  const [step, setStep] = useState(0);
  const [folio, setFolio] = useState('A-12'); // Simulado
  const [eta, setEta] = useState(5); // Simulado
  const [answers, setAnswers] = useState({});

  // Preguntas de perfilamiento
  const questions = [
    {
      key: 'objetivo',
      text: '¿Buscas para vivir o invertir?',
      options: [
        { label: 'QUIERO MI HOGAR', value: 'vivir' },
        { label: 'QUIERO INVERTIR', value: 'invertir' },
      ],
    },
    {
      key: 'tipo',
      text: '¿Qué tipo de propiedad te interesa?',
      options: [
        { label: 'Departamento', value: 'dept' },
        { label: 'Casa', value: 'casa' },
        { label: 'Oficina', value: 'oficina' },
      ],
    },
    {
      key: 'zona',
      text: '¿En qué comuna o sector buscas?',
      options: [
        { label: 'Vitacura', value: 'vitacura' },
        { label: 'Ñuñoa', value: 'nunoa' },
        { label: 'Maipú', value: 'maipu' },
      ],
    },
    {
      key: 'presupuesto',
      text: '¿Cuál es tu presupuesto estimado?',
      options: [
        { label: 'Hasta 4000 UF', value: '4000' },
        { label: 'Hasta 6000 UF', value: '6000' },
        { label: 'Más de 6000 UF', value: '6001' },
      ],
    },
  ];


  const currentQuestion = questions[step];

  const handleAnswer = (value: string) => {
    setAnswers({ ...answers, [currentQuestion.key]: value });
    if (step < questions.length - 1) {
      setStep(step + 1);
    } else {
      alert('¡Gracias! Pronto te llamará un ejecutivo.');
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '0 auto', padding: 24, fontFamily: 'sans-serif' }}>
      <h1 style={{ color: '#222', marginBottom: 8 }}>ASISTENTE DIGITAL URBANI</h1>
      <div style={{ marginBottom: 16 }}>
        <strong>TU NÚMERO DE ATENCIÓN: {folio} | ESPERA ESTIMADA: {eta} MIN</strong>
      </div>
      {!hasTicket ? (
        <button
          style={{
            display: 'block',
            width: '100%',
            marginBottom: 24,
            padding: 20,
            fontSize: 22,
            background: '#1976d2',
            color: '#fff',
            border: 'none',
            borderRadius: 10,
            cursor: 'pointer',
            fontWeight: 600,
          }}
          onClick={() => setHasTicket(true)}
        >
          TOMAR NÚMERO DE ATENCIÓN
        </button>
      ) : (
        <div style={{ background: '#f5f5f5', borderRadius: 12, padding: 16, marginBottom: 16 }}>
          <div style={{ marginBottom: 12, fontWeight: 500 }}>
            Excelente. Te ayudaré a encontrar opciones. Responde estas breves preguntas:
          </div>
          <div style={{ fontSize: 20, marginBottom: 16 }}>{currentQuestion.text}</div>
          {currentQuestion.options.map((opt) => (
            <button
              key={opt.value}
              style={{
                display: 'block',
                width: '100%',
                marginBottom: 12,
                padding: 16,
                fontSize: 18,
                background: '#1976d2',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                cursor: 'pointer',
              }}
              onClick={() => handleAnswer(opt.value)}
            >
              {opt.label}
            </button>
          ))}
          <button
            style={{
              display: 'block',
              width: '100%',
              marginBottom: 0,
              padding: 12,
              fontSize: 16,
              background: '#eee',
              color: '#333',
              border: 'none',
              borderRadius: 8,
              cursor: 'pointer',
            }}
            onClick={() => handleAnswer('skip')}
          >
            Saltar pregunta | No lo sé
          </button>
        </div>
      )}
    </div>
  );
}
