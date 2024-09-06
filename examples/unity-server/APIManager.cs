using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class APIClient : MonoBehaviour
{
    private ObjectManager objectManager;
    private const string apiUrl = "http://localhost:5000";  
    

    private void Start()
    {
        objectManager = FindObjectOfType<ObjectManager>();
        if(objectManager == null)
        {
            Debug.LogError("Object manager is not assigned");
        }
        StartCoroutine(FetchAgentData());
    }

    private IEnumerator FetchAgentData()
    {
        while (true)
        {
            using (UnityWebRequest www = UnityWebRequest.Get("http://localhost:5000/get_agent_status"))
            {
                yield return www.SendWebRequest();

                if (www.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError($"Error getting agent updates: {www.error}");
                    Debug.LogError($"Response Code: {www.responseCode}");
                    Debug.LogError($"Response Body: {www.downloadHandler.text}");
                }
                else
                {
                    // Call the method on the instance of ObjectManager
                    objectManager.ProcessAgentUpdates(www.downloadHandler.text);
                }
            }
            yield return new WaitForSeconds(1f); // Poll every second
        }

    }
    public void UpdateAgents(string jsonData)
    {
        StartCoroutine(PostRequest(apiUrl + "/update_agents", jsonData));
    }

    public void GetAgentStatus()
    {
        StartCoroutine(GetRequest(apiUrl + "/get_agent_status"));
    }

    private IEnumerator PostRequest(string url, string jsonData)
    {
        using (UnityWebRequest www = UnityWebRequest.PostWwwForm(url, jsonData))
        {
            www.uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(jsonData));
            www.downloadHandler = new DownloadHandlerBuffer();
            www.SetRequestHeader("Content-Type", "application/json");
            
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                Debug.Log("Form upload complete!");
            }
            else
            {
                Debug.Log(www.error);
            }
        }
    }

    private IEnumerator GetRequest(string url)
    {
        using (UnityWebRequest www = UnityWebRequest.Get(url))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.Success)
            {
                Debug.Log(www.downloadHandler.text);
            }
            else
            {
                Debug.Log(www.error);
            }
        }
    }
}
