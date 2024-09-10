from aiohttp import ClientSession, ClientTimeout
import argparse
import asyncio

import geo
import streetview

import csv
from pathlib import Path

def main(p1, p2, resolution, target_crs, filepath):
    p1 = tuple(p1)
    p2 = tuple(p2)
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['x', 'y', 'z'])    
    panos = asyncio.run(write_panos(p1, p2, resolution, target_crs, filepath))

async def write_panos(p1, p2, resolution, target_crs, filepath):
    sample = geo.Sample(p1, p2, resolution)
    radius = sample.search_radius()
    async with ClientSession(timeout=ClientTimeout(total=None), raise_for_status=True) as session:
        tasks = []
        ids = set()
        for lat, lon in sample.generate_latlon_samples():
            tasks.append(write_pano_xyz(ids, await streetview.StreetViewAPI.find_pano_full(session, lat, lon, radius), target_crs, filepath))
        await asyncio.gather(*tasks)
    
async def write_pano_xyz(ids, pano, target_crs, filepath):
    if pano and pano.elevation and pano.depth and pano.id not in ids:
        ids.add(pano.id)
        xyz_4326 = (pano.lon, pano.lat, pano.elevation - pano.depth.data[-1][0])
        transformer = geo.Transform(4326, target_crs)
        xyz_target = transformer.transform3d(xyz_4326)
        print(xyz_target)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, writerow, xyz_target, filepath)

def writerow(row, filepath):
    with open(filepath, 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(nargs=2, type=float,
                        help="Latitude and Longitude of the first bounding rectangle point",
                        dest="p1")
    parser.add_argument(nargs=2, type=float,
                        help="Latitude and Longitude of the second bounding rectangle point",
                        dest="p2")
    parser.add_argument("-r", "--resolution",
                        default=50.0, type=float, required=False,
                        help="Maximum distance between sample points",
                        dest="resolution")
    parser.add_argument("-t", "--target-crs",
                        default=4326, type=int, required=False,
                        help="EPSG code of the target CRS",
                        dest="target_crs")
    parser.add_argument("-o", "--output",
                        default="./output.csv", type=str, required=False,
                        help="Output filepath",
                        dest="filepath")
    args = parser.parse_args()

    main(args.p1, args.p2, args.resolution, args.target_crs, args.filepath)