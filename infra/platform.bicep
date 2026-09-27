param environmentName string
param location string
param suffix string
param postgresAdminLogin string
@secure()
param postgresAdminPassword string

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-riskml-${suffix}'
  location: location
  properties: { retentionInDays: environmentName == 'prod' ? 30 : 7 }
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-riskml-${suffix}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: workspace.listKeys().primarySharedKey
      }
    }
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'striskml${suffix}'
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource fileService 'Microsoft.Storage/storageAccounts/fileServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource modelShare 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-05-01' = {
  parent: fileService
  name: 'models'
  properties: {
    accessTier: 'TransactionOptimized'
    enabledProtocols: 'SMB'
  }
}

resource modelStorage 'Microsoft.App/managedEnvironments/storages@2024-03-01' = {
  parent: environment
  name: 'models'
  properties: {
    azureFile: {
      accountName: storage.name
      accountKey: storage.listKeys().keys[0].value
      shareName: modelShare.name
      accessMode: 'ReadOnly'
    }
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: 'psql-riskml-${suffix}'
  location: location
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: {
    administratorLogin: postgresAdminLogin
    administratorLoginPassword: postgresAdminPassword
    version: '16'
    storage: { storageSizeGB: 32 }
    backup: { backupRetentionDays: environmentName == 'prod' ? 14 : 7 }
    network: { publicNetworkAccess: 'Disabled' }
    highAvailability: { mode: 'Disabled' }
  }
}

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-riskml-${suffix}'
  location: location
  identity: { type: 'SystemAssigned' }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      ingress: { external: true, targetPort: 8000, transport: 'http' }
      activeRevisionsMode: 'Single'
    }
    template: {
      containers: [{
        name: 'api'
        image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
        env: [
          { name: 'RISK_ML_ENVIRONMENT', value: environmentName }
          { name: 'RISK_ML_MODEL_PATH', value: '/models/champion.joblib' }
        ]
        volumeMounts: [{ volumeName: 'models', mountPath: '/models' }]
        resources: { cpu: json('0.5'), memory: '1Gi' }
        probes: [
          { type: 'Liveness', httpGet: { path: '/health', port: 8000 }, initialDelaySeconds: 10 }
          { type: 'Readiness', httpGet: { path: '/ready', port: 8000 }, initialDelaySeconds: 10 }
        ]
      }]
      volumes: [{ name: 'models', storageType: 'AzureFile', storageName: modelStorage.name }]
      scale: { minReplicas: environmentName == 'prod' ? 1 : 0, maxReplicas: 3 }
    }
  }
}

output apiFqdn string = api.properties.configuration.ingress.fqdn
output storageAccountName string = storage.name
output postgresServerName string = postgres.name

