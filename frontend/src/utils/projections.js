import proj4 from "proj4";

// WGS84
proj4.defs(
  "EPSG:4326",
  "+proj=longlat +datum=WGS84 +no_defs"
);

// UTM Zone 44N (India)
proj4.defs(
  "EPSG:32644",
  "+proj=utm +zone=44 +datum=WGS84 +units=m +no_defs"
);

export function lonLatToUTM(lon, lat) {
  return proj4("EPSG:4326", "EPSG:32644", [lon, lat]);
}
