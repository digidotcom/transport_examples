# Enable Digi Remote Manager (DRM) via SSH
The purpose of this application is to enable [Digi Remote Manager](https://my.devicecloud.com/) on a single TransPort router or to a list of TransPort routers from a configuration file.

Upon completion of each update, the router is rebooted and the DRM Device Id is added to a CSV file for uploading to DRM via the Bulk Add feature.

## Usage
Optional, create a virtual Python environment, using `virtualenv` 
1) Install required packages via [PIP](https://pypi.python.org/pypi/pip) using `pip install -r requirements.txt`
2) Run the application providing an IP address as the first argument
`$ python enable_drm.py 1.2.3.4`
3) OR, Run the application providing a list of IP addresses in a file, titled `iplist.txt`.
`$ python enable_drm.py`
4) Use the `bulkadd_results_[datetime].csv` file to upload successfully provisioned routers to **Digi Remote Manager** using the **Bulk Add** feature. Bulk Add is found under the **Device Management** tab within the **`More...`** button.

## Configuration file format: `iplist.txt`
A single IP address per line, accessible from PC running application. Lines beginning with a hash `#`, will be skipped and considered a comment.
Example file:
```
# skip this line
1.1.1.1
2.2.2.2
3.3.3.3
4.4.4.4
```
