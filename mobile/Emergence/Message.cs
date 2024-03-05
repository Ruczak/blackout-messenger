using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Emergence
{
    public class Message
    {
        public Message() { }
        public int Id { get; set; }
        public string content { get; set; }
        public string sender { get; set; }
        public string time { get; set; }
    }
}
