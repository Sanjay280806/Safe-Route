import type { BlockedReport, User } from "../types";

interface ReportStatusPanelProps {
  reports: BlockedReport[];
  user: User | null;
  onVerify: (report: BlockedReport, decision: "confirm" | "reject") => void;
}

export function ReportStatusPanel({ reports, user, onVerify }: ReportStatusPanelProps) {
  return (
    <section className="panel reports-panel">
      <div className="panel-heading">
        <div><p className="eyebrow">Field intelligence</p><h2>Active reports</h2></div>
        <span className="count-pill danger">{reports.filter((report) => report.verification_status !== "rejected").length}</span>
      </div>
      {reports.length === 0 ? <p className="safe-message">No active field reports.</p> : null}
      <div className="report-list">
        {reports.map((report) => (
          <article className="report-row" key={report.id}>
            <span className={`report-status-dot ${report.verification_status}`} />
            <div>
              <strong>{report.road_name}</strong>
              <p>{report.note}</p>
              <small>{report.source.replace(/_/g, " ")} · {report.verification_status}</small>
            </div>
            {user?.role === "admin" && report.verification_status === "pending" ? (
              <span className="admin-verify-actions">
                <button type="button" onClick={() => onVerify(report, "confirm")}>Confirm</button>
                <button type="button" onClick={() => onVerify(report, "reject")}>Reject</button>
              </span>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
