targetScope = 'subscription'

@allowed(['dev', 'staging', 'prod'])
param environmentName string = 'dev'
param location string
@minLength(3)
param postgresAdminLogin string
@secure()
param postgresAdminPassword string

var suffix = uniqueString(subscription().id, environmentName, location)
var resourceGroupName = 'rg-riskml-${environmentName}-${suffix}'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: {
    workload: 'risk-ml'
    environment: environmentName
  }
}

module platform 'platform.bicep' = {
  scope: resourceGroup
  name: 'riskml-platform'
  params: {
    environmentName: environmentName
    location: location
    suffix: suffix
    postgresAdminLogin: postgresAdminLogin
    postgresAdminPassword: postgresAdminPassword
  }
}

output resourceGroupName string = resourceGroup.name
output apiFqdn string = platform.outputs.apiFqdn
output storageAccountName string = platform.outputs.storageAccountName

