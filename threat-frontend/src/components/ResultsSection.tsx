import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import type { AnalysisResponse, Threat } from "../types/analysis";
import { RISK_LEVEL_CONFIG } from "../constants/riskLevels";
import { ThreatCard } from "./ThreatCard";
import { Activity, Cpu, Shield } from "lucide-react";

interface ResultsSectionProps {
  analysis: AnalysisResponse;
}

function sortThreatsByScore(threats: Threat[]): Threat[] {
  return [...threats].sort(
    (a, b) => (b.dread_score ?? 0) - (a.dread_score ?? 0),
  );
}

export function ResultsSection({ analysis }: ResultsSectionProps) {
  const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set([0]));
  const riskConfig = RISK_LEVEL_CONFIG[analysis.risk_level];
  const threatsByScore = useMemo(
    () => sortThreatsByScore(analysis.threats),
    [analysis.threats],
  );

  const toggleExpanded = (index: number) => {
    setExpandedItems((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      {/* Risk Score Card */}
      <div className="glass-card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <Shield className="w-5 h-5" /> Security Assessment
          </h2>
          <span
            className={`px-4 py-1 rounded-full text-sm font-bold ${riskConfig.bgColor} ${riskConfig.textColor}`}
          >
            {analysis.risk_level} ({analysis.risk_score.toFixed(1)}/10)
          </span>
        </div>

        <p className="text-sm text-gray-400 mb-4">{riskConfig.description}</p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <StatCard
            icon={<Cpu className="w-4 h-4" />}
            label="Components"
            value={analysis.component_count}
          />
          <StatCard
            icon={<Activity className="w-4 h-4" />}
            label="Threats"
            value={analysis.threat_count}
          />
          <StatCard
            icon={<Shield className="w-4 h-4" />}
            label="Model"
            value={analysis.model_used.split("/")[0]}
          />
        </div>

        {analysis.processing_time !== undefined && (
          <p className="text-xs text-gray-500 mt-4 text-right">
            Processed in {analysis.processing_time.toFixed(2)}s
          </p>
        )}
      </div>

      {/* Threats List */}
      <div className="glass-card">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5" /> Identified Threats
        </h2>

        {threatsByScore.length === 0 ? (
          <p className="text-gray-400 text-center py-8">
            No threats identified in this diagram.
          </p>
        ) : (
          <div className="space-y-3">
            {threatsByScore.map((threat, i) => (
              <ThreatCard
                key={i}
                threat={threat}
                index={i}
                expanded={expandedItems.has(i)}
                onToggle={() => toggleExpanded(i)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Components Summary */}
      {analysis.components.length > 0 && (
        <div className="glass-card">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5" /> Architecture Components
          </h2>
          <div className="flex flex-wrap gap-2">
            {analysis.components.map((comp) => (
              <span
                key={comp.id}
                className="px-3 py-1 bg-white/5 rounded-full text-sm text-gray-300 border border-white/10"
              >
                {comp.name} <span className="text-gray-500">({comp.type})</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
}

function StatCard({ icon, label, value }: StatCardProps) {
  return (
    <div className="bg-white/5 rounded-lg p-3 text-center">
      <div className="flex items-center justify-center gap-1 text-gray-400 mb-1">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <p className="text-lg font-semibold text-white">{value}</p>
    </div>
  );
}
