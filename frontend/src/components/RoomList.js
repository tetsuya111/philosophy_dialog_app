import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './RoomList.css';

const RoomList = ({ onJoinRoom, apiBaseUrl }) => {
  const [rooms, setRooms] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRooms = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${apiBaseUrl}/rooms/`);
      setRooms(response.data.rooms || []);
    } catch (err) {
      setError('ルーム一覧の取得に失敗しました。');
      console.error('Error fetching rooms:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRooms();
  }, []);

  const handleJoinRoom = (roomId) => {
    onJoinRoom(roomId);
  };

  return (
    <div className="room-list">
      <div className="room-list-header">
        <h3>既存のルームに参加</h3>
        <button className="refresh-btn" onClick={fetchRooms} disabled={isLoading}>
          {isLoading ? '更新中...' : '🔄 更新'}
        </button>
      </div>

      {error && <div className="error-text">{error}</div>}

      {isLoading ? (
        <div className="loading">読み込み中...</div>
      ) : rooms.length === 0 ? (
        <div className="empty-message">
          現在利用可能なルームはありません
        </div>
      ) : (
        <div className="rooms-grid">
          {rooms.map((room) => (
            <div key={room.room_id} className="room-card">
              <div className="room-info">
                <h4 className="room-name">{room.room_name}</h4>
                <div className="room-details">
                  <span className="participant-count">
                    👥 {room.participants_count}/{room.max_participants}
                  </span>
                  <span className={`status ${room.is_active ? 'active' : 'inactive'}`}>
                    {room.is_active ? '● アクティブ' : '○ 非アクティブ'}
                  </span>
                </div>
              </div>
              <button
                className="join-btn"
                onClick={() => handleJoinRoom(room.room_id)}
                disabled={room.participants_count >= room.max_participants}
              >
                {room.participants_count >= room.max_participants ? '満室' : '参加'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RoomList;
