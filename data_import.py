from pathlib import Path
from shapely.geometry import Point
from shapely.ops import nearest_points
import geopandas as gpd
import pandas as pd
import pyodbc
import requests

# Define path
SSURGO_FOLDER = "PA071"
base = Path(__file__).parent / SSURGO_FOLDER
tabular = base / "tabular"
mdb_file = base / "soildb_PA_2003.mdb"
spatial = base / "spatial"

# Load raw data tables
mapunit = pd.read_csv(tabular / "mapunit.txt", sep="|", header=None, low_memory=False)
component = pd.read_csv(tabular / "comp.txt", sep="|", header=None, low_memory=False)
chorizon = pd.read_csv(tabular / "chorizon.txt", sep="|", header=None, low_memory=False)

# Column names 
mapunit.columns = [
    "musym", "muname", "mukind", "mustatus", "muacres",
    "mapunitlfw_l", "mapunitlfw_r", "mapunitlfw_h",
    "mapunitpfa_l", "mapunitpfa_r", "mapunitpfa_h",
    "farmlndcl", "muhelcl", "muwathelcl", "muwndhelcl",
    "interpfocus", "invesintens", "iacornsr", "nhiforsoigrp",
    "nhspiagr", "vtsepticsyscl", "mvpi", "lkey", "mukey",
]

component.columns = [
    "comppct_l", "comppct_r", "comppct_h",         # 0-2
    "compname", "compkind", "majcompflag", "otherph", # 3-6
    "localphase", "slope_l", "slope_r", "slope_h",  # 7-10
    "slopelenusle_l", "slopelenusle_r", "slopelenusle_h", # 11-13
    "runoff", "tfact", "wei", "weg", "erocl",        # 14-18  (col14=nan, 15=1.0, 16=48, 17=6, 18=Class1)
    "earthcovkind1", "earthcovkind2",                # 19-20
    "hydricon", "hydricrating", "drainagecl",        # 21-23
    "sresstypmax_l", "sresstypmax_r", "sresstypmax_h", # 24-26
    "frostact_l", "frostact_r", "frostact_h",        # 27-29
    "aspectccwise", "aspectrep",                     # 30-31
    "aspectcwise_l", "aspectcwise_r",                # 32-33
    "geomdesc_l", "geomdesc_r", "geomdesc_h",        # 34-36
    "elev_l", "elev_r", "elev_h",                    # 37-39
    "reannualprecip_l", "reannualprecip_r", "reannualprecip_h", # 40-42
    "map_l", "map_r", "map_h",                       # 43-45
    "airtempa_r", "smoistcond",                      # 46-47
    "nirrrestrictor",                                # 48
    "tjstasoimoistdept_l", "tjstasoimoistdept_r", "tjstasoimoistdept_h", # 49-51
    "tjstasoimoistdepb_l", "tjstasoimoistdepb_r", "tjstasoimoistdepb_h", # 52-54
    "tjstasoimoiststat",                             # 55 (col53=10, rest nan)
    "col56", "col57", "col58", "col59",              # 56-59 (all nan - unknown)
    "col60", "col61", "col62", "col63",              # 60-63 (all nan)
    "col64", "col65", "col66", "col67",              # 64-67 (all nan)
    "col68", "col69", "col70", "col71",              # 68-71 (all nan)
    "taxclname",                                     # 72
    "castorieindex_l", "castorieindex_r", "castorieindex_h", # 73-75
    "flecolcomnum_l", "flecolcomnum_r", "flecolcomnum_h",    # 76-78
    "hydgrp", "corcon", "corsteel",                  # 79-81
    "taxclname2",                                    # 82
    "taxorder", "taxsuborder", "taxgrtgroup",        # 83-85
    "taxsubgrp", "taxpartsize", "taxpartsizemod",    # 86-88
    "taxceactcl", "taxreaction", "taxtempcl",        # 89-91
    "taxmoistscl", "taxtempregime", "soiltaxedition", # 92-94
    "col95", "col96", "col97", "col98", "col99",     # 95-99 (all nan)
    "col100", "col101", "col102", "col103", "col104", # 100-104 (all nan)
    "col105", "col106",                              # 105-106 (all nan)
    "mukey", "cokey",                                # 107-108
]

chorizon.columns = [
    "hzname", "desgndisc", "desgnmaster", "desgnmasterprime", "desgnvert",  # 0-4
    "hzdept_l", "hzdept_r", "hzdept_h",                                      # 5-7
    "hzdepb_l", "hzdepb_r", "hzdepb_h",                                      # 8-10
    "hzthk_l", "hzthk_r", "hzthk_h",                                        # 11-13
    "fraggt10_l", "fraggt10_r", "fraggt10_h",                                # 14-16
    "frag3to10_l", "frag3to10_r", "frag3to10_h",                            # 17-19
    "sieveno4_l", "sieveno4_r", "sieveno4_h",                                # 20-22
    "sieveno10_l", "sieveno10_r", "sieveno10_h",                             # 23-25
    "sieveno40_l", "sieveno40_r", "sieveno40_h",                             # 26-28
    "sieveno200_l", "sieveno200_r", "sieveno200_h",                          # 29-31
    "sandvf_l", "sandvf_r", "sandvf_h",                                      # 32-34
    "sandco_l", "sandco_r", "sandco_h",                                      # 35-37
    "sandmed_l", "sandmed_r", "sandmed_h",                                   # 38-40
    "sandfine_l", "sandfine_r", "sandfine_h",                               # 41-43
    "sandtotal_l", "sandtotal_r", "sandtotal_h",                            # 44-46
    "silttotal_l", "silttotal_r", "silttotal_h",                            # 47-49
    "claytotal_l", "claytotal_r", "claytotal_h",                            # 50-52
    "sandvc_l", "sandvc_r", "sandvc_h",                                      # 53-55
    "col56", "col57", "col58",                                               # 56-58
    "col59", "col60", "col61",                                               # 59-61
    "col62", "col63", "col64",                                               # 62-64
    "om_l", "om_r", "om_h",                                                  # 65-67
    "dbtenthbar_l", "dbtenthbar_r", "dbtenthbar_h",                         # 68-70
    "dbthirdbar_l", "dbthirdbar_r", "dbthirdbar_h",                         # 71-73
    "dbfifteenbar_l", "dbfifteenbar_r", "dbfifteenbar_h",                   # 74-76
    "dbovendry_l", "dbovendry_r", "dbovendry_h",                            # 77-79
    "partdensity",                                                            # 80
    "ksat_l", "ksat_r", "ksat_h",                                            # 81-83
    "awc_l", "awc_r", "awc_h",                                               # 84-86
    "wtenthbar_l", "wtenthbar_r", "wtenthbar_h",                            # 87-89
    "wthirdbar_l", "wthirdbar_r", "wthirdbar_h",                            # 90-92
    "wfifteenbar_l", "wfifteenbar_r", "wfifteenbar_h",                      # 93-95
    "wsatiated_l", "wsatiated_r", "wsatiated_h",                            # 96-98
    "lep_l", "lep_r", "lep_h",                                               # 99-101
    "ll_l", "ll_r", "ll_h",                                                  # 102-104
    "pi_l", "pi_r", "pi_h",                                                  # 105-107
    "aashind_l", "aashind_r", "aashind_h",                                   # 108-110
    "kwfact", "kffact",                                                       # 111-112
    "col113", "col114", "col115",                                            # 113-115
    "col116", "col117", "col118",                                            # 116-118
    "col119", "col120", "col121",                                            # 119-121
    "col122", "col123", "col124",                                            # 122-124
    "cec7_l", "cec7_r", "cec7_h",                                           # 125-127
    "ecec_l", "ecec_r", "ecec_h",                                            # 128-130
    "sumbases_l", "sumbases_r", "sumbases_h",                               # 131-133
    "ph1to1h2o_l", "ph1to1h2o_r", "ph1to1h2o_h",                           # 134-136
    "ph01mcacl2_l", "ph01mcacl2_r", "ph01mcacl2_h",                        # 137-139
    "freeiron_l", "freeiron_r", "freeiron_h",                               # 140-142
    "feoxalate_l", "feoxalate_r", "feoxalate_h",                            # 143-145
    "extracid_l", "extracid_r", "extracid_h",                               # 146-148
    "extral_l", "extral_r", "extral_h",                                      # 149-151
    "aloxalate_l", "aloxalate_r", "aloxalate_h",                            # 152-154
    "pbray1_l", "pbray1_r", "pbray1_h",                                      # 155-157
    "poxalate_l", "poxalate_r", "poxalate_h",                               # 158-160
    "ph2osoluble_l", "ph2osoluble_r", "ph2osoluble_h",                      # 161-163
    "ptotal_l", "ptotal_r", "ptotal_h",                                      # 164-166
    "excavdifcl", "excavdifms",                                              # 167-168
    "cokey", "chkey",                                                         # 169-170
]

# Filter to only get depths where we will probe (< 10 cm)
PROBE_DEPTH_CM = 10

dominant = component[component["majcompflag"] == "Yes"].copy()

hz = chorizon.copy()
hz["hzdept_r"] = pd.to_numeric(hz["hzdept_r"], errors="coerce")
hz["hzdepb_r"] = pd.to_numeric(hz["hzdepb_r"], errors="coerce")

mask = (hz["hzdept_r"] < PROBE_DEPTH_CM) & (hz["hzdepb_r"] > 0)
hz_filtered = hz[mask].copy()
hz_filtered = hz_filtered.reset_index(drop=True)

# Join the 3 tables
hz_cols = [
    "cokey", "chkey",
    "hzname", "hzdept_r", "hzdepb_r",
    "om_l", "om_r", "om_h",
    "cec7_l", "cec7_r", "cec7_h",
    "ph1to1h2o_l", "ph1to1h2o_r", "ph1to1h2o_h",
    "awc_r", "ksat_r", "dbthirdbar_r",
]

comp_cols = [
    "cokey", "mukey",
    "compname", "comppct_r", "drainagecl",
    "taxorder", "taxgrtgroup",
]

mapunit_cols = [
    "mukey", "musym", "muname",
]

hz_slim = hz_filtered[hz_cols].copy()
comp_slim = dominant[comp_cols].copy()
mapunit_slim = mapunit[mapunit_cols].copy()

merged = hz_slim.merge(comp_slim, on="cokey", how="inner")
merged = merged.merge(mapunit_slim, on="mukey", how="left")
merged = merged.reset_index(drop=True)

conn_str = (
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    f"DBQ={mdb_file};"
)

def read_mdb_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM [{table_name}]")
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    return pd.DataFrame.from_records(rows, columns=columns)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

chorizon_mdb = read_mdb_table(cursor, "chorizon")
conn.close()

texture_cache = Path(__file__).parent / "texture_lookup.csv"

if texture_cache.exists():
    # load from local cache — no internet needed
    texture = pd.read_csv(texture_cache)
    print("Loaded texture data from local cache")
else:
    # first run only — fetch from API and save locally
    print("Texture cache not found — fetching from SDA API...")
    query = """
    SELECT 
        mu.mukey,
        ch.sandtotal_r,
        ch.silttotal_r,
        ch.claytotal_r
    FROM 
        legend l
        INNER JOIN mapunit mu ON mu.lkey = l.lkey
        INNER JOIN component co ON co.mukey = mu.mukey
        INNER JOIN chorizon ch ON ch.cokey = co.cokey
    WHERE 
        l.areasymbol = 'PA071'
        AND co.majcompflag = 'Yes'
        AND ch.hzdept_r < 10
        AND ch.hzdepb_r > 0
    """
    url = "https://sdmdataaccess.sc.egov.usda.gov/tabular/post.rest"
    response = requests.post(url, data={"query": query, "format": "JSON"})
    data = response.json()
    df = pd.DataFrame(data["Table"], columns=["mukey", "sandtotal_r", "silttotal_r", "claytotal_r"])
    df["mukey"] = pd.to_numeric(df["mukey"], errors="coerce")
    texture = df.drop_duplicates(subset="mukey").copy()
    texture.rename(columns={
        "sandtotal_r": "sand_pct",
        "silttotal_r": "silt_pct",
        "claytotal_r": "clay_pct",
    }, inplace=True)
    texture.to_csv(texture_cache, index=False)
    print(f"Texture data saved to {texture_cache}")

# join to merged
texture["mukey"] = pd.to_numeric(texture["mukey"], errors="coerce")
merged["mukey"] = pd.to_numeric(merged["mukey"], errors="coerce")
merged = merged.merge(texture, on="mukey", how="left")

# Stats
for col in ["om_r", "cec7_r", "ph1to1h2o_r", "sand_pct", "silt_pct", "clay_pct", "awc_r", "ksat_r"]:
    merged[col] = pd.to_numeric(merged[col], errors="coerce")

# Export to CSV
output_path = Path(__file__).parent / "SSURGO_results.csv"
merged.to_csv(output_path, index=False)
print(f"\n✓ Results saved to: {output_path}")
print(f"  {len(merged)} rows, {len(merged.columns)} columns")

shapefile = spatial / "soilmu_a_pa071.shp"
soilmap = gpd.read_file(shapefile)

def soil_lookup(lat, lon, soilmap, soildata):
    """ 
    Given a latitude and longitude, returns the 
    soil properties from SSURGO data referenced
    from their polygons
    """
    point = Point(lon, lat)
    match = soilmap[soilmap.geometry.contains(point)]

    if match.empty:
        return None
    
    # Fetch mapunit key
    mukey = int(match.iloc[0]['MUKEY'])

    # Look up soil properties
    result = soildata[soildata['mukey'] == mukey]

    if result.empty:
        return None
    
    return result.iloc[0]

test_lat = 39.870045
test_lon = -76.185195

result = soil_lookup(test_lat, test_lon, soilmap, merged)

if result is not None:
    print(f"Soil at ({test_lat}, {test_lon}):")
    print(f"  Map unit:   {result['musym']} — {result['muname']}")
    print(f"  Soil series: {result['compname']}")
    print(f"  pH:          {result['ph1to1h2o_r']}")
    print(f"  OM:          {result['om_r']}%")
    print(f"  CEC:         {result['cec7_r']} meq/100g")
    print(f"  Sand:        {result['sand_pct']}%")
    print(f"  Silt:        {result['silt_pct']}%")
    print(f"  Clay:        {result['clay_pct']}%")
else:
    print("No soil data found for this location")