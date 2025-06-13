import React, { useState } from 'react';
import './Sidebar.css';
import { FaBars, FaPlus, FaCommentDots } from 'react-icons/fa';

const chatHistory = [
    { id: 1, title: '최근 채팅 1' },
    { id: 2, title: '최근 채팅 2' },
    { id: 3, title: '최근 채팅 3' },
    { id: 4, title: '최근 채팅 4' },
    { id: 5, title: '최근 채팅 5' },
];

function Sidebar() {
    const [open, setOpen] = useState(true);

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
            <button className="sidebar-newchat">
                <FaPlus /> 새 채팅
            </button>
            <div className="sidebar-history">
                <div className="sidebar-history-title">최근 채팅</div>
                <ul>
                    {chatHistory.map(chat => (
                        <li key={chat.id} className="sidebar-history-item">
                            <FaCommentDots style={{ marginRight: 8 }} />
                            <span>{chat.title}</span>
                        </li>
                    ))}
                </ul>
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