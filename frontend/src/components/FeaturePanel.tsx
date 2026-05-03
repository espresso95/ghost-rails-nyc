import { MapPin, ShieldAlert, TrainFront } from "lucide-react";
import type { RailFeature } from "../types";

type FeaturePanelProps = {
  feature: RailFeature | null;
};

export function FeaturePanel({ feature }: FeaturePanelProps) {
  if (!feature) {
    return (
      <section className="panel-section empty-state">
        <MapPin size={22} aria-hidden="true" />
        <h2>Select a rail feature</h2>
        <p>Tap a point or line on the map, or search for a feature by name, borough, route, or corridor.</p>
      </section>
    );
  }

  const properties = feature.properties;

  return (
    <section className="panel-section feature-panel">
      <div className="feature-heading">
        <div>
          <p className="eyebrow">{formatType(properties.feature_type)}</p>
          <h2>{properties.name}</h2>
        </div>
        <span className="status-pill">{properties.status}</span>
      </div>

      <div className="fact-grid">
        <Fact label="Borough" value={properties.borough} />
        <Fact label="Opened" value={properties.opened_year?.toString() ?? "Unknown"} />
        <Fact label="Closed" value={properties.closed_year?.toString() ?? "N/A"} />
        <Fact label="Safety" value={formatType(properties.safety_classification)} />
      </div>

      <p className="summary">{properties.summary}</p>

      <div className="route-row">
        <TrainFront size={18} aria-hidden="true" />
        <div>
          <span className="label">Nearby service</span>
          <div className="route-list">
            {properties.nearby_active_routes.map((route) => (
              <span className="route-dot" key={route}>
                {route}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="safety-note">
        <ShieldAlert size={18} aria-hidden="true" />
        <span>{properties.visibility}</span>
      </div>
    </section>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="fact">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatType(value: string) {
  return value.replaceAll("_", " ");
}

