VERSION='v1.2.0'

read -p "location ? [westeurope]: " location
location=${location:-westeurope}

read -p "function name ? [dtInject]: " name
name=${name:-dtInject}

read -p "resource group name ? [rg-${name}]: " resourceGroupName
resourceGroupName=${resourceGroupName:-rg-$name}

read -p "Digital Twins resource group ? (required): " digitalTwinsResourceGroup
[[ -z $digitalTwinsResourceGroup ]] && echo "Digital Twins resource group must be set!" && exit 1

read -p "Digital Twins Name ?: " digitalTwinsName
[[ -z $digitalTwinsName ]] && echo "Digital Twins name must be set!" && exit 1

read -p "Dt-injector version ? [${VERSION}]: " dtInjectorPackageVersion
dtInjectorPackageVersion=${dtInjectorPackageVersion:-$VERSION}


dtInjectorPackage="https://github.com/Cosmo-Tech/azure-digital-twin-injector-python/releases/download/${dtInjectorPackageVersion}/artifact.zip"

# download function source from github
echo "Downloading dtinjector package..." && \
wget -O artifact.zip $dtInjectorPackage && \

# create resource group azure
if [[ "$(az group exists -g $resourceGroupName)" == "true" ]]; then
    echo  "Using existing Azure resource group"
else
    echo "Creating Azure resource group..." &&\
    az group create --location $location -n $resourceGroupName
fi

# install ARM (storage, service plan, function app)
echo "Installing ARM on $resourceGroupName..." && \
az deployment group create -g $resourceGroupName \
    --template-file ARM_injector_group.json \
    --parameters location=$location name=$name digitalTwinsResourceGroup=$digitalTwinsResourceGroup digitalTwinsName=$digitalTwinsName && \

# upload source to azure function app
echo "Upload source to function app..." && \
az functionapp deployment source config-zip -g $resourceGroupName -n $name --src artifact.zip && \

# restart function app
#echo "restart funciton app..." && \
#az functionapp restart -g rg-dtInjPy -n dtInjPy

rm artifact.zip
echo "done"
