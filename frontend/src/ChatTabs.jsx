import React, { useState } from 'react';
import './ChatTabs.css';

const TABS = [
    { key: 'html', label: 'HTML' },
    { key: 'css', label: 'CSS' },
    { key: 'js', label: 'JS' },
];

function ChatTabs() {
    const [activeTab, setActiveTab] = useState('html');

    return (
        <div className="chat-tabs-container">
            <div className="chat-tabs">
                {TABS.map(tab => (
                    <button
                        key={tab.key}
                        className={`chat-tab${activeTab === tab.key ? ' active' : ''}`}
                        onClick={() => setActiveTab(tab.key)}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>
            <div className="chat-tab-empty">
                이 탭은 현재 비어 있습니다.
            </div>
        </div>
    );
}

export default ChatTabs; 