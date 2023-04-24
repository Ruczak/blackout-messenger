using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Net.Sockets;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Xamarin.Forms;

namespace Messeger
{
    public partial class MainPage : ContentPage
    {
        private ClientWebSocket ws;
        private ObservableCollection<Messege> messeges = new ObservableCollection<Messege>();
        public MainPage()
        {
            InitializeComponent();
            messegesListView.ItemsSource = messeges;
        }

        public async void OnIpChanged(object sender, TextChangedEventArgs e)
        {
            try
            {
                ws = new ClientWebSocket();
                await ws.ConnectAsync(new Uri($"ws://{ipEntry.Text}:8080/"), CancellationToken.None);
                statusLabel.Text = "Connected";
                statusLabel.TextColor = Color.Green;
                Console.WriteLine("WebSocket connected");

                while (ws.State == WebSocketState.Open)
                {
                    byte[] buffer = new byte[1024];
                    WebSocketReceiveResult result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
                    string message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
                    

                    if (result.EndOfMessage)
                    {
                        Messege receivedMessage = JsonConvert.DeserializeObject<Messege>(message);

                        Device.BeginInvokeOnMainThread(() =>
                        {
                            messeges.Add(receivedMessage);
                        });
                    }
                }

                statusLabel.Text = "Disconnected";
                statusLabel.TextColor = Color.Red;
                Console.WriteLine("WebSocket disconnected");
            }
            catch (Exception ex)
            {
                statusLabel.Text = "Connection failed: " + ex.Message;
                statusLabel.TextColor = Color.Red;
            }
        }

        protected async override void OnDisappearing()
        {
            if(ws != null)
            {
                await ws.CloseAsync(WebSocketCloseStatus.NormalClosure, string.Empty, CancellationToken.None);
                statusLabel.Text = "Disconnected";
                statusLabel.TextColor = Color.Red;
            }
            base.OnDisappearing();
        }

        private async void sendClicked(Object sender, EventArgs e)
        {
            if (ws.State == WebSocketState.Open)
            {
                string message = messegeEntry.Text;
                byte[] buffer = Encoding.UTF8.GetBytes(message);
                await ws.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, CancellationToken.None);
            }
        }
    }
}
