using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;

public class ObjectManager : MonoBehaviour
{
    public GameObject dronePrefab; // Assign this in the Unity Editor
    public Transform objectsParent; // Assign this to manage objects

    private Dictionary<string, GameObject> agents = new Dictionary<string, GameObject>();

    private void Start()
    {
        StartCoroutine(GetAgentUpdates());
    }

    private IEnumerator GetAgentUpdates()
    {
        while (true)
        {
            using (UnityWebRequest www = UnityWebRequest.Get("http://localhost:5500/")) // Replace with your server URL
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
                    ProcessAgentUpdates(www.downloadHandler.text);
                }
            }
            yield return new WaitForSeconds(1f); // Poll every second
        }
    }

    public void ProcessAgentUpdates(string jsonData)
    {
        // Assume jsonData is a JSON string with agent information
        var agentsData = JsonUtility.FromJson<AgentData[]>(jsonData);

        foreach (var data in agentsData)
        {
            if (!agents.ContainsKey(data.agentType))
            {
                // Create new agent
                GameObject agent = Instantiate(dronePrefab, data.position, Quaternion.identity, objectsParent);
                agents[data.agentType] = agent;
            }
            else
            {
                // Update existing agent
                GameObject agent = agents[data.agentType];
                agent.transform.position = data.position;
            }
        }

        // Handle deletion
        var keysToRemove = new List<string>();
        foreach (var agent in agents)
        {
            bool exists = false;
            foreach (var data in agentsData)
            {
                if (data.agentType == agent.Key)
                {
                    exists = true;
                    break;
                }
            }
            if (!exists)
            {
                keysToRemove.Add(agent.Key);
                Destroy(agent.Value);
            }
        }

        foreach (var key in keysToRemove)
        {
            agents.Remove(key);
        }
    }
}

[System.Serializable]
public class AgentData
{
    public string agentType;
    public Vector2 position;
}
