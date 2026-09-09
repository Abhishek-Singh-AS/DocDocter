import { useState } from "react";
import { ingestFile, resetKnowledgeBase } from "../api/client";

function UploadPanel({ onDocumentReplaced }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [replaceExisting, setReplaceExisting] = useState(true);
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");

  function handleFileChange(event) {
    const file = event.target.files[0];
    setSelectedFile(file || null);
    setStatus("idle");
    setResult(null);
    setErrorMessage("");
  }

  async function handleUpload() {
    if (!selectedFile) return;

    setStatus("uploading");
    setErrorMessage("");

    try {
      // If the user wants a fresh start, clear out old documents
      // BEFORE uploading the new one, so nothing from a previous
      // PDF lingers in Pinecone or shows up in later answers.
      if (replaceExisting) {
  await resetKnowledgeBase();
  onDocumentReplaced();
}

      const data = await ingestFile(selectedFile);
      setResult(data);
      setStatus("success");
    } catch (err) {
      setErrorMessage(err.message);
      setStatus("error");
    }
  }

  return (
    <div>
      <h2 className="section-heading">Add a Document</h2>
      <p style={{ color: "#9ca3af", marginTop: "-8px", marginBottom: "16px" }}>
        Upload a PDF — DocSpider will read it, break it into pieces, and remember it so you can ask questions later.
      </p>

      <div className="card" style={{ marginBottom: "16px" }}>
        <input
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          style={{ color: "#e7e9f5" }}
        />
        <p style={{ color: "#9ca3af", fontSize: "0.85rem", margin: "10px 0 0 0" }}>
          Larger documents (50+ pages) may take a few minutes to process. Please don't close this tab while uploading.
        </p>
      </div>

      <label style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "16px", color: "#e7e9f5", fontSize: "0.9rem" }}>
        <input
          type="checkbox"
          checked={replaceExisting}
          onChange={(e) => setReplaceExisting(e.target.checked)}
        />
        Replace previous document (recommended — keeps answers focused on just this file)
      </label>

      <button
        className="primary-button"
        onClick={handleUpload}
        disabled={!selectedFile || status === "uploading"}
      >
        {status === "uploading" ? "Reading document... this can take a few minutes for larger files" : "Upload & Learn Document"}
      </button>

      {status === "success" && result && (
        <div className="card" style={{ marginTop: "20px", borderColor: "#22c55e" }}>
          <strong style={{ color: "#22c55e" }}>✅ Done!</strong>
          <p style={{ margin: "8px 0 0 0" }}>
            <strong>{result.filename}</strong> is now searchable —
            broken into {result.chunks_added} pieces.
          </p>
          <p style={{ margin: "4px 0 0 0", color: "#9ca3af", fontSize: "0.9rem" }}>
            Total pieces stored: {result.total_vectors_in_store}
          </p>
        </div>
      )}

      {status === "error" && (
        <div className="card" style={{ marginTop: "20px", borderColor: "#f43f5e" }}>
          <strong style={{ color: "#f43f5e" }}>⚠️ Something went wrong</strong>
          <p style={{ margin: "8px 0 0 0" }}>{errorMessage}</p>
        </div>
      )}
    </div>
  );
}

export default UploadPanel;