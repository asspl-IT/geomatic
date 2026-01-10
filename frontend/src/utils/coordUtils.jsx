export function toDMS(deg, isLat = true) {
  const abs = Math.abs(deg);
  const d = Math.floor(abs);
  const m = Math.floor((abs - d) * 60);
  const s = (((abs - d) * 60 - m) * 60).toFixed(3);

  const dir = isLat
    ? deg >= 0 ? "N" : "S"
    : deg >= 0 ? "E" : "W";

  return `${d}° ${m}' ${s}" ${dir}`;
}
