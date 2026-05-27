# Topology
<img width="942" height="395" alt="image" src="https://github.com/user-attachments/assets/bd7a1ae6-d293-48c8-9264-dbcbd3e575aa" />

Pre-requirement :
1. Run whole steps of focom and get kubeconfig ( It's should be set as `$STARLINGX_KUBECONFIG_B64` )

Target:
1. Install NFO and use `kubeconfig` to register a `Cluster ID`.
2. Use the `Cluster ID` to sequentially register various IDs, and finally obtain an `instance_id`.
3. Use the `instance_id` to deploy gNB to the target cluster.


## Skip the rAPP deploy nfo flow — deploy nfo directly using curl

let's directly use the kubeconfig file which we got from [nino_o2_focom-branch/revised_Example.md](https://github.com/bmw-ece-ntust/nino-o2-focom/blob/revised/Example.md)

Set `STARLINGX_KUBECONFIG_B64` as an environment variable:

Enter on SMO server `Archimedes`:
> Replace `/home/ubuntu/leo/smo-o2-focom` with the actual path of your FOCOM files.

```bash
cd /home/ubuntu/leo/smo-o2-focom
export STARLINGX_KUBECONFIG_B64=$(cat cluster_fixed.yaml | base64 -w 0)
```


### Main 6 Steps
```
Register Cluster
|
Set Credentials
|
Test Connection
|
Create VNF Descriptor
|
Create Deployment
|
Instantiate
```

> When nfo later connects to the rApp API via `deploy_via_nfo()`, only the last 3 steps are invoked. The first 3 steps still need to be completed manually.



Clone repo and switch to `revised` branch:
**Replace `<Your SSH Key>` with your actual SSH key for GitHub access.**
```bash
git clone https://<Your SSH Key>@github.com/bmw-ece-ntust/nino-o2-nfo.git

cd nino-o2-nfo
git checkout revised

```

Build up image from `nfo` folder:

- Build image and push to registry:
> Replace `<your-username>` with your actual username for the Quay registry.
```
docker logout bmw.ece.ntust.edu.tw

docker login bmw.ece.ntust.edu.tw

# Build
docker build -t bmw.ece.ntust.edu.tw/<your-username>/nfo:latest .   

# Push
docker push bmw.ece.ntust.edu.tw/<your-username>/nfo:latest
```

- Modify `values.yaml` ( Path : `nino-o2-nfo/nfo/k8s/chart`)
```
image:
  repository: bmw.ece.ntust.edu.tw/<your-username>/nfo
  tag: latest       
```


```
# Run nfo service
cd /...Path to nfo folder.../nino-o2-nfo/nfo/k8s/chart

helm install nfo . -n o2 --create-namespace


# verify nfo service is running

╭─ubuntu@zhongkui ~/testingSpace/nino-o2-nfo/nfo/k8s/chart ‹revised●›
╰─$ kubectl get svc -n o2
NAME   TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
nfo    NodePort   10.110.56.242   <none>        8000:31028/TCP   14s
```

NFO service port is `31028`


Step 1 — Register Cluster
> You can read Appendix of this note for "How to find STX Cluster's api endpoint?"
```bash
curl -X POST http://192.168.8.69:31028/api/kubernetes-clusters/ \
  -H 'Content-Type: application/json' \
  -d '{
    "api_endpoint": "https://192.168.206.202:30205",
    "cloud_name": "StarlingX",
    "auth_method": "kubeconfig",
    "cluster_version": "v1.31.0",
    "node_count": 3,
    "supports_helm": true
  }' | jq .

#### Log ####

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   727  100   524  100   203   3198   1239 --:--:-- --:--:-- --:--:--  4432
{
  "cloud_id": "64893fdc-b04f-4938-86c6-7d7c93e652b6",
  "cloud_name": "StarlingX",
  "api_endpoint": "https://192.168.206.202:30205",
  "api_version": "v1.29",
  "auth_method": "kubeconfig",
  "cluster_version": "v1.31.0",
  "node_count": 3,
  "supports_helm": true,
  "supports_operators": true,
  "default_namespace": "default",
  "max_pods_per_node": 110,
  "max_namespaces": 100,
  "storage_classes": [],
  "prometheus_endpoint": "",
  "connection_status": "UNKNOWN",
  "last_health_check": null,
  "created_at": "2026-05-07T23:04:56.353758Z",
  "updated_at": "2026-05-07T23:04:56.353789Z"
}
```
Note down your `<cluster-id>`: `64893fdc-b04f-4938-86c6-7d7c93e652b6` — you will need it later.


Step 2 — Set Credentials

Replace `<cluster-id>` and `$STARLINGX_KUBECONFIG_B64` with the actual values:
```bash

export CLUSTER_ID=64893fdc-b04f-4938-86c6-7d7c93e652b6

curl -X POST http://192.168.8.69:31028/api/kubernetes-clusters/$CLUSTER_ID/set_credentials/ \
  -H 'Content-Type: application/json' \
  -d '{
    "auth_method": "kubeconfig",
    "kubeconfig_content": "'$STARLINGX_KUBECONFIG_B64'"
  }'  | jq .


#### Log ####

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  9468  100    93  100  9375    258  26018 --:--:-- --:--:-- --:--:-- 26300
{
  "k8s_id": "64893fdc-b04f-4938-86c6-7d7c93e652b6",
  "status": "Credentials updated successfully"
}
```

Step 3 — Test Connection

```bash
curl -X POST http://192.168.8.69:31028/api/kubernetes-clusters/$CLUSTER_ID/test_connection/

#### Log ####

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--    100    82  100    82    0     0    230      0 --:--:-- --:--:-- --:--:--   2100    82  100    82    0     0    230      0 --:--:-- --:--:-- --:--:--   230
{
  "connected": true,
  "status": "CONNECTED",                                     <------------------ Connection successful
  "last_check": "2026-05-07T23:40:15.449493Z"
}
```


Step 4 — Create VNF Descriptor

```bash
curl -X POST http://192.168.8.69:31028/api/o2dms/v2/vnf_instances/ \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "oai-gnb-test",
    "profile_type": "kubernetes",
    "artifact_repo_url": "https://github.com/motangpuar/ocloud-helm-templates.git",
    "artifact_name": "oai-gnb-fhi-72",
    "artifact_repo_branch": "openshift/pegatron",
    "target_cluster": "'"$CLUSTER_ID"'",
    "values": {}
  }' | jq .


#### Log ####

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   954  100   635  100   319   3718   1867 --:--:-- --:--:-- --:--:--  5611
{
  "descriptor_id": "6ddf0ecb-1fd2-418c-bca4-6434cdf78316",
  "name": "oai-gnb-test",
  "description": "",
  "homing": false,
  "profile_type": "kubernetes",
  "artifact_source_type": "helm_repo",
  "artifact_chart_path": "",
  "artifact_repo_url": "https://github.com/motangpuar/ocloud-helm-templates.git",
  "artifact_name": "oai-gnb-fhi-72",
  "artifact_repo_branch": "openshift/pegatron",
  "artifact_version": "latest",
  "input_params": {},
  "required_cpu_cores": 1,
  "required_memory_gb": 1,
  "required_storage_gb": 10,
  "created_at": "2026-05-08T01:26:57.335347Z",
  "updated_at": "2026-05-08T01:26:57.335381Z",
  "additional_params": {},
  "target_cluster": "64893fdc-b04f-4938-86c6-7d7c93e652b6"
}
```

Note down the `descriptor_id`: `6ddf0ecb-1fd2-418c-bca4-6434cdf78316`


Step 5 — Create Deployment

Replace `6ddf0ecb-1fd2-418c-bca4-6434cdf78316` with your `descriptor_id`:
```bash

export DESCRIPTOR_ID=6ddf0ecb-1fd2-418c-bca4-6434cdf78316


curl -X POST http://192.168.8.69:31028/api/o2dms/v2/deployments/ \
  -H 'Content-Type: application/json' \
  -d '{
    "descriptor": "'"$DESCRIPTOR_ID"'",
    "name": "oai-gnb-test-deploy"
  }' | jq .


#### Log ####

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   516  100   419  100    97   1527    353 --:--:-- --:--:-- --:--:--  1883
{
  "instance_id": "7041b5a0-16cd-47ee-8f6f-b63a8ebdce70",
  "descriptor_name": "oai-gnb-test",
  "name": "oai-gnb-test-deploy",
  "user_provided_namespace": null,
  "instantiation_state": "NOT_INSTANTIATED",
  "deployment_namespace": null,
  "helm_release_name": null,
  "vm_instances": [],
  "smo_callback_url": "",
  "created_at": "2026-05-08T01:30:27.445337Z",
  "updated_at": "2026-05-08T01:30:27.445367Z",
  "descriptor": "6ddf0ecb-1fd2-418c-bca4-6434cdf78316"
}
```

Note down the `instance_id`: `7041b5a0-16cd-47ee-8f6f-b63a8ebdce70`

Step 6 — Instantiate (Actual Deployment):

```bash
export INSTANCE_ID=7041b5a0-16cd-47ee-8f6f-b63a8ebdce70

curl -X POST http://192.168.8.69:31028/api/o2dms/v2/deployments/$INSTANCE_ID/instantiate/ \
  -H 'Content-Type: application/json' \
  -d '{
    "instantiation_params": {
      "namespace": "oai-test"
    }
  }' | jq .
```


---

# Appendix

## How to delete a wrongly registered cluster ID

First, list the existing `cluster ID`s:

> Replace `192.168.8.69:31028` with your actual nfo `service IP` and `port`.
```bash
curl -X GET http://192.168.8.69:31028/api/kubernetes-clusters/ | jq .
```

After obtaining the ID, delete it:

> Replace `<CLUSTER_ID>` with the actual cluster ID you want to delete.
```bash
curl -X DELETE http://192.168.8.69:31028/api/kubernetes-clusters/<CLUSTER_ID>/
```

A successful deletion returns `204 No Content` (empty response).


## How to find STX Cluster's api endpoint?

You can use random IP from the cluster nodes with port `30205` as the API endpoint.

- Location of api server ( `worker-0` in this case):
```
12:38:58 root@galileo ~ → kubectl get pod -n oran-o2 -o wide
NAME                    READY   STATUS    RESTARTS   AGE     IP            NODE       NOMINATED NODE   READINESS GATES
o2api-9ccd47478-8jmmf   5/5     Running   0          7d22h   172.16.43.9   worker-0   <none>           <none>
```

- Service port ( It's `30205` !! )
```
08:41:49 root@galileo ~ → kubectl get svc -n oran-o2 | grep o2api
o2api     NodePort   10.108.95.13   <none>        5005:30205/TCP    126d
```

- Final API endpoint: `https://<worker-1's Internal IP>:30205` . 
```
09:30:11 root@galileo ~ → kubectl get nodes -o wide
NAME           STATUS   ROLES           AGE    VERSION   INTERNAL-IP       EXTERNAL-IP   OS-IMAGE                         KERNEL-VERSION     CONTAINER-RUNTIME
controller-1   Ready    control-plane   176d   v1.29.2   192.168.206.3     <none>        Debian GNU/Linux 11 (bullseye)   6.6.0-1-amd64      containerd://1.6.21
joule          Ready    <none>          174d   v1.29.2   192.168.206.82    <none>        Debian GNU/Linux 11 (bullseye)   6.6.0-1-rt-amd64   containerd://1.6.21
worker-0       Ready    <none>          176d   v1.29.2   192.168.206.223   <none>        Debian GNU/Linux 11 (bullseye)   6.6.0-1-amd64      containerd://1.6.21
worker-1       Ready    <none>          173d   v1.29.2   192.168.206.202   <none>        Debian GNU/Linux 11 (bullseye)   6.6.0-1-amd64      containerd://1.6.21     <---- worker-1's Internal IP : 192.168.206.202
```
