import { useEffect, useMemo, useRef } from "react";
import maplibregl, { GeoJSONSource, Map, StyleSpecification } from "maplibre-gl";
import type { FeatureCollection, RailFeature } from "../types";

type MapViewProps = {
  features: FeatureCollection | null;
  selectedFeatureId: string | null;
  onSelectFeature: (featureId: string) => void;
};

const STYLE: StyleSpecification = {
  version: 8,
  sources: {
    osm: {
      type: "raster",
      tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "OpenStreetMap",
    },
  },
  layers: [
    {
      id: "osm",
      type: "raster",
      source: "osm",
    },
  ],
};

export function MapView({ features, selectedFeatureId, onSelectFeature }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);

  const geojson = useMemo(() => features ?? {type: "FeatureCollection" as const, features: []}, [features]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return;
    }

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: STYLE,
      center: [-73.97, 40.73],
      zoom: 10.3,
      minZoom: 9,
      maxZoom: 16,
      attributionControl: false,
    });

    map.addControl(new maplibregl.NavigationControl({showCompass: false}), "top-right");
    map.addControl(new maplibregl.AttributionControl({compact: true}), "bottom-left");
    mapRef.current = map;

    map.on("load", () => {
      map.addSource("features", {
        type: "geojson",
        data: geojson,
      });
      map.addLayer({
        id: "historic-lines",
        type: "line",
        source: "features",
        filter: ["==", ["geometry-type"], "LineString"],
        paint: {
          "line-color": ["case", ["==", ["get", "id"], selectedFeatureId ?? ""], "#e11d48", "#1f7a6d"],
          "line-width": ["case", ["==", ["get", "id"], selectedFeatureId ?? ""], 5, 3],
          "line-opacity": 0.82,
        },
      });
      map.addLayer({
        id: "historic-points",
        type: "circle",
        source: "features",
        filter: ["==", ["geometry-type"], "Point"],
        paint: {
          "circle-color": ["case", ["==", ["get", "id"], selectedFeatureId ?? ""], "#e11d48", "#f8c630"],
          "circle-radius": ["case", ["==", ["get", "id"], selectedFeatureId ?? ""], 8, 6],
          "circle-stroke-color": "#111827",
          "circle-stroke-width": 1.4,
        },
      });

      for (const layerId of ["historic-points", "historic-lines"]) {
        map.on("click", layerId, (event) => {
          const feature = event.features?.[0];
          const featureId = feature?.properties?.id;
          if (typeof featureId === "string") {
            onSelectFeature(featureId);
          }
        });
        map.on("mouseenter", layerId, () => {
          map.getCanvas().style.cursor = "pointer";
        });
        map.on("mouseleave", layerId, () => {
          map.getCanvas().style.cursor = "";
        });
      }
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) {
      return;
    }
    const source = map.getSource("features") as GeoJSONSource | undefined;
    if (source) {
      source.setData(geojson);
    }
  }, [geojson]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) {
      return;
    }
    for (const layerId of ["historic-points", "historic-lines"]) {
      if (!map.getLayer(layerId)) {
        continue;
      }
      const color = layerId === "historic-points" ? "circle-color" : "line-color";
      map.setPaintProperty(layerId, color, ["case", ["==", ["get", "id"], selectedFeatureId ?? ""], "#e11d48", layerId === "historic-points" ? "#f8c630" : "#1f7a6d"]);
    }
    const selected = features?.features.find((feature) => feature.properties.id === selectedFeatureId);
    if (selected) {
      flyToFeature(map, selected);
    }
  }, [features, selectedFeatureId]);

  return <div className="map-canvas" ref={containerRef} aria-label="Map of historic NYC rail features" />;
}

function flyToFeature(map: Map, feature: RailFeature) {
  const coordinates = feature.geometry.coordinates;
  if (feature.geometry.type === "Point") {
    map.flyTo({center: coordinates as [number, number], zoom: Math.max(map.getZoom(), 12), essential: true});
    return;
  }

  const points = coordinates as [number, number][];
  const bounds = points.reduce((currentBounds, point) => currentBounds.extend(point), new maplibregl.LngLatBounds(points[0], points[0]));
  map.fitBounds(bounds, {padding: 72, maxZoom: 12.6, duration: 700});
}
