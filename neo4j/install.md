## Create VM on Azure  

### Create VM  
1. `create vm`  
2. `chmod 400 neo4j-pc_key.pem`  
3. `ssh -i neo4j-pc_key.pem azureuser@20.x.x.x`  

### Inside the VM  
1. Add key and update sources:  
   ```bash
   wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -  
   echo 'deb https://debian.neo4j.com stable 4.4' | sudo tee /etc/apt/sources.list.d/neo4j.list  
   sudo apt update  
   ```

2. Install Neo4j:
   ```bash
   sudo apt install neo4j -y
   ```

3. Config Neo4j:
   ```bash
   sudo nano /etc/neo4j/neo4j.conf
   ```
   Localize and uncomment:
   ```
   dbms.default_listen_address=0.0.0.0
   ```

4. Set password:
   ```bash
   sudo neo4j-admin set-initial-password neo123456


### Verify
systemctl status neo4j
http://localhost:7474