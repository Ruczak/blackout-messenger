using Microsoft.Maui.Controls;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Emergence
{
    public class MessageTemplateSelector : DataTemplateSelector
    {
        public DataTemplate IncomingTemplate { get; set; } 
        public DataTemplate OutgoingTemplate { get; set; }
        protected override DataTemplate OnSelectTemplate(object item, BindableObject container)
        {
            return ((Message)item).sender != MainPage.ServerID ? IncomingTemplate : OutgoingTemplate;
        }
    }
}
