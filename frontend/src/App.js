import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [lines, setLines] = useState([]);
  const [tables, setTables] = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await axios.post("http://localhost:5000/extract", formData);
    setLines(res.data.lines);
    setTables(res.data.tables || []);
  };

  const askQuestion = async () => {
    const res = await axios.post("http://localhost:5000/ask", { question });
    setAnswer(res.data.answer);
  };

  return (
    <div className="container">
      <div className="left-pane">
        <h2>Textract App</h2>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={uploadFile}>Upload</button>

        <h3>Extracted Text:</h3>
        <div className="extracted-box">
          {lines.map((line, idx) => (
            <div className="text-block" key={idx}>{line}</div>
          ))}

          {tables.map((table, tableIdx) => (
            <table className="table-block" key={tableIdx}>
              <tbody>
                {table.map((row, rowIdx) => (
                  <tr key={rowIdx}>
                    {row.map((cell, colIdx) => (
                      <td key={colIdx}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ))}
        </div>
      </div>

      <div className="right-pane">
        <h3>Ask a Question</h3>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask something about the document..."
        />
        <button onClick={askQuestion}>Submit</button>
        <div className="answer-box">
          <strong>Answer:</strong>
          <ReactMarkdown
            components={{
              table: ({ node, ...props }) => (
                <table className="markdown-table" {...props} />
              ),
              th: ({ node, ...props }) => <th {...props} />,
              td: ({ node, ...props }) => <td {...props} />,
            }}
          >
            {answer}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

export default App;