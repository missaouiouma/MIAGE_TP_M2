import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { getUserMessages, askQuestion, getUserSessions } from "../api/api";

const ChatbotPage = () => {
  const location = useLocation();
  const userId = location.state?.userId; // Récupérer l'ID utilisateur depuis la navigation

  const [sessions, setSessions] = useState([]); // Liste des sessions
  const [selectedSession, setSelectedSession] = useState(null); // Session sélectionnée
  const [messages, setMessages] = useState([]); // Messages de la session sélectionnée
  const [input, setInput] = useState(""); // Input utilisateur

  // Charger les sessions au montage
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await getUserSessions(userId); // API pour récupérer les sessions
        setSessions(res.data); // Mettre à jour les sessions
        if (res.data.length > 0) {
          setSelectedSession(res.data[0]); // Sélectionner la première session par défaut
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des sessions :", error);
      }
    };

    if (userId) {
      fetchSessions(); // Charger les sessions si l'utilisateur est connecté
    }
  }, [userId]);

  // Charger les messages pour la session sélectionnée
  useEffect(() => {
    const fetchMessages = async () => {
      if (selectedSession) {
        try {
          const res = await getUserMessages(userId, selectedSession.session_id); // API pour récupérer les messages de la session
          setMessages(res.data); // Mettre à jour les messages de la session
        } catch (error) {
          console.error("Erreur lors de la récupération des messages :", error);
        }
      } else {
        setMessages([]); // Réinitialiser les messages si aucune session n'est sélectionnée
      }
    };

    fetchMessages();
  }, [selectedSession, userId]);

  // Envoyer un message
  const sendMessage = async () => {
    if (input.trim()) {
      const userMessage = { role: "user", content: input };
      setMessages((prevMessages) => [...prevMessages, userMessage]); // Ajouter le message utilisateur localement

      try {
        const res = await askQuestion({ user_id: userId, question: input }); // Appel API pour obtenir la réponse
        const botResponse = { role: "assistant", content: res.data.response };
        setMessages((prevMessages) => [...prevMessages, botResponse]); // Ajouter la réponse de l'assistant
      } catch (error) {
        console.error("Erreur lors de l'appel à l'API :", error);
        const errorResponse = {
          role: "assistant",
          content: "Erreur : impossible de récupérer une réponse.",
        };
        setMessages((prevMessages) => [...prevMessages, errorResponse]); // Ajouter une erreur comme réponse
      }

      setInput(""); // Réinitialiser le champ d'entrée
    }
  };

  if (!userId) {
    return <p style={{ color: "red" }}>Erreur : Aucun utilisateur connecté.</p>;
  }

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "Arial, sans-serif" }}>
      {/* Sidebar pour les sessions */}
      <div
        style={{
          width: "25%",
          borderRight: "1px solid #ccc",
          padding: "10px",
          backgroundColor: "#f7f7f7",
        }}
      >
        <h3>Vos sessions</h3>
        <ul style={{ listStyleType: "none", padding: 0 }}>
          {sessions.map((session) => (
            <li
              key={session.session_id}
              onClick={() => setSelectedSession(session)} // Changer de session sélectionnée
              style={{
                padding: "10px",
                cursor: "pointer",
                backgroundColor:
                  selectedSession?.session_id === session.session_id
                    ? "#0077b6"
                    : "transparent",
                color: selectedSession?.session_id === session.session_id ? "#fff" : "#000",
                borderRadius: "5px",
                marginBottom: "5px",
              }}
            >
              {new Date(session.created_at).toLocaleString()} {/* Date lisible */}
            </li>
          ))}
        </ul>
      </div>

      {/* Zone de chat */}
      <div style={{ flex: "1", padding: "20px" }}>
        <h2 style={{ textAlign: "center", color: "#0077b6" }}>AItravel</h2>
        <div
          style={{
            border: "1px solid #ccc",
            height: "400px",
            overflowY: "scroll",
            padding: "10px",
            borderRadius: "8px",
            backgroundColor: "#f9f9f9",
          }}
        >
          {messages.length === 0 ? (
            <p style={{ textAlign: "center", color: "#aaa" }}>
              Aucun message dans cette session.
            </p>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  textAlign: msg.role === "user" ? "right" : "left",
                  margin: "10px 0",
                }}
              >
                <strong>{msg.role === "user" ? "Vous" : "AItravel"} :</strong>{" "}
                <span
                  style={{
                    display: "inline-block",
                    backgroundColor: msg.role === "user" ? "#0077b6" : "#e0f7fa",
                    color: msg.role === "user" ? "#fff" : "#000",
                    padding: "10px",
                    borderRadius: "12px",
                    maxWidth: "70%",
                    wordWrap: "break-word",
                  }}
                >
                  {msg.content}
                </span>
              </div>
            ))
          )}
        </div>

        {/* Champ d'entrée */}
        <div style={{ marginTop: "10px", display: "flex", alignItems: "center" }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tapez un message..."
            style={{
              flex: "1",
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #ccc",
              marginRight: "10px",
            }}
          />
          <button
            onClick={sendMessage}
            style={{
              backgroundColor: "#0077b6",
              color: "#fff",
              padding: "10px 20px",
              borderRadius: "8px",
              border: "none",
              cursor: "pointer",
            }}
          >
            Envoyer
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotPage;