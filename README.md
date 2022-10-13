[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fgithub.com%2FCosmo-Tech%2Fazure-digital-twin-injector-python%2Fblob%2Fmaster%2Fdeploy%2FARM_injector_group.json)

# dt-injector - Digital twin csv injector

dtInjector is a group of Azure function app that manage (Create, Update, Delete) twins ans relations into an Azure Digital Twin instance from csv files. it simplifies feeding data into a digital twin.

# How to install

Run the install.sh script or follow the instructions below

## Prerequisites
You must have a resourceGroup to install the function on. You can create one with the command:
```
az create group -l <location> -n <resourceGroupName>
```

## Create resources
Use the Azure button above to acces the specific Azure installation wizard or use Azure CLI.
```
az deployment group create
```
[https://learn.microsoft.com/en-us/cli/azure/deployment/group?view=azure-cli-latest#az-deployment-group-create]

Download the artifact.zip from releases, and then push source to the function with the commande below:
```
az functionapp deployment source config-zip -g <resourceGroupName> -n <functionName> --src artifact.zip
```

# How to run
1. In order to run the DT Injector, we need the URL of the orchestrator function we want to execute. In order to retrieve the function url, go to Azure Portal, then to Functions and select the name of the function and click on Get Function Url (function key).

2. You should have already stored the csv files you want to use as an input in the correct storage in Azure : create-twins storage, update-twins storage etc.

3. After that, you need to send an HTTP request to the function Url that you retrieved with a tool that enables you to do that, like Postman for example.
The body of the HTTP request needs to specify the action we want to carry out and the element on which it operates. An example of an HTTP request body would be: 
{
"action": "Create",
"element": "Twin"
} 
The possible values for action are : Update, Create, Delete. And the possible values for element are : Twin, Relationship

4. You can check the result of the execution on ADT.

5. You can access the logs to debug or simply to have a record of the execution in Application Insights. Here are some useful KUSTO queries you can run : 
- traces | where message contains "Dev Log" : this query enables us to get all the logs that have been written in the code of the DT Injector, these are mainly the information logs about a creation/update/deletion of a twin/relationship or errors related to the structure of the received http request.
- traces | where customDimensions.["LogLevel"]==
        "Information"
        "Error"
        "Warning"
This query enables us to get the logs of a specified log level. 
    - The option “Error” shows the errors that occurred in the execution of the Function App. However, this query doesn’t enable us to get the exception. For example, if the creation of a twin is not successful because of an exception, we will not get this exception unless we run the following query : exceptions.
    - The option “Warning” could be quite useful especially since the logs about moving messages to a queue-poison are on a warning level.
- traces | where severityLevel ==
        "0" (for debug level)
        "1" (for information level)
        "2" (for warning level)
        "3" (for error level)
The results of this query resemble those of the previous one. 

6. Always check the queues in the Azure STorage Account linked to the DT Injector, to see if a poison queue has been created. If that is the case, the poison queue will contain all the messages that couldn’t successfully modify the ADT. 




