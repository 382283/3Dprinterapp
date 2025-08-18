from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json
from datetime import datetime

class ConnectionManager:
    """
    WebSocket接続を管理するクラス
    接続中のクライアントを保持し、全クライアントへの通知を担当
    """

    def __init__(self):
        #接続中のクライアントを保持するリスト
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        """
        新しいWebSocket接続を受け入れる
        """
        
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"クライアントが接続しました。現在の接続数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        WebSocket接続を切断する
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"クライアントが切断されました。現在の接続数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        特定のクライアントメッセージを送信
        """
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """
        接続中の全クライアントにメッセージを送信
        """
        #切断された接続を解除
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        for connection in disconnected:
            self.active_connections.remove(connection)
        
        print(f"全クライアント({len(self.active_connections)}件)にメッセージを送信しました")

#グローバルな接続マネージャーインスタンスを作成
manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocketエンドポイントのメイン処理
    クライアントとの接続・切断・メッセージ受信を処理
    """
    
    await manager.connect(websocket)
    try:
        while True:
            #クライアントからのメッセージを受信（現在は使用しないが、将来の拡張用)
            data = await websocket.receive_text()
            #必要に応じてクライアントからのメッセージを処理
            print(f"クライアントからメッセージを受信: {data}")
    except WebSocketDisconnect:
        #クライアントが切断した場合
        manager.disconnect(websocket)

async def notify_new_order(order_data: dict):
    """
    新規依頼制作時に全クライアントに通知する関数
    order_data: 新規依頼された依頼データ
    """
    notification = {
        "type": "new_order",
        "data": order_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast(json.dumps(notification, ensure_ascii=False))

async def notify_order_update(order_data: dict):
    """
    進捗更新時に全クライアントに通知する関数
    order_data:  更新された依頼データ
    """
    # 通知用のJSONメッセージを作成
    notification = {
        "type": "order_update",
        "data": order_data,
        "timestamp": datetime.now().isoformat()
    }

    #JSON文字列に変換して全クライアントに送信
    await manager.broadcast(json.dumps(notification, ensure_ascii=False))