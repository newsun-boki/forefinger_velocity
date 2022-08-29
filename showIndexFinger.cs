using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class showIndexFinger : MonoBehaviour
{
    public Transform indexFinger;
    public Transform ball;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        // Debug.Log(indexFinger.position);
        ball.position = indexFinger.position;
    }
}
