import { useEffect, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Download, Play, FileText, Loader2, Sparkles, Brain, ListChecks, Lightbulb, Hammer, CheckCircle2, TriangleAlert, Copy, Wand2, XCircle } from "lucide-react";

const Card = ({ className, children }: any) => (
  <div className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className || ""}`}>{children}</div>
);
const CardHeader = ({ children, className }: any) => (
  <div className={`flex flex-col space-y-1.5 p-6 ${className || ""}`}>{children}</div>
);
const CardTitle = ({ children }: any) => (
  <h3 className="text-2xl font-semibold leading-none tracking-tight">{children}</h3>
);
const CardDescription = ({ children }: any) => (
  <p className="text-sm text-muted-foreground">{children}</p>
);
const CardContent = ({ children, className }: any) => (
  <div className={`p-6 pt-0 ${className || ""}`}>{children}</div>
);
const CardFooter = ({ children, className }: any) => (
  <div className={`flex items-center p-6 pt-0 ${className || ""}`}>{children}</div>
);

const computeApiBase = () => {
  const envBase = (import.meta as any).env?.VITE_API_BASE_URL as string | undefined;
  if (envBase) return envBase;
  try {
    const h = location.hostname;
    const p = location.port;
    const isDevLike = (
      p === "5173" ||
      p === "4173" ||
      h === "localhost" ||
      h === "127.0.0.1" ||
      h === "0.0.0.0" ||
      h.endsWith(".local") ||
      /^10\./.test(h) ||
      /^192\.168\./.test(h) ||
      (() => { const m = h.match(/^172\.(\d{1,2})\./); return !!(m && parseInt(m[1], 10) >= 16 && parseInt(m[1], 10) <= 31); })()
    );
    const defaultLocalBase = `${location.protocol}//${location.hostname}:8000`;
    const sameOriginBase = `${location.protocol}//${location.host}`;
    return isDevLike ? defaultLocalBase : sameOriginBase;
  } catch {
    return "/";
  }
};

const API_BASE = computeApiBase();

const models = ["o4-mini", "o3", "gpt-5", "gpt-5-mini", "gpt-oss-120b"] as const;

function App() {
  const [model, setModel] = useState<(typeof models)[number]>("gpt-5");
  const [seedsText, setSeedsText] = useState("");
  const [guideline, setGuideline] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reportMarkdown, setReportMarkdown] = useState<string>("");
  const [progress, setProgress] = useState<any[]>([]);
  const [counters, setCounters] = useState({ predicted: 0, kept: 0, proved: 0, accepted: 0 });
  const [predictedTotal, setPredictedTotal] = useState(0);
  type PredStatus = "pending" | "processing" | "accepted" | "accepted_both" | "failed";
  type PredItem = { id: string; statement: string; status: PredStatus };
  const [predictionItems, setPredictionItems] = useState<PredItem[]>([]);
  const [hideFailed, setHideFailed] = useState(true);
  const awaitingAcceptanceRef = useRef<string[]>([]); // FIFO of proved → accepted mapping
  const hasScrolledOnReportRef = useRef(false);

  useEffect(() => {
    if (reportMarkdown && !hasScrolledOnReportRef.current) {
      hasScrolledOnReportRef.current = true;
      try {
        window.scrollTo({ top: document.documentElement.scrollHeight, behavior: "smooth" });
      } catch {
        try {
          window.scrollTo(0, document.documentElement.scrollHeight);
        } catch {}
      }
    }
    if (!reportMarkdown) {
      hasScrolledOnReportRef.current = false;
    }
  }, [reportMarkdown]);

  const canStart = useMemo(() => seedsText.trim().length > 0 && !loading, [seedsText, loading]);

  const startResearch = async () => {
    if (!canStart) return;
    setLoading(true);
    setError(null);
    setReportMarkdown("");
    setProgress([]);
    setCounters({ predicted: 0, kept: 0, proved: 0, accepted: 0 });
    setPredictedTotal(0);
    setPredictionItems([]);
    awaitingAcceptanceRef.current = [];
    try {
      const resp = await fetch(`${API_BASE}/report/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seeds: seedsText, research_guideline: guideline || null, model }),
      });
      if (!resp.ok || !resp.body) {
        const detail = await resp.json().catch(() => ({} as any));
        throw new Error(detail?.detail || `HTTP ${resp.status}`);
      }
      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf("\n")) >= 0) {
          const line = buf.slice(0, idx).trim();
          buf = buf.slice(idx + 1);
          if (!line) continue;
          try {
            const evt = JSON.parse(line);
            setProgress((prev) => [...prev, evt]);
            if (evt.phase === "prediction" && evt.status === "done") {
              const list: string[] = Array.isArray(evt.predictions) ? evt.predictions : [];
              setCounters((c) => ({ ...c, predicted: evt.count || list.length || 0 }));
              const total = (evt.count || list.length || 0) as number;
              setPredictedTotal(total);
              if (list.length) {
                setPredictionItems(list.map((s: string) => ({ id: s, statement: s, status: "pending" })));
              }
            } else if (evt.phase === "novelty" && evt.status === "done") {
              setCounters((c) => ({ ...c, kept: evt.kept || 0 }));
              const kept: string[] = Array.isArray(evt.statements) ? evt.statements : [];
              if (kept.length) {
                setPredictionItems((items) => {
                  const keptSet = new Set(kept);
                  return items.map((it) => (
                    keptSet.has(it.id)
                      ? { ...it, status: "processing" }
                      : { ...it, status: "failed" }
                  ));
                });
              }
            } else if (evt.phase === "proving" && evt.status === "proved") {
              setCounters((c) => ({ ...c, proved: c.proved + 1 }));
              const s = String(evt.statement || "");
              if (s) awaitingAcceptanceRef.current.push(s);
            } else if (evt.phase === "proving" && evt.status === "accepted") {
              setCounters((c) => ({ ...c, accepted: c.accepted + 1 }));
              const s = String(evt.statement || awaitingAcceptanceRef.current.shift() || "");
              if (s) setPredictionItems((items) => items.map((it) => it.id === s ? { ...it, status: it.status === "accepted_both" ? it.status : "accepted" } : it));
            } else if (evt.phase === "proving" && evt.status === "accepted_both") {
              const s = String(evt.statement || "");
              if (s) setPredictionItems((items) => items.map((it) => it.id === s ? { ...it, status: "accepted_both" } : it));
              else {
                setPredictionItems((items) => {
                  const idxAccepted = (() => {
                    for (let i = items.length - 1; i >= 0; i--) {
                      if (items[i].status === "accepted") return i;
                    }
                    return -1;
                  })();
                  if (idxAccepted >= 0) {
                    const clone = items.slice();
                    clone[idxAccepted] = { ...clone[idxAccepted], status: "accepted_both" };
                    return clone;
                  }
                  const fallback = awaitingAcceptanceRef.current.shift();
                  if (fallback) {
                    return items.map((it) => it.id === fallback ? { ...it, status: "accepted_both" } : it);
                  }
                  return items;
                });
              }
            } else if (evt.phase === "complete" && typeof evt.report_markdown === "string") {
              setReportMarkdown(evt.report_markdown);
            } else if (evt.phase === "error" && evt.error) {
              setError(String(evt.error));
            } else if (evt.phase === "proving" && evt.status === "failed") {
              const s = String(evt.statement || "");
              if (s) {
                setPredictionItems((items) => items.map((it) => it.id === s ? { ...it, status: "failed" } : it));
                awaitingAcceptanceRef.current = awaitingAcceptanceRef.current.filter((x) => x !== s);
              }
            }
          } catch {}
        }
      }
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    const text = reportMarkdown || "";
    const blob = new Blob([text], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "research_report.md";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const copyReport = async () => {
    try {
      await navigator.clipboard.writeText(reportMarkdown || "");
    } catch {}
  };

  const phaseIcon = (phase: string, status?: string) => {
    if (phase === "prediction") return <Lightbulb className="h-4 w-4 text-yellow-500" />;
    if (phase === "novelty") return <Sparkles className="h-4 w-4 text-fuchsia-500" />;
    if (phase === "proving") {
      if (status === "accepted") return <CheckCircle2 className="h-4 w-4 text-emerald-500" />;
      return <Hammer className="h-4 w-4 text-blue-500" />;
    }
    if (phase === "complete") return <CheckCircle2 className="h-4 w-4 text-emerald-600" />;
    if (phase === "error") return <TriangleAlert className="h-4 w-4 text-red-500" />;
    return <FileText className="h-4 w-4" />;
  };

  return (
    <div className="min-h-screen w-screen bg-background text-foreground">
      <div className="mx-auto max-w-4xl px-4 py-6">
        <div className="relative overflow-hidden rounded-xl border bg-gradient-to-r from-violet-600 via-fuchsia-600 to-rose-600 text-white animate-gradient">
          <div className="px-5 py-6 flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-white/15 backdrop-blur flex items-center justify-center">
              <Wand2 className="h-6 w-6" />
            </div>
            <div>
              <div className="text-lg font-semibold tracking-tight flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Research Report Generator
              </div>
              <div className="text-white/80 text-sm mt-0.5 flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                Generate KaTeX-ready Markdown from seeds and guidelines
              </div>
            </div>
          </div>
        </div>

        <Card className="mt-6 transition-all duration-300 hover:shadow-lg animate-fade-in-up">
          <CardHeader>
            <CardTitle>Configuration</CardTitle>
            <CardDescription>Choose model, enter seed(s) and an optional research guideline.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="sm:col-span-1">
                <label htmlFor="model" className="text-sm font-medium inline-flex items-center gap-1.5">
                  <Brain className="h-4 w-4 text-primary" /> Model
                </label>
                <select
                  id="model"
                  className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={model}
                  onChange={(e) => setModel(e.target.value as (typeof models)[number])}
                >
                  {models.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
              <div className="sm:col-span-2">
                <label htmlFor="guideline" className="text-sm font-medium inline-flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-fuchsia-600" /> Research guideline (optional)
                </label>
                <Textarea
                  id="guideline"
                  className="mt-1"
                  placeholder="e.g., advance results in convex optimization regarding gradient flow"
                  value={guideline}
                  onChange={(e) => setGuideline(e.target.value)}
                  rows={3}
                />
              </div>
            </div>

            <div>
              <label htmlFor="seeds" className="text-sm font-medium inline-flex items-center gap-1.5">
                <ListChecks className="h-4 w-4 text-blue-600" /> Seed result(s)
              </label>
              <Textarea
                id="seeds"
                className="mt-1"
                placeholder={`Paste a single LaTeX result or a list like in seed files.\n- Single example: see backend/seeds/seed_memory.txt\n- Multiple example: see backend/seeds/seed_convex.txt`}
                value={seedsText}
                onChange={(e) => setSeedsText(e.target.value)}
                rows={10}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Accepts a single statement or a bracketed list of quoted statements (raw LaTeX allowed).
              </p>
          </div>
          </CardContent>
          <CardFooter className="flex items-center justify-between">
            <div className="text-sm text-destructive h-5 inline-flex items-center gap-1">
              {error ? <TriangleAlert className="h-4 w-4" /> : null}
              {error ? error : "\u00A0"}
            </div>
            <Button onClick={startResearch} disabled={!canStart}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Running…
                </>
              ) : (
                <>
                  <Play className="mr-2 h-4 w-4" />
                  Start
                </>
              )}
            </Button>
          </CardFooter>
        </Card>

        {progress.length > 0 && (
          <Card className="mt-6 transition-all duration-300 hover:shadow-lg animate-fade-in-up">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="inline-flex items-center gap-2"><Sparkles className="h-5 w-5" /> Progress</CardTitle>
                  <CardDescription>Live updates with phases and results</CardDescription>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <div className="inline-flex items-center gap-1"><Lightbulb className="h-4 w-4 text-yellow-600" /> {counters.predicted}</div>
                  <div className="inline-flex items-center gap-1"><Sparkles className="h-4 w-4 text-fuchsia-600" /> {counters.kept}</div>
                  <div className="inline-flex items-center gap-1"><Hammer className="h-4 w-4 text-blue-600" /> {counters.proved}</div>
                  <div className="inline-flex items-center gap-1"><CheckCircle2 className="h-4 w-4 text-emerald-600" /> {counters.accepted}</div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Predictions todo-style list when available */}
              {predictionItems.length > 0 && (
                <div className="mb-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-sm font-medium inline-flex items-center gap-2">
                      <ListChecks className="h-4 w-4 text-blue-600" /> Predictions ({predictionItems.filter(i=>i.status!=='failed').length}/{predictedTotal || counters.predicted})
                    </div>
                    <label className="text-xs inline-flex items-center gap-2 select-none cursor-pointer">
                      <input
                        type="checkbox"
                        className="h-3.5 w-3.5 accent-blue-600"
                        checked={hideFailed}
                        onChange={(e)=>setHideFailed(e.target.checked)}
                      />
                      Hide failed
                    </label>
                  </div>
                  <ul className="grid gap-3 sm:grid-cols-2">
                    {(hideFailed ? predictionItems.filter(i=>i.status!=="failed") : predictionItems).map((item) => {
                      const statusBadge = (
                        item.status === 'accepted_both' ? <Badge className="bg-emerald-700 text-white border-emerald-800">Verified</Badge>
                        : item.status === 'accepted' ? <Badge className="bg-emerald-600 text-white border-emerald-700">Accepted</Badge>
                        : item.status === 'processing' ? <Badge className="bg-blue-600 text-white border-blue-700">Checking</Badge>
                        : item.status === 'pending' ? <Badge className="bg-amber-500 text-white border-amber-600">Pending</Badge>
                        : <Badge className="bg-red-500 text-white border-red-600">Failed</Badge>
                      );
                      return (
                        <li key={item.id} className={`rounded-lg border p-3 transition-colors bg-card/60 hover:bg-accent/40 ${item.status==='accepted' ? 'border-emerald-300/50' : item.status==='failed' ? 'opacity-75' : ''}`}>
                          <div className="flex items-start gap-2">
                            <div className="mt-0.5">
                              {item.status === 'accepted' || item.status === 'accepted_both' ? (
                                <CheckCircle2 className={`h-4 w-4 ${item.status==='accepted_both' ? 'text-emerald-700' : 'text-emerald-600'}`} />
                              ) : item.status === 'failed' ? (
                                <XCircle className="h-4 w-4 text-red-500" />
                              ) : (
                                <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                              )}
                            </div>
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center justify-between gap-2 mb-1">
                                <div className="shrink-0">{statusBadge}</div>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  aria-label="Copy prediction"
                                  className="h-7 w-7"
                                  onClick={async()=>{ try { await navigator.clipboard.writeText(item.statement); } catch{} }}
                                >
                                  <Copy className="h-4 w-4" />
                                </Button>
                              </div>
                              <div className={`prose dark:prose-invert max-w-none text-sm whitespace-pre-wrap ${item.status === 'failed' ? 'line-through text-muted-foreground' : ''}`}>
                                {item.statement}
                              </div>
                              {item.status === 'processing' && (
                                <div className="mt-2 h-1 w-full overflow-hidden rounded bg-muted">
                                  <div className="h-full w-1/2 animate-gradient bg-gradient-to-r from-blue-500 via-fuchsia-500 to-rose-500" />
                                </div>
                              )}
                            </div>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
              <ScrollArea className="h-48 pr-3">
                <ul className="text-sm space-y-1">
                  {progress.map((p, i) => (
                    <li key={i} className="text-muted-foreground flex items-start gap-2 animate-fade-in-up">
                      <div className="mt-0.5">{phaseIcon(p.phase, p.status)}</div>
                      <div className="min-w-0">
                        <span className="text-foreground font-medium">{p.phase}</span> {p.status || ""}
                        {p.statement ? ` — ${String(p.statement).slice(0, 80)}` : ""}
                      </div>
                    </li>
                  ))}
                </ul>
              </ScrollArea>
            </CardContent>
          </Card>
        )}

        {reportMarkdown && (
          <Card className="mt-8 transition-all duration-300 hover:shadow-lg animate-fade-in-up">
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <div>
                <CardTitle>Report</CardTitle>
                <CardDescription>Rendered with KaTeX. You can download the Markdown.</CardDescription>
              </div>
              <div className="flex items-center gap-1">
                <Button variant="ghost" size="icon" onClick={copyReport} aria-label="Copy report">
                  <Copy className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon" onClick={downloadReport} aria-label="Download report">
                  <Download className="h-5 w-5" />
                </Button>
              </div>
            </CardHeader>
            <Separator />
            <CardContent className="mt-4">
              <ScrollArea className="h-[70vh] pr-4">
                <div className="prose dark:prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                    {reportMarkdown}
                  </ReactMarkdown>
            </div>
          </ScrollArea>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

export default App;
