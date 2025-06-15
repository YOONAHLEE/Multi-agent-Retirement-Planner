import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';
import Sidebar from './Sidebar';

const CHAT_API_URL = 'http://localhost:8000/api/chat';
const NEWS_API_URL = 'http://localhost:8000/news';

function Chatbot() {
    const [messages, setMessages] = useState([
        { sender: 'bot', text: '안녕하세요! 무엇을 도와드릴까요?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [news, setNews] = useState([]);
    const [expanded, setExpanded] = useState(null); // 'news' | 'stock' | null
    const messagesEndRef = useRef(null);
    const [session, setSession] = useState(null); // { session_id, user_id, started_at }
    const [sessions, setSessions] = useState([]); // 세션 목록

    useEffect(() => {
        fetch(NEWS_API_URL)
            .then(res => res.json())
            .then(data => setNews(data.news || []))
            .catch(() => setNews([]));
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userMessage = { sender: 'user', text: input };
        setMessages((msgs) => [...msgs, userMessage]);
        setInput('');
        setLoading(true);
        try {
            const response = await fetch(CHAT_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input })
            });
            const data = await response.json();
            setMessages((msgs) => [...msgs, { sender: 'bot', text: data.response }]);
        } catch (e) {
            setMessages((msgs) => [...msgs, { sender: 'bot', text: '오류가 발생했습니다.' }]);
        }
        setLoading(false);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    };

    // 새 세션 생성 시 목록에 추가
    const handleNewSession = (newSession) => {
        setSession(newSession);
        setSessions(prev => [newSession, ...prev]);
    };

    return (
        <div style={{ display: 'flex', minHeight: '100vh', background: 'linear-gradient(120deg, #181A20 60%, #f7f8fa 100%)' }}>
            <Sidebar onNewSession={handleNewSession} sessions={sessions} />
            <main style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0', gap: '32px' }}>
                <div className="chatbot-container" style={{ height: '80vh', maxWidth: '900px', width: '100%' }}>
                    <div className="chatbot-header">퇴직연금 Agent</div>
                    <div className="chatbot-messages">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`chatbot-message ${msg.sender}`}>
                                {msg.text}
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                    <div className="chatbot-input-area">
                        <input
                            type="text"
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="메시지를 입력하세요..."
                            disabled={loading}
                        />
                        <button onClick={sendMessage} disabled={loading || !input.trim()}>
                            {loading ? '전송 중...' : '전송'}
                        </button>
                    </div>
                </div>
                <div className="right-widgets" style={{ display: 'flex', flexDirection: 'column', gap: '24px', height: '80vh', minWidth: '340px', maxWidth: '400px', width: '100%' }}>
                    <div className="news-widget" style={{ background: '#23272f', color: '#fff', borderRadius: '16px', boxShadow: '0 4px 24px rgba(0,0,0,0.10)', padding: '24px', flex: 1, minHeight: '200px', overflowY: 'auto', cursor: 'pointer' }}
                        onClick={() => setExpanded('news')} title="클릭 시 확대">
                        <h3 style={{ margin: '0 0 12px 0', fontSize: '1.1rem', color: '#29a6e3' }}>최신 뉴스</h3>
                        <ul style={{ padding: 0, margin: 0, listStyle: 'none' }}>
                            {news.length === 0
                                ? <li>뉴스를 불러오는 중...</li>
                                : news.slice(0, 3).map((item, idx) => <li key={idx}>• {item.title}</li>)}
                        </ul>
                    </div>
                </div>
                {/* 오버레이 모달 */}
                {expanded && (
                    <div className="overlay-modal" onClick={() => setExpanded(null)}>
                        <div className="overlay-content" onClick={e => e.stopPropagation()}>
                            <button className="close-btn" onClick={() => setExpanded(null)}>닫기</button>
                            {expanded === 'news' ? (
                                <div>
                                    <h2 style={{ color: '#29a6e3', marginTop: 0 }}>최신 뉴스</h2>
                                    <ul style={{ padding: 0, margin: 0, listStyle: 'none' }}>
                                        {news.length === 0
                                            ? <li>뉴스를 불러오는 중...</li>
                                            : news.map((item, idx) => <li key={idx} style={{ marginBottom: 10 }}>• {item.title}</li>)}
                                    </ul>
                                </div>
                            ) : (
                                <div>
                                    <h2 style={{ color: '#29a6e3', marginTop: 0 }}>주식 그래프</h2>
                                    <div style={{ width: '100%', height: '320px', background: '#181A20', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#b0bec5', fontSize: '1.2rem' }}>
                                        (확대된 그래프 영역 예시)
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default Chatbot; 