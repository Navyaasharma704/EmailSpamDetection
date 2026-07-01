import "./App.css";
import { useState } from "react";
import axios from "axios";

function App() {

  const [email, setEmail] = useState("");
  const [result, setResult] = useState("");

  const detectSpam = async () => {

    try {

      const response = await axios.post(
        "http://127.0.0.1:5000/predict",
        {
          email: email
        }
      );

      setResult(response.data.result);

    } catch (error) {

      console.log(error);
      setResult("Server Error");

    }

  };


  return (
    <div className="container">

      <h1>Email Spam Detection using Machine Learning</h1>

      <p className="subtitle">
        Detect whether an email is Spam or Not Spam
      </p>


      <textarea
        rows="12"
        placeholder="Paste your email here..."
        value={email}
        onChange={(e)=>setEmail(e.target.value)}
      ></textarea>


      <button onClick={detectSpam}>
        Detect Spam
      </button>


      {
        result && 
        <h2>
          Result: {result}
        </h2>
      }


    </div>
  );
}

export default App;