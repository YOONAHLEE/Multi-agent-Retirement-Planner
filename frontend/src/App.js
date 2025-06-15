import './App.css';
import MarketCard from './MarketCard';

function App() {
  return (
    <div style={{ display: "flex", gap: 24, background: "#101014", padding: 32, minHeight: "100vh" }}>
      <MarketCard symbol="^KS11" label="KOSPI" />
      <MarketCard symbol="^KQ11" label="KOSDAQ" />
      <MarketCard symbol="^IXIC" label="NASDAQ" />
    </div>
  );
}

export default App;
