# Elastic Cloud Deployment on Azure

This guide provides steps to configure Elastic Cloud service in the Azure portal.

## Step 1: Access Azure Portal
1. Go to [Azure Portal](https://portal.azure.com).
2. Sign in with your Azure account.

## Step 2: Navigate to Azure Marketplace
1. Click **Create a resource** in the left menu.
2. Search for **Elastic Cloud**.
3. Select **Elastic Cloud (An Azure Native ISV Service)** from the search results.

## Step 3: Create Elastic Cloud Deployment
1. Click **Create**.
2. Select your **Azure subscription**.
3. Create or select a **resource group**.
4. Choose a **region** near your location.

## Step 4: Finish and Deploy
1. Click **Review + create**.
2. Verify the settings.
3. Click **Create**.
4. Wait for deployment completion (this may take a few minutes).

## Step 6: Get Access Credentials
1. Go to the resource created on Kibana.
3. Create an **API key** by following the instructions.

## Step 7: Create API Key
1. After creating the API key, save the **full key** (formatted as `id:key`).
2. **IMPORTANT**: Store the API key securely, as it won't be displayed again.


# ElasticSearch on Local
## Dependencies
sudo apt-get update && sudo apt-get install apt-transport-https wget -y
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list

## Install
sudo apt-get update && sudo apt-get install elasticsearch -y

## Start service
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch

## set password
sudo /usr/share/elasticsearch/bin/elasticsearch-reset-password -u elastic -i

# Install Kibana
## Install
sudo apt install kibana
sudo systemctl enable kibana
sudo systemctl start kibana

## Configure
access http://localhost:5601

## generate Kibana token
sudo /usr/share/elasticsearch/bin/elasticsearch-create-enrollment-token -s kibana

## generate verification code
sudo /usr/share/kibana/bin/kibana-verification-code