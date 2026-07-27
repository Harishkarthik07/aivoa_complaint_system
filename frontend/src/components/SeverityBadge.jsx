export default function SeverityBadge({ severity }) {
  if (!severity) return <span className="badge neutral">Pending</span>
  const cls = severity.toLowerCase()
  return <span className={`badge ${cls}`}>{severity}</span>
}
