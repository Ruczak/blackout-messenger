using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Net.WebSockets;
using System.Text;
namespace Emergence;

public partial class MainPage : ContentPage
{
    private ClientWebSocket ws;
    private ObservableCollection<Message> messeges = new ObservableCollection<Message>();

    public static string ServerID;
    public MainPage()
    {
        InitializeComponent();
        messegesListView.ItemsSource = messeges;
    }

    public async void connectClicked(object sender, EventArgs e)
    {
        connectButton.Text = "Connecting...";
        connectButton.IsEnabled = false;

        if (ws == null || ws.State != WebSocketState.Open)
        {
            ws = new ClientWebSocket();

            try
            {
                messeges.Clear();
                await ws.ConnectAsync(new Uri($"ws://{ipEntry.Text}:8080/"), CancellationToken.None);
                statusLabel.Text = "Connected";
                statusLabel.TextColor = Colors.Green;
                connectButton.Text = "Disconnect";
                connectButton.IsEnabled = true;

                while (ws.State == WebSocketState.Open)
                {
                    byte[] buffer = new byte[1024];
                    WebSocketReceiveResult result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
                    string message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);

                    if (result.EndOfMessage)
                    {
                        var receivedMessage = JsonConvert.DeserializeObject<dynamic>(message);

                        if(receivedMessage.MessageType == "ServerID")
                        {
                            ServerID = receivedMessage.content;
                        }
                        else if(receivedMessage.MessageType == "Message")
                        {
                            Message m = new Message {content = receivedMessage.content, time = receivedMessage.time, sender = receivedMessage.sender };
                            messeges.Add(m);
                            messegesListView.ScrollTo(m, animate: true);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                if (ws.State != WebSocketState.Open)
                {
                    statusLabel.Text = "Connection failed: Server is down";
                }
                else
                {
                    statusLabel.Text = "Connection failed: " + ex.Message;
                }
                statusLabel.TextColor = Colors.Red;
                connectButton.IsEnabled = true;
                connectButton.Text = "Connect";
            }
        }
        else
        {
            await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
            statusLabel.Text = "Disconnected";
            statusLabel.TextColor = Colors.Red;
            connectButton.Text = "Connect";
            connectButton.IsEnabled = true;
        }
    }

    public async void disconnectClicked(object sender, EventArgs e)
    {
        if (ws != null && ws.State == WebSocketState.Open)
        {
            await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
            statusLabel.Text = "Disconnected";
            statusLabel.TextColor = Colors.Red;
        }
    }

    protected async override void OnDisappearing()
    {
        if (ws != null && ws.State == WebSocketState.Open)
        {
            await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
            statusLabel.Text = "Disconnected";
            statusLabel.TextColor = Colors.Red;
        }

        base.OnDisappearing();
    }

    private async void sendClicked(Object sender, EventArgs e)
    { 
        if (ws.State == WebSocketState.Open && messegeEntry.Text != "")
        {
            string message = messegeEntry.Text;
            byte[] buffer = Encoding.UTF8.GetBytes(message);
            await ws.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
            messegeEntry.Text = "";
        }
    }
}