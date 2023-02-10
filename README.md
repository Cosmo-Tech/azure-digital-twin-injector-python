# dt-injector - Digital twin csv injector

dtInjector is a group of Azure function app that manage (Create, Update, Delete) twins ans relations into an Azure Digital Twin instance from csv files. it simplifies feeding data into a digital twin.

# How to install

## Prerequisites

- use a support that runs bash
- have installed azCli
- have correct admin rights \**see below for details*

## Install

Log in with azCli:
```
az login
```

Run the install.sh: (This script can be found in the 'deploy' folder.)
```
./install.sh
```

## Description

This script prompt information to run properly:
- **location**: An Azure cloud location use when creting Azure resources. (Default value: *westeurope*)
- **function name**: use to name defferent resources. (Default value: *dtInject*)
    - the Azure function as *"{name}"*
    - the Azure resource group as *"rg-{name}"* (only if not override after)
    - the Azure hosting plan as *"hpn-{name}"*
    - the Azure storage account name as *"s{name}"* (for this one '-' are removed and the whole name is passed to lower case).
- **resource group name**: use to select the resource group in which the function, service plan and storage will be create. (if it doesn't existe the resource group will be created with this name) (Default value: *rg-{name}*)
- **Digital Twins resource group**: use to find the ADT that will be the target of the injection function. (required)
- **Digital Twins Name**: use to find the ADT that will be the target of the injection function. (required)

On exectution, this script will:
1. Download function source package
2. Create an Azure resource group (or use the one specified if exist)
3. Deploy the ARM "ARM_injector_group.json" (found in the deploy folder)
    1. Create the storage account in the resource group with all necessary containers and queue
        - **container** input-files
        - **container** history-files
        - **queue**     create-twin-queue
        - **queue**     create-relationship-queue
        - **queue**     delete-twin-queue
        - **queue**     delete-relationship-queue
        - **queue**     update-twin-queue
        - **queue**     update-relationship-queue
    2. Create the hosting plan
        - **sku tier** ElasticPremium
    3. Create the Azure function
        - **application setting** AzureWebJobsStorage: containing the connection string to the Azure storage previously created
        - **application setting** storageAccountName:  containing the name of the Azure storage previously created
        - **application setting** DIGITAL_TWIN_URL:    containing the target ADT url
        - **application setting** FUNCTIONS_EXTENSION_VERSION: ~4 (recommended [Azure Functions runtime version](https://learn.microsoft.com/en-us/azure/azure-functions/functions-versions?tabs=v4&pivots=programming-language-python))
        - **application setting** FUNCTIONS_WORKER_RUNTIME: python
        - **application setting** WEBSITE_RUN_FROM_PACKAGE: 1 (indicate that the function source are set from a package)
        - **site configuration**  linuxFxVersion: python|3.9
    4. Assign to the Azure Function the azureDigitalTwinDataOwner role on ADT
4. Upload the source package to the azure function

### About rights 
To be able to run correctly, the user log in must have the right to do all the action above.
- Create a resource group 
- Create a storage account
- Create a hosting plan
- Create an Azure Function App
- Assign azureDigitalTwinDataOwner role to ADT
- Update an Azure Function App


# How to manual install

To manual install the function, all above step must be done including running the ARM. The ARM can be seen as a complilation of step, so each sub-step can be run separatly.
Each step and sub-step has a [az cli](https://learn.microsoft.com/en-us/cli/azure/reference-index?view=azure-cli-latest) command linked to it.

Prerequisites are the same as for the install by script.


# How to run
1. In order to run the DT Injector, we need to get the `InjectorEntrypoint` url with default or master code.

2. You should have already stored your input csv files in the correct Azure storage (depending on the action you want to perform):
    - create-storage/create-twins
    - create-storage/create-relationships
    - update-storage/update-twins
    - update-storage/update-relationships
    - delete-storage/delete-twins
    - delete-storage/delete-relationships

3. After that, you need to send an HTTP request to the `InjectorEntrypoint` function Url that you retrieved with a tool that enables you to do that, like Postman for example.
The body of the HTTP request should be empty but the URL as a parameter that you should change for each action we want to carry out (remove the code as it is extracted from the request)
```
POST https://{myfunc}.azurewebsites.net/api/orchestrators/{action}?code={mycode}
```
The possible values for action are :
- `Create_Twins`
- `Create_Relationships`
- `Delete_Twins`
- `Delete_Relationships`
- `Update_Twins`
- `Update_Relationships`

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

# How it runs

This project contains a total of 13 functions. They interact as describe in the following schema:
![image](.images/schema_global)

This create the 6 functions *Create_Twin*, *Create_Relationship*, *Update_Twin*, *Update_Relationship*, *Delete_Twin*, *Delete_Relationships*.
Thoses functions works asynchronously as they utilize queue for processing message.

## Function behaviour

### Create Twins and Relationships
These create function use Azure python library function **"Upsert"** which create or replace a twin or relationships.

### Update Twins and Relationships
These update funciton use Azure python library function **"Update"** at which is given update operation base on input csv content. 

- Each non-empty field is process as a add operation which create or replace the twin attribue.
- Each empty field is process as a delete operation which remove the twin attribue.

This function is not idempotent, trying to remove an already removed attribues will result in an exception.

### Delete Twins and Relationships
These delete function use Azure python library function **"Delete"** which remove a twin or relationships.

The Azure Digital Twin will prevent any deletion of a twin with a relationship. Trying to do so will result in an Exception.

# Technicalities

* History-files container only hold the last file read. It's not an archive with all processed files.
* As thoses functions are asynchronous, processing already started will continue even if an exception is raised.
