import React, { useState } from "react";

export default function Calculator() {
  const [overallPercent, setOverallPercent] = useState("");
  const [totalLectures, setTotalLectures] = useState("");
  const [targetPercent, setTargetPercent] = useState(75);
  const [remainingWeeks, setRemainingWeeks] = useState("");
  const [file, setFile] = useState(null);
  const [timetable, setTimetable] = useState({});
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [extractedText, setExtractedText] = useState("");
  const [confidence, setConfidence] = useState(null);

  const uploadFile = async () => {
    if (!file) {
      setError("Please select a timetable image");
      return;
    }
    
    setLoading(true);
    setError("");
    setExtractedText("");
    setConfidence(null);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/upload_timetable", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      
      if (data.timetable) {
        setTimetable(data.timetable);
        setExtractedText(data.extracted_text || "");
        setConfidence(data.confidence || null);
        setError("");
      } else {
        setError(data.error || "Failed to extract timetable");
        setExtractedText(data.extracted_text || "");
      }
    } catch (err) {
      setError("Network error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const parseTableText = async () => {
    if (!extractedText) {
      setError("No extracted text to parse");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const response = await fetch("http://localhost:5000/parse_table", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: extractedText,
        }),
      });

      const data = await response.json();
      
      if (data.timetable) {
        setTimetable(data.timetable);
        setError("");
      } else {
        setError(data.error || "Failed to parse table");
      }
    } catch (err) {
      setError("Network error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculate = async () => {
    const response = await fetch("http://localhost:5000/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        overallPercent,
        totalLectures,
        targetPercent,
        remainingWeeks,
        timetable,
      }),
    });

    const data = await response.json();
    setResults(data.results || {});
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Attendance Calculator with Timetable Upload</h2>

      <input
        type="number"
        placeholder="Overall Attendance (%)"
        value={overallPercent}
        onChange={(e) => setOverallPercent(e.target.value)}
      />
      <br />

      <input
        type="number"
        placeholder="Total Lectures Conducted"
        value={totalLectures}
        onChange={(e) => setTotalLectures(e.target.value)}
      />
      <br />

      <input
        type="number"
        placeholder="Target Attendance (%)"
        value={targetPercent}
        onChange={(e) => setTargetPercent(e.target.value)}
      />
      <br />

      <input
        type="number"
        placeholder="Remaining Weeks"
        value={remainingWeeks}
        onChange={(e) => setRemainingWeeks(e.target.value)}
      />
      <br />

      <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={uploadFile} disabled={loading}>
        {loading ? "Processing..." : "Upload Timetable"}
      </button>

      {error && (
        <div style={{ color: "red", margin: "10px 0", padding: "10px", border: "1px solid red", borderRadius: "4px" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {confidence !== null && (
        <div style={{ color: "green", margin: "10px 0" }}>
          <strong>OCR Confidence:</strong> {confidence}%
        </div>
      )}

      {extractedText && (
        <div style={{ margin: "10px 0" }}>
          <h4>Extracted Text (Raw OCR):</h4>
          <pre style={{ background: "#f5f5f5", padding: "10px", borderRadius: "4px", fontSize: "12px", maxHeight: "200px", overflow: "auto" }}>
            {extractedText}
          </pre>
          <button 
            onClick={parseTableText} 
            style={{ marginTop: "10px", padding: "8px 16px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Parse as Table
          </button>
        </div>
      )}

      <h3>Extracted Timetable:</h3>
      <pre>{JSON.stringify(timetable, null, 2)}</pre>

      <button onClick={calculate}>Calculate</button>

      <h3>Results:</h3>
      {Object.keys(results).length > 0 &&
        Object.entries(results).map(([subject, result], index) => (
          <p key={index}><b>{subject}:</b> {result}</p>
        ))}
    </div>
  );
}
