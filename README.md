# streetview-dem

Generate digital elevation maps (DEM) from google street view API queries.

## Installation

### Using Conda

Reproduced from [Conda's user guide](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file).

1. Create the environment from the ```environment.yml``` file:
    ```shell
    conda env create -f environment.yml
    ```
2. Activate the new environment:
    ```shell
    conda activate streetview-dem
    ```
3. Verify that the new environment was installed correctly:
    ```shell
    conda env list
    ```
    You can also use ```conda info --envs```.

## Running

```run.py``` queries a bounding rectangle for available Google Street View panoramas and builds a point cloud from the elevation data of the panoramas. Refer to the [Arguments](#arguments) section for details about input arguments.

Sample run:
```shell
python run.py 1.2843199044475546 103.77660798583958 1.3019238320101958 103.756764131736 -r 200 -t 3414 -o ./output/wcp.xyz
```
The above command will query the bounding rectangle defined by (1.2843199044475546, 103.77660798583958) and (1.3019238320101958, 103.756764131736) at a sample resolution of 200m. The output will be stored in ```./output/wcp.xyz``` in EPSG:3414 format.

## <a name="arguments"></a>Arguments

| Name             | Flags                  | Type        | Description                                                 | Required    | Default            |
|------------------|------------------------|-------------|-------------------------------------------------------------|-------------|--------------------|
| ```p1_lat```     | -                      | ```float``` | Latitude of p1 in WGS84                                     | ```True```  | -                  |
| ```p1_lon```     | -                      | ```float``` | Longitude of p1 in WGS84                                    | ```True```  | -                  |
| ```p2_lat```     | -                      | ```float``` | Latitude of p2 in WGS84                                     | ```True```  | -                  |
| ```p2_lon```     | -                      | ```float``` | Longitude of p2 in WGS84                                    | ```True```  | -                  |
| ```resolution``` | ```-r, --resolution``` | ```float``` | Maximum orthogonal distance between sample points in metres | ```False``` | ```50.0```         |
| ```target_crs``` | ```-t, --target```     | ```int```   | EPSG code of the target CRS                                 | ```False``` | ```4326```         |
| ```output```     | ```-o, --output```     | ```str```   | Output filepath                                             | ```False``` | ```./output.csv``` |

p1 and p2 serve as corner points defining the query bounding rectangle.
