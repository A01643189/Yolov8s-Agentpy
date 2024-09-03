using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

public class WebSocketClient : MonoBehaviour
{
    private ClientWebSocket webSocket;

    async void Start()
    {
        webSocket = new ClientWebSocket();
        await webSocket.ConnectAsync(new Uri("ws://127.0.0.1:8000"), CancellationToken.None);

        // Example of sending an image as binary data
        Texture2D tex = GetCameraImage();  // Assume this captures your camera image
        byte[] imageBytes = tex.EncodeToJPG();
        await SendMessage(imageBytes);

        // Receiving the processed image
        await ReceiveMessage();
    }

    private async Task SendMessage(byte[] message)
    {
        var arraySegment = new ArraySegment<byte>(message);
        await webSocket.SendAsync(arraySegment, WebSocketMessageType.Binary, true, CancellationToken.None);
    }

    private async Task ReceiveMessage()
    {
        var buffer = new byte[1024 * 1024];  // 1MB buffer size
        var arraySegment = new ArraySegment<byte>(buffer);
        var result = await webSocket.ReceiveAsync(arraySegment, CancellationToken.None);

        if (result.MessageType == WebSocketMessageType.Binary)
        {
            // Handle received image data
            Texture2D tex = new Texture2D(2, 2);
            tex.LoadImage(buffer, true);
            // Optionally display or process the received image
            Debug.Log("Received image from server");
        }
    }

    private Texture2D GetCameraImage()
    {
        // Implement this method to capture and return the current camera image as Texture2D
        return new Texture2D(2, 2);  // Replace with actual image capture code
    }

    private async void OnApplicationQuit()
    {
        await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
        webSocket.Dispose();
    }
}
