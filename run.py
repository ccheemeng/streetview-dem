from aiohttp import ClientSession
import argparse
import asyncio

import geo
import streetview

import csv

def main(p1, p2, resolution, target_crs, filepath):
    p1 = tuple(p1)
    p2 = tuple(p2)
    
    panos = asyncio.run(get_panos(p1, p2, resolution))
    xyz_4326s = []
    ids = set()
    for pano in panos:
        if pano is not None and pano.id not in ids:
            ids.add(pano.id)
            xyz_4326s.append((pano.lon, pano.lat, pano.elevation - pano.depth.data[-1][0]))
    
    transformer = geo.Transform(4326, target_crs)
    xyz_target = list(map(lambda xyz: transformer.transform3d(xyz), xyz_4326s))
    
    with open(filepath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['x', 'y', 'z'])
        csv_writer.writerows(xyz_target)

async def get_panos(p1, p2, resolution):
    sample = geo.Sample(p1, p2, resolution)
    radius = sample.search_radius()
    async with ClientSession() as session:
        tasks = []
        for lat, lon in sample.generate_latlon_samples():
            tasks.append(streetview.StreetViewAPI.find_pano_full(session, lat, lon, radius))
        return await asyncio.gather(*tasks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(nargs=2, type=float,
                        help="Latitude and Longitude of the first bounding rectangle point",
                        dest="p1")
    parser.add_argument(nargs=2, type=float,
                        help="Latitude and Longitude of the second bounding rectangle point",
                        dest="p2")
    parser.add_argument("-r", "--resolution",
                        default=50, type=float, required=False,
                        help="Maximum distance between sample points",
                        dest="resolution")
    parser.add_argument("-t", "--target-crs",
                        default=4326, type=int, required=False,
                        help="EPSG code of the target CRS",
                        dest="target_crs")
    parser.add_argument("-o", "--output",
                        default="./output.xyz", type=str, required=False,
                        help="Output filepath",
                        dest="filepath")
    args = parser.parse_args()

    main(args.p1, args.p2, args.resolution, args.target_crs, args.filepath)