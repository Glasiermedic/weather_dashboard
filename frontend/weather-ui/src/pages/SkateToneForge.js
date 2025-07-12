function SkateToneForge() {
  return (
    <div style={{ textAlign: 'center' }}>
      <h1>SkateTone Forge</h1>
      <p>🎵🛹 Hang tight! This musical skatepark is under construction.</p>
      <div style={{ marginTop: '2rem' }}>
        <div style={{
          width: '2rem',
          height: '2rem',
          border: '4px solid #ccc',
          borderTop: '4px solid #000',
          borderRadius: '50%',
          margin: 'auto',
          animation: 'spin 1s linear infinite'
        }}></div>
      </div>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default SkateToneForge;
