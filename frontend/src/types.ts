export type PointGeometry = {
  type: "Point";
  coordinates: [number, number];
};

export type LineStringGeometry = {
  type: "LineString";
  coordinates: [number, number][];
};

export type Geometry = PointGeometry | LineStringGeometry;

export type RailFeatureProperties = {
  id: string;
  name: string;
  feature_type: string;
  borough: string;
  status: string;
  opened_year: number | null;
  closed_year: number | null;
  nearby_active_routes: string[];
  nearby_active_stations: string[];
  visibility: string;
  safety_classification: string;
  summary: string;
  source_ids: string[];
};

export type RailFeature = {
  type: "Feature";
  geometry: Geometry;
  properties: RailFeatureProperties;
};

export type FeatureCollection = {
  type: "FeatureCollection";
  features: RailFeature[];
};

export type SourceSnippet = {
  title: string;
  document_id: string;
  chunk_id: string;
  snippet: string;
};

export type ChatResponse = {
  answer: string;
  sources: SourceSnippet[];
  confidence: string;
  safety_note: string | null;
  retrieval_debug: Record<string, unknown>;
};

export type SearchResult = {
  score: number;
  feature: RailFeature;
};
