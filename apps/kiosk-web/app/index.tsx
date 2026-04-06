import React from 'react';
import KioskScreen from './KioskScreen';

function getApiOrigin(): string {
  const envBase = (import.meta.env.VITE_API_BASE as string | undefined) ?? '/api/v1';
  try {
    return new URL(envBase).origin;
  } catch {
    return window.location.origin;
  }
}

function Portal() {
  const apiOrigin = getApiOrigin();
  const executiveUrl = (import.meta.env.VITE_EXECUTIVE_URL as string | undefined) ?? `${apiOrigin}/executive-dashboard`;
  const supervisorUrl = (import.meta.env.VITE_SUPERVISOR_URL as string | undefined) ?? `${apiOrigin}/supervisor-dashboard`;
  const docsUrl = (import.meta.env.VITE_DOCS_URL as string | undefined) ?? `${apiOrigin}/docs`;

  return (
    <main style={styles.page}>
      <section style={styles.headerCard}>
        <h1 style={styles.h1}>Portal de Herramientas Urbani</h1>
        <p style={styles.muted}>Accesos rapidos a kiosko, dashboards y utilidades operativas.</p>
      </section>

      <section style={styles.grid}>
        <article style={styles.card}>
          <h3 style={styles.h3}>Kiosko</h3>
          <p style={styles.muted}>Flujo de cliente para tomar numero y perfilado.</p>
          <a href="/?view=kiosk" target="_blank" rel="noreferrer" style={{ ...styles.btn, ...styles.btnPrimary }}>
            Abrir Kiosko
          </a>
        </article>

        <article style={styles.card}>
          <h3 style={styles.h3}>Dashboard Ejecutivo</h3>
          <p style={styles.muted}>Llamar siguiente, iniciar/finalizar y transferencias.</p>
          <a href={executiveUrl} target="_blank" rel="noreferrer" style={{ ...styles.btn, ...styles.btnSecondary }}>
            Abrir Ejecutivo
          </a>
        </article>

        <article style={styles.card}>
          <h3 style={styles.h3}>Dashboard Supervisor</h3>
          <p style={styles.muted}>Metricas globales, prioridad, transferencias y busqueda por RUT.</p>
          <a href={supervisorUrl} target="_blank" rel="noreferrer" style={{ ...styles.btn, ...styles.btnSecondary }}>
            Abrir Supervisor
          </a>
        </article>

        <article style={styles.card}>
          <h3 style={styles.h3}>API / Documentacion</h3>
          <p style={styles.muted}>Explora endpoints y prueba operaciones en Swagger.</p>
          <a href={docsUrl} target="_blank" rel="noreferrer" style={{ ...styles.btn, ...styles.btnGhost }}>
            Abrir API Docs
          </a>
        </article>
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    padding: '24px',
    color: '#e7eefc',
    background:
      'radial-gradient(circle at 10% 10%, #1d2f53 0%, #0d1320 42%, #090e16 100%)',
    fontFamily: '"Segoe UI", sans-serif',
  },
  headerCard: {
    maxWidth: 980,
    margin: '0 auto 14px auto',
    borderRadius: 16,
    border: '1px solid #263651',
    padding: 16,
    background: 'linear-gradient(180deg,#111a2a,#141d30)',
  },
  h1: { margin: 0, fontSize: 38 },
  h3: { margin: 0, fontSize: 28 },
  muted: { color: '#9fb2d3', margin: '6px 0 0 0' },
  grid: {
    maxWidth: 980,
    margin: '0 auto',
    display: 'grid',
    gridTemplateColumns: 'repeat(2,minmax(0,1fr))',
    gap: 12,
  },
  card: {
    borderRadius: 16,
    border: '1px solid #263651',
    padding: 16,
    background: 'linear-gradient(180deg,#111a2a,#141d30)',
    display: 'grid',
    gap: 10,
  },
  btn: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
    padding: '0 16px',
    borderRadius: 10,
    border: 'none',
    fontWeight: 700,
    textDecoration: 'none',
  },
  btnPrimary: { background: '#69cc25', color: '#0b1a07' },
  btnSecondary: { background: '#3a9ee8', color: '#081523' },
  btnGhost: { background: 'transparent', border: '1px solid #263651', color: '#e7eefc' },
};

export default function App() {
  const search = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const view = search?.get('view');

  if (view === 'kiosk') {
    return <KioskScreen />;
  }
  return <Portal />;
}
