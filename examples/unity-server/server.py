import asyncio
import websockets
import cv2
import numpy as np
from ultralytics import YOLO
from securityagents import SecurityModel, DroneAgent

parameters = {'steps': 20}
security_model = SecurityModel(parameters)

model = YOLO('best_2.0.pt')

async def process_message(message, websocket):
    nparr = np.frombuffer(message, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    for agent in security_model.agents:
        if isinstance(agent, DroneAgent):
            agent.see(img, coordinator=security_model.coordinator())  # Handle coordinator or threat detection

    # Process the image using YOLOv8 model
    results = model.track(img, persist=True)
    annotated_frame = results[0].plot()

    # Encode the frame back to bytes to send to the client
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    await websocket.send(buffer.tobytes())

    # Optionally display the image
    cv2.imshow('YOLOv8 Tracking', annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return False
    return True

async def handle_websocket(websocket):
    try:
        async for message in websocket:
            # Check if the message is binary data
            if isinstance(message, bytes):
                # Process the binary data
                if not await process_message(message, websocket):
                    break
            else:
                print("Received a non-binary message")
    except Exception as e:
        print(f"An error occurred: {e}")

async def process_message(message, websocket):
    try:
        # Convert the message to a numpy array
        nparr = np.frombuffer(message, np.uint8)
        # Process the numpy array as needed
        # For example, save or analyze the data
        return True
    except Exception as e:
        print(f"An error occurred while processing the message: {e}")
        return False

async def main():
    async with websockets.serve(handle_websocket, "127.0.0.1", 8000):
        print("WebSocket Server Started")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
