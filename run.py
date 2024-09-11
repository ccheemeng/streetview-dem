import aiocsv
import aiofiles
from aiohttp import ClientSession, ClientTimeout
import argparse
import asyncio

import geo
import streetview

import csv
from pathlib import Path

async def main(p1, p2, resolution, target_crs, filepath):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['x', 'y', 'z'])
    
    p1 = tuple(p1)
    p2 = tuple(p2)
    sample = geo.Sample(p1, p2, resolution)
    latlon = list(sample.generate_latlon_samples())
    lat = [x[0] for x in latlon]
    lon = [x[1] for x in latlon]
    radius = sample.search_radius()
    await write_panos(lat, lon, radius, target_crs, filepath)

async def write_panos(lat, lon, radius, target_crs, filepath):
    ids = set()
    async with ClientSession(timeout=ClientTimeout(total=None), raise_for_status=True) as session:
        async with aiofiles.open(filepath, 'w+') as afp:
            for i in range(len(lat)):
                async for row in get_xyz(session, ids, lat[i], lon[i], radius, target_crs):
                    writer = aiocsv.AsyncWriter(afp)
                    await writer.writerow(row)
    
async def get_xyz(session, ids, lat, lon, radius, target_crs):
    pano = await streetview.StreetViewAPI.find_pano_full(session, lat, lon, radius)
    if pano and pano.id not in ids and pano.elevation and pano.depth:
        ids.add(pano.id)
        xyz_4326 = (pano.lon, pano.lat, pano.elevation - pano.depth.data[-1][0])
        transformer = geo.Transform(4326, target_crs)
        xyz_target = transformer.transform3d(xyz_4326)
        print(xyz_target)
        yield xyz_target

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

    asyncio.run(main(args.p1, args.p2, args.resolution, args.target_crs, args.filepath))