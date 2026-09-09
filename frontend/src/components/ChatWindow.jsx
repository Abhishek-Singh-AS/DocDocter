import { useState } from "react";
import { askQuestion } from "../api/client";

function ChatWindow({ messages, setMessages }) {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [expandedSourcesIndex, setExpandedSourcesIndex] = useState(null);

  async function handleAsk() {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || isLoading) return;

    setIsLoading(true);
    setErrorMessage("");

    try {
      const data = await askQuestion(trimmedQuestion);
      setMessages((prev) => [
        { question: trimmedQuestion, ...data },
        ...prev,
      ]);
      setQuestion("");
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleAsk();
    }
  }

  return (
    <div>
      <h2 className="section-heading">Ask Something</h2>

      <div style={{ display: "flex", gap: "10px", marginBottom: "16px" }}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your uploaded documents..."
          style={{
            flex: 1,
            padding: "12px 14px",
            borderRadius: "8px",
            border: "1px solid #262e52",
            background: "#1a2140",
            color: "#e7e9f5",
            fontSize: "0.95rem",
          }}
        />
        <button
          className="primary-button"
          onClick={handleAsk}
          disabled={!question.trim() || isLoading}
        >
          {isLoading ? "Thinking..." : "Ask"}
        </button>
      </div>

      {errorMessage && (
        <div className="card" style={{ marginBottom: "16px", borderColor: "#f43f5e" }}>
          <strong style={{ color: "#f43f5e" }}>⚠️ {errorMessage}</strong>
        </div>
      )}

      {messages.length === 0 && !isLoading && (
        <p style={{ color: "#6b7280" }}>No questions asked yet — try one above.</p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
        {messages.map((msg, index) => (
          <div key={index} className="card">
            <p style={{ margin: 0, fontWeight: 600, color: "#f43f5e" }}>
              You asked: {msg.question}
            </p>
            <p style={{ margin: "10px 0" }}>{msg.answer}</p>

            {msg.sources && msg.sources.length > 0 && (
              <div>
                <button
                  onClick={() =>
                    setExpandedSourcesIndex(expandedSourcesIndex === index ? null : index)
                  }
                  style={{
                    background: "none",
                    border: "none",
                    color: "#38bdf8",
                    cursor: "pointer",
                    fontSize: "0.85rem",
                    padding: 0,
                  }}
                >
                  {expandedSourcesIndex === index ? "▲ Hide sources" : "▼ Show sources"}
                </button>

                {expandedSourcesIndex === index && (
                  <div style={{ marginTop: "10px" }}>
                    {msg.sources.map((src, i) => (
                      <div key={i} style={{ color: "#9ca3af", fontSize: "0.85rem" }}>
                        📎 {src}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChatWindow;