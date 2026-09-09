import { useState } from "react";
import "./App.css";
import UploadPanel from "./components/UploadPanel";
import ChatWindow from "./components/ChatWindow";
import EvalDashboard from "./components/EvalDashboard";

function App() {
  const [activeTab, setActiveTab] = useState("upload");
  const [messages, setMessages] = useState([]);

  return (
    <>
      <div className="background-blobs">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>

      <div className="app-container">
        <div className="app-header">
          <span className="app-logo">🕸️</span>
          <h1 className="app-title">DocSpider</h1>
        </div>
        <p className="app-subtitle">
          Upload your documents, then ask them anything — answers come straight from your own files.
        </p>

        <div className="tab-bar">
          <button
            className={`tab-button ${activeTab === "upload" ? "active" : ""}`}
            onClick={() => setActiveTab("upload")}
          >
            📥 Upload
          </button>
          <button
            className={`tab-button ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            💬 Ask
          </button>
          <button
            className={`tab-button ${activeTab === "eval" ? "active" : ""}`}
            onClick={() => setActiveTab("eval")}
          >
            📊 Quality Check
          </button>
        </div>

        <div className="tab-content">
          {activeTab === "upload" && <UploadPanel onDocumentReplaced={() => setMessages([])} />}
          {activeTab === "chat" && <ChatWindow messages={messages} setMessages={setMessages} />}
          {activeTab === "eval" && <EvalDashboard messages={messages} />}
        </div>
      </div>
    </>
  );
}

export default App;