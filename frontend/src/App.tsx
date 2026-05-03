import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Layers, Search } from "lucide-react";
import { fetchFeatures, searchFeatures } from "./api/client";
import { ChatPanel } from "./components/ChatPanel";
import { FeaturePanel } from "./components/FeaturePanel";
import { MapView } from "./components/MapView";
import type { FeatureCollection, RailFeature } from "./types";

export function App() {
  const [features, setFeatures] = useState<FeatureCollection | null>(null);
  const [selectedFeatureId, setSelectedFeatureId] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    fetchFeatures()
      .then(setFeatures)
      .catch((caughtError: Error) => setError(caughtError.message));
  }, []);

  const selectedFeature = useMemo(() => {
    return features?.features.find((feature) => feature.properties.id === selectedFeatureId) ?? null;
  }, [features, selectedFeatureId]);

  async function handleSearch() {
    if (!query.trim()) {
      return;
    }
    setIsSearching(true);
    setError(null);
    try {
      const results = await searchFeatures(query.trim());
      if (results[0]) {
        setSelectedFeatureId(results[0].feature.properties.id);
      } else {
        setError("No matching rail features found.");
      }
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Search failed.");
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">GR</span>
          <div>
            <h1>Ghost Rails NYC</h1>
            <p>Local subway-history atlas</p>
          </div>
        </div>
        <form
          className="search-form"
          onSubmit={(event) => {
            event.preventDefault();
            void handleSearch();
          }}
        >
          <Search size={18} aria-hidden="true" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="City Hall, Rockaway, old els"
            aria-label="Search rail features"
          />
          <button type="submit" disabled={isSearching}>
            Search
          </button>
        </form>
      </header>

      {error && (
        <div className="error-banner" role="alert">
          <AlertTriangle size={18} aria-hidden="true" />
          <span>{error}</span>
        </div>
      )}

      <section className="workspace">
        <div className="map-region">
          <MapView
            features={features}
            selectedFeatureId={selectedFeatureId}
            onSelectFeature={setSelectedFeatureId}
          />
          <div className="map-status">
            <Layers size={16} aria-hidden="true" />
            <span>{featureCountLabel(features?.features ?? [])}</span>
          </div>
        </div>
        <aside className="side-panel">
          <FeaturePanel feature={selectedFeature} />
          <ChatPanel selectedFeature={selectedFeature} />
        </aside>
      </section>
    </main>
  );
}

function featureCountLabel(features: RailFeature[]) {
  if (features.length === 0) {
    return "Loading local features";
  }
  return `${features.length} curated features`;
}

