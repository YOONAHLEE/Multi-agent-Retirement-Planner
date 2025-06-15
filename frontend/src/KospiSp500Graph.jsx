import React, { useEffect, useState } from "react";

function KospiSp500Graph() {
    const [imgBase64, setImgBase64] = useState("");

    useEffect(() => {
        fetch("http://localhost:8000/graph/kospi_sp500")
            .then(res => res.json())
            .then(data => setImgBase64(data.image_base64));
    }, []);

    return (
        <div style={{ position: "absolute", right: 20, bottom: 20, width: 400, zIndex: 100 }}>
            {imgBase64 && (
                <img
                    src={`data:image/png;base64,${imgBase64}`}
                    alt="KOSPI vs S&P500"
                    style={{ width: "100%", borderRadius: 8, boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}
                />
            )}
        </div>
    );
}

export default KospiSp500Graph; 