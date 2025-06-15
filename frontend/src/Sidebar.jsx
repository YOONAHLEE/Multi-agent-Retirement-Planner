import React, { useState } from 'react';
import './Sidebar.css';
import { FaBars, FaPlus, FaCommentDots } from 'react-icons/fa';

function Sidebar({ onNewSession, sessions }) {
    const [open, setOpen] = useState(true);

    const handleNewChat = async () => {
        try {
            const res = await fetch('http://localhost:8000/retirement/sessions', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
            });
            const data = await res.json();
            if (onNewSession) onNewSession(data);
        } catch (e) {
            alert('새 채팅 세션 생성에 실패했습니다.');
        }
    };

    if (!open) {
        return (
            <aside className="sidebar sidebar-closed">
                <button className="sidebar-toggle" onClick={() => setOpen(true)} title="사이드바 열기">
                    <FaBars size={22} />
                </button>
            </aside>
        );
    }

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <button className="sidebar-toggle" onClick={() => setOpen(false)} title="사이드바 닫기">
                    <FaBars size={22} />
                </button>
                <span className="sidebar-logo">퇴직연금<br />분석 서비스</span>
            </div>
            <button className="sidebar-newchat" onClick={handleNewChat}>
                <FaPlus /> 새 채팅
            </button>
            <div className="sidebar-session-list">
                {sessions && sessions.length > 0 && sessions.map(session => (
                    <div key={session.session_id} className="sidebar-history-item">
                        <FaCommentDots style={{ marginRight: 8 }} />
                        <span>{session.session_id.slice(0, 8)}</span>
                    </div>
                ))}
            </div>
            <div className="sidebar-footer">
                <div className="sidebar-makers-title">만든 사람</div>
                <div className="sidebar-makers-list">
                    <span>김현규</span>, <span>이윤아</span><br />
                    <span>조수현</span>, <span>김태한</span>
                </div>
            </div>
        </aside>
    );
}

export default Sidebar; 