targetScope = 'resourceGroup'

// Parameters the user provides
@description('Azure region where the Synapse workspace will be deployed (must match the ADLS account region).')
param location string

@description('Name of the Synapse workspace.')
param synapseName string

@description('Existing ADLS Gen2 storage account name (in this resource group and same region).')
param storageAccountName string

@description('Existing ADLS Gen2 filesystem (container) name within the storage account.')
param filesystemName string

@description('Object ID of the initial Entra ID workspace admin (user or group).')
param initialWorkspaceAdminObjectId string

// Managed resource group name for Synapse-managed resources
var managedResourceGroupName = '${synapseName}-managedrg'

// Synapse workspace with Entra-only authentication and no managed private endpoint creation to ADLS
resource workspace 'Microsoft.Synapse/workspaces@2021-06-01' = {
  name: synapseName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    defaultDataLakeStorage: {
      // Required: user is providing existing ADLS account + filesystem
      // Hardcoded as requested: user cannot change this
      createManagedPrivateEndpoint: false
      accountUrl: 'https://${storageAccountName}.dfs.${environment().suffixes.storage}'
      filesystem: filesystemName
    }

    // Networking and managed RG
    managedVirtualNetwork: 'default'
    managedResourceGroupName: managedResourceGroupName

    // Security defaults
    publicNetworkAccess: 'Enabled'

    // Entra ID admin (required when using Entra-only auth)
    cspWorkspaceAdminProperties: {
      initialWorkspaceAdminObjectId: initialWorkspaceAdminObjectId
    }

    // Entra ID only authentication for SQL
    azureADOnlyAuthentication: true

    // Keep trusted service bypass disabled by default
    trustedServiceBypassEnabled: false
  }
}

// Explicitly enforce Entra-only auth via child resource (defense in depth with current API)
resource aadOnlyAuth 'Microsoft.Synapse/workspaces/azureADOnlyAuthentications@2021-06-01' = {
  parent: workspace
  name: 'default'
  properties: {
    azureADOnlyAuthentication: true
  }
}

// Minimum TLS settings for dedicated SQL (recommended security baseline)
resource minimalTls 'Microsoft.Synapse/workspaces/dedicatedSQLminimalTlsSettings@2021-06-01' = {
  parent: workspace
  name: 'default'
  properties: {
    minimalTlsVersion: '1.2'
  }
}

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output principalId string = workspace.identity.principalId
