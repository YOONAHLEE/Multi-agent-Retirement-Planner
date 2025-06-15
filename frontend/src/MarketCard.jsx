import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import axios from 'axios';

export default function MarketCard({ symbol, label }) {
    const [data, setData] = useState(null);

    useEffect(() => {
        axios.get(`http://localhost:8000/market-index/${symbol}`).then(res => {
            setData(res.data);
        });
    }, [symbol]);

    if (!data) return <div className="card">Loading...</div>;

    return (
        <div className="card" style={{ background: "#181A20", color: "#fff", borderRadius: 16, padding: 24, minWidth: 300 }}>
            <div style={{ fontSize: 18, fontWeight: 600 }}>{label}</div>
            <div style={{ fontSize: 28, fontWeight: 700, margin: "8px 0" }}>
                {data.price ? `$${data.price.toLocaleString()}` : "-"}
                <span style={{ fontSize: 16, marginLeft: 8, color: data.change > 0 ? "#4caf50" : "#e53935" }}>
                    {data.change > 0 ? "+" : ""}{data.change?.toFixed(2)} ({data.percent?.toFixed(2)}%)
                </span>
            </div>
            <Line
                data={{
                    labels: data.timestamps,
                    datasets: [
                        {
                            data: data.history,
                            borderColor: "#29a6e3",
                            backgroundColor: "rgba(41,166,227,0.1)",
                            tension: 0.3,
                            pointRadius: 0,
                        },
                    ],
                }}
                options={{
                    plugins: { legend: { display: false } },
                    scales: { x: { display: false }, y: { display: false } },
                }}
                height={60}
            />
        </div>
    );
} 