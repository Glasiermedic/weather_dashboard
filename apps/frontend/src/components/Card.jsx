export default function Card({ title, children, className = "" }) {
  return (
    <section
      className={[
        "rounded-xl border border-slate-200 bg-white shadow-sm",
        "p-4",
        "flex flex-col",
        className,
      ].join(" ")}
    >
      {title ? (
        <header className="mb-3">
          <h2 className="text-sm font-semibold text-slate-800">{title}</h2>
        </header>
      ) : null}

      {/* Makes inner content stretch nicely */}
      <div className="flex-1 min-h-0">{children}</div>
    </section>
  );
}
