import { ExternalLink, FileText } from "lucide-react";

export type SourceInfo = {
  id: string;
  url?: string | null;
  title?: string | null;
};

export type SourceRecord = {
  id: string;
  url?: string | null;
  title?: string | null;
  source_type?: string | null;
  authority_tier?: number | null;
};

type EvidenceRecord = {
  source_id?: string;
  source_url?: string | null;
  source_title?: string | null;
};

type SpecificationWithEvidence = {
  evidence?: EvidenceRecord[];
};

export function buildSourceMap(
  sources: SourceRecord[] | undefined,
  specifications: Record<string, SpecificationWithEvidence>
): Map<string, SourceInfo> {
  const map = new Map<string, SourceInfo>();

  for (const source of sources ?? []) {
    if (!source.id) {
      continue;
    }

    map.set(source.id, {
      id: source.id,
      url: source.url,
      title: source.title,
    });
  }

  for (const specification of Object.values(specifications)) {
    for (const evidence of specification.evidence ?? []) {
      const sourceId = evidence.source_id;

      if (!sourceId) {
        continue;
      }

      const existing = map.get(sourceId);

      map.set(sourceId, {
        id: sourceId,
        url: existing?.url ?? evidence.source_url,
        title: existing?.title ?? evidence.source_title,
      });
    }
  }

  return map;
}

export function getSourceLabel(
  sourceId: string,
  sourceMap: Map<string, SourceInfo>
): string {
  const source = sourceMap.get(sourceId);

  if (!source) {
    return sourceId;
  }

  return source.title || truncateUrl(source.url) || source.id;
}

function truncateUrl(url?: string | null): string | undefined {
  if (!url) {
    return undefined;
  }

  try {
    const hostname = new URL(url).hostname.replace(/^www\./, "");
    return hostname;
  } catch {
    return url;
  }
}

type SourceLinkProps = {
  sourceId: string;
  sourceMap: Map<string, SourceInfo>;
  className?: string;
  showIcon?: boolean;
  externalIcon?: boolean;
};

export default function SourceLink({
  sourceId,
  sourceMap,
  className = "",
  showIcon = true,
  externalIcon = false,
}: SourceLinkProps) {
  const source = sourceMap.get(sourceId);
  const label = getSourceLabel(sourceId, sourceMap);
  const url = source?.url;

  if (url) {
    return (
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className={`source-link ${className}`.trim()}
        title={url}
      >
        {showIcon ? (
          externalIcon ? (
            <ExternalLink size={12} strokeWidth={2} />
          ) : (
            <FileText size={14} strokeWidth={2} />
          )
        ) : null}
        <span>{label}</span>
      </a>
    );
  }

  return (
    <span
      className={`source-link source-link--unlinked ${className}`.trim()}
      title={sourceId}
    >
      {showIcon ? <FileText size={14} strokeWidth={2} /> : null}
      <span>{label}</span>
    </span>
  );
}

type SourceLinkListProps = {
  sourceIds: string[];
  sourceMap: Map<string, SourceInfo>;
  className?: string;
  itemClassName?: string;
};

export function SourceLinkList({
  sourceIds,
  sourceMap,
  className = "",
  itemClassName = "",
}: SourceLinkListProps) {
  const uniqueIds = Array.from(new Set(sourceIds));

  if (!uniqueIds.length) {
    return null;
  }

  return (
    <ul className={className}>
      {uniqueIds.map((sourceId) => (
        <li key={sourceId} className={itemClassName}>
          <SourceLink sourceId={sourceId} sourceMap={sourceMap} />
        </li>
      ))}
    </ul>
  );
}

type SourceTagListProps = {
  sourceIds: string[];
  sourceMap: Map<string, SourceInfo>;
  className?: string;
};

export function SourceTagList({
  sourceIds,
  sourceMap,
  className = "source-tags",
}: SourceTagListProps) {
  const uniqueIds = Array.from(new Set(sourceIds));

  if (!uniqueIds.length) {
    return null;
  }

  return (
    <div className={className}>
      {uniqueIds.map((sourceId) => (
        <SourceLink
          key={sourceId}
          sourceId={sourceId}
          sourceMap={sourceMap}
          className="source-tag"
          showIcon={false}
          externalIcon
        />
      ))}
    </div>
  );
}
