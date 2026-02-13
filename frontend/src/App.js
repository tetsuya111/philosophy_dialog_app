import React, { useState } from 'react';
import axios from 'axios';
import JitsiMeeting from './components/JitsiMeeting';
import RoomList from './components/RoomList';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/webrtc';

function App() {
  const [currentRoom, setCurrentRoom] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const createAndJoinRoom = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/rooms/create/`);
      const roomData = response.data;
      setCurrentRoom(roomData);
    } catch (err) {
      setError('ルームの作成に失敗しました。');
      console.error('Error creating room:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const joinRoom = async (roomId) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/rooms/${roomId}/join/`);
      const roomData = response.data;
      setCurrentRoom(roomData);
    } catch (err) {
      setError('ルームへの参加に失敗しました。');
      console.error('Error joining room:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const leaveRoom = () => {
    setCurrentRoom(null);
    setError(null);
  };

  if (currentRoom) {
    return (
      <div className="app">
        <JitsiMeeting
          roomName={currentRoom.room_name}
          roomId={currentRoom.room_id}
          domain={currentRoom.jitsi_domain || 'meet.jit.si'}
          onLeave={leaveRoom}
        />
      </div>
    );
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1 className="title">🎥 WebRTC Video Conference</h1>
          <p className="subtitle">最大4人でビデオ通話ができます</p>
        </header>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="actions">
          <button
            className="btn btn-primary"
            onClick={createAndJoinRoom}
            disabled={isLoading}
          >
            {isLoading ? '作成中...' : '🚀 新しいルームを作成して参加'}
          </button>
        </div>

        <div className="divider">
          <span>または</span>
        </div>

        <RoomList onJoinRoom={joinRoom} apiBaseUrl={API_BASE_URL} />
      </div>
    </div>
  );
}

export default App;
