export function HeroHeader() {
  return (
    <header className="hero">
      <div className="hero-glow" />
      <div className="hero-content">
        <h1>InsightAI</h1>
        <p className="subtitle">Analizá tus ventas con IA · datos reales en 3D</p>
        <div className="hero-badges">
          <span className="badge">PostgreSQL</span>
          <span className="badge">Groq LLM</span>
          <span className="badge">Tool calling</span>
          <span className="badge">Three.js</span>
        </div>
      </div>
    </header>
  );
}
