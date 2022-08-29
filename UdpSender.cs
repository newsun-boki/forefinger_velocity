using UnityEngine;
using System;
using System.Text;
using System.Net;
using System.Net.Sockets;
using System.Threading;

public class UdpSender : MonoBehaviour
{

    UdpClient client; 
    public int port = 5052;
    public bool startRecieving = true;
    public bool printToConsole = false;
    public Transform tf;


    public void Start()
    {

        client = new UdpClient(0);
        client.Connect("localhost",port);
    }


    // receive thread
    public void Update() 
    {

        try
        {
            string str =  tf.position.x.ToString() + ","+ tf.position.y.ToString() + ","+tf.position.z.ToString();
            byte[] sendBytes = Encoding.ASCII.GetBytes(str);
            client.Send(sendBytes,sendBytes.Length);
            if(printToConsole){
                Debug.Log(str);
            }
        }
        catch (Exception err)
        {
            print(err.ToString());
        }
        
    }

}
