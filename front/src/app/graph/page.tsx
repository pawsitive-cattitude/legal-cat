"use client";
import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

// ClauseGraphComponent.tsx
// Default export: ClauseGraph
// Tailwind-ready React component to visualize clauses (nodes) and connections (edges).
// - Hover/click nodes to view text
// - Search on the right; clicking a result centers + highlights the node
// - Accepts `nodes` and `links` props so you can pass RAG-extracted data easily
//
// Usage (in Next.js):
// import ClauseGraph, { sampleData } from "./ClauseGraphComponent";
// <ClauseGraph nodes={sampleData.nodes} links={sampleData.links} width={1000} height={700} />
//
// Data shape expected:
// nodes: [{ id: string, label?: string, text?: string, type?: string }]
// links: [{ source: string, target: string, relation?: string }]
//
// Notes on integration with RAG: when you extract clauses from a document, create a node
// per clause with `id` (unique), `label` (short title), `text` (full clause text), and add
// links representing "affects", "references", "depends-on" etc. Pass them as props.

type NodeDatum = {
  id: string;
  label?: string;
  text?: string;
  type?: string;
};

type LinkDatum = {
  source: string;
  target: string;
  relation?: string;
};

export const sampleData: { nodes: NodeDatum[]; links: LinkDatum[] } = {
  nodes: [
    {
      id: "clause_1",
      label: "Term of Lease",
      text: "Lease duration is 12 months starting from Sep 1, 2025. Tenant may terminate early only under clause 7.",
      type: "core",
    },
    {
      id: "clause_2",
      label: "Automatic Renewal",
      text: "The lease automatically renews for 24 months unless tenant gives 90 days notice. Renewal notice handled by landlord agent (email only).",
      type: "suspicious",
    },
    {
      id: "clause_3",
      label: "Early Termination Fee",
      text: "If tenant terminates early, a fee equal to 6 months' rent is charged unless landlord consents in writing.",
      type: "penalty",
    },
    {
      id: "clause_4",
      label: "Notice Period",
      text: "All notices must be provided in writing and delivered to the address in Schedule A or to landlord@example.com.",
      type: "procedural",
    },
    {
      id: "clause_5",
      label: "Agent Authority",
      text: "Landlord's agent may accept notices on behalf of landlord; agent's decisions are final.",
      type: "authority",
    },
    {
      id: "clause_6",
      label: "Security Deposit",
      text: "Deposit refundable within 30 days minus deductions for damages. Deductions calculated at landlord's discretion.",
      type: "financial",
    },
    {
      id: "clause_7",
      label: "Special Early Exit",
      text: "Tenant may terminate early without fee if they obtain a replacement tenant approved by landlord within 30 days.",
      type: "exception",
    },
    {
      id: "clause_8",
      label: "Maintenance Duties",
      text: "Tenant responsible for routine maintenance (changing lightbulbs, unclogging drains). Landlord responsible for structural issues.",
      type: "responsibility",
    },
    {
      id: "clause_9",
      label: "Late Rent Penalty",
      text: "Late payments incur $100 penalty plus 5% of outstanding rent per month.",
      type: "penalty",
    },
    {
      id: "clause_10",
      label: "Inspection Rights",
      text: "Landlord may inspect the premises with 24 hours notice, except in emergencies when immediate access is allowed.",
      type: "procedural",
    },
    {
      id: "clause_11",
      label: "Full Moon Exit Penalty",
      text: "If tenant vacates during a full moon, landlord reserves right to impose extraordinary penalties. (Clearly suspicious).",
      type: "suspicious",
    },
    {
      id: "clause_12",
      label: "Rent Increase",
      text: "Rent may be increased annually by up to 15% at landlord's discretion with 30 days notice.",
      type: "financial",
    },
    {
      id: "clause_13",
      label: "Utilities Payment",
      text: "Tenant is responsible for water, gas, and electricity bills. Internet and trash included in rent.",
      type: "responsibility",
    },
    {
      id: "clause_14",
      label: "Insurance Requirement",
      text: "Tenant must maintain renter's insurance covering at least $50,000 in liability.",
      type: "financial",
    },
    {
      id: "clause_15",
      label: "Pet Policy",
      text: "Pets allowed only with landlord approval. Additional $500 deposit required.",
      type: "responsibility",
    },
  ],
  links: [
    {
      source: "clause_1",
      target: "clause_2",
      relation: "renewal_affects_duration",
    },
    { source: "clause_2", target: "clause_4", relation: "notice_requirement" },
    {
      source: "clause_4",
      target: "clause_5",
      relation: "agent_receives_notice",
    },
    {
      source: "clause_3",
      target: "clause_1",
      relation: "penalty_for_early_termination",
    },
    {
      source: "clause_7",
      target: "clause_3",
      relation: "exception_reduces_penalty",
    },
    { source: "clause_6", target: "clause_3", relation: "deposit_may_cover" },
    {
      source: "clause_2",
      target: "clause_5",
      relation: "agent_handles_renewal_notice",
    },
    {
      source: "clause_9",
      target: "clause_6",
      relation: "deposit_used_for_penalty",
    },
    {
      source: "clause_10",
      target: "clause_8",
      relation: "inspection_affects_maintenance",
    },
    {
      source: "clause_11",
      target: "clause_7",
      relation: "suspicious_exception",
    },
    {
      source: "clause_12",
      target: "clause_1",
      relation: "rent_increase_affects_term",
    },
    {
      source: "clause_12",
      target: "clause_2",
      relation: "increase_rolls_into_renewal",
    },
    {
      source: "clause_13",
      target: "clause_6",
      relation: "utilities_affect_deposit",
    },
    {
      source: "clause_14",
      target: "clause_1",
      relation: "insurance_linked_to_term",
    },
    {
      source: "clause_15",
      target: "clause_6",
      relation: "pet_policy_affects_deposit",
    },
  ],
};

export default function ClauseGraph({
  nodes = sampleData.nodes,
  links = sampleData.links,
  width = 1000,
  height = 700,
}: {
  nodes?: NodeDatum[];
  links?: LinkDatum[];
  width?: number;
  height?: number;
}) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [selected, setSelected] = useState<NodeDatum | null>(null);
  const [hovered, setHovered] = useState<NodeDatum | null>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<NodeDatum[]>([]);
  const simulationRef = useRef<any>(null);
  const gRef = useRef<SVGGElement | null>(null);
  const zoomRef = useRef<any>(null);

  // Build maps for quick lookup
  const nodeById = useRef(new Map<string, NodeDatum>());
  useEffect(() => {
    nodeById.current.clear();
    nodes.forEach((n) => nodeById.current.set(n.id, n));
  }, [nodes]);

  // Initialize SVG + force simulation
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const g = svg.append("g").attr("class", "graph-root");
    gRef.current = g.node() as unknown as SVGGElement;

    const defs = svg.append("defs");

    // arrow marker
    defs
      .append("marker")
      .attr("id", "arrow")
      .attr("viewBox", "0 -5 10 10")
      .attr("refX", 25)
      .attr("refY", 0)
      .attr("markerWidth", 6)
      .attr("markerHeight", 6)
      .attr("orient", "auto")
      .append("path")
      .attr("d", "M0,-5L10,0L0,5")
      .attr("fill", "#888");

    // zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 3])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });

    zoomRef.current = zoom;
    svg.call(zoom as any);

    // create link and node selections
    const link = g
      .append("g")
      .attr("class", "links")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 1.2)
      .attr("stroke", "#999")
      .attr("marker-end", "url(#arrow)");

    const node = g
      .append("g")
      .attr("class", "nodes")
      .selectAll("g")
      .data(nodes)
      .join((enter) => {
        const gnode = enter.append("g");
        gnode
          .append("circle")
          .attr("r", 18)
          .attr("stroke", "#333")
          .attr("stroke-width", 1.2);
        gnode
          .append("text")
          .attr("dy", 4)
          .attr("x", 0)
          .attr("text-anchor", "middle")
          .attr("font-size", 10);
        return gnode;
      });

    node.select("circle").attr("fill", (d: any) => {
      switch (d.type) {
        case "suspicious":
          return "#ffefc2"; // pale yellow
        case "penalty":
          return "#ffd6d6"; // pale red
        case "financial":
          return "#d6eaff"; // pale blue
        default:
          return "#e6f9e6"; // pale green
      }
    });

    node.select("text").text((d: any) => d.label || d.id);

    // tooltip div
    const container = d3
      .select("body")
      .append("div")
      .attr("class", "clause-tooltip hidden");
    container
      .style("position", "absolute")
      .style("pointer-events", "none")
      .style("max-width", "320px")
      .style("padding", "8px")
      .style("border-radius", "6px")
      .style("box-shadow", "0 4px 12px rgba(0,0,0,0.15)")
      .style("background", "white")
      .style("font-size", "13px")
      .style("z-index", "9999");

    // simulation
    const sim = d3
      .forceSimulation(nodes as any)
      .force(
        "link",
        d3
          .forceLink(links as any)
          .id((d: any) => d.id)
          .distance(140)
          .strength(0.8)
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide(28));

    simulationRef.current = sim;

    const drag = (simulation: any) => {
      function dragstarted(event: any, d: any) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }

      function dragged(event: any, d: any) {
        d.fx = event.x;
        d.fy = event.y;
      }

      function dragended(event: any, d: any) {
        if (!event.active) simulation.alphaTarget(0);
        // keep node frozen where it is so user can inspect
        d.fx = d.x;
        d.fy = d.y;
      }

      return d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    };

    node.call(drag(sim));

    node
      .on("mouseover", function (event: any, d: any) {
        container
          .classed("hidden", false)
          .html(
            `<strong>${d.label || d.id}</strong><div style='margin-top:6px'>${(
              d.text || ""
            ).slice(0, 240)}${(d.text || "").length > 240 ? "..." : ""}</div>`
          );
        setHovered(d);
      })
      .on("mousemove", function (event: any) {
        container
          .style("left", event.pageX + 12 + "px")
          .style("top", event.pageY + 12 + "px");
      })
      .on("mouseout", function () {
        container.classed("hidden", true);
        setHovered(null);
      })
      .on("click", function (event: any, d: any) {
        setSelected(d);
      });

    sim.on("tick", () => {
      link
        .attr("x1", (l: any) => (l.source as any).x)
        .attr("y1", (l: any) => (l.source as any).y)
        .attr("x2", (l: any) => (l.target as any).x)
        .attr("y2", (l: any) => (l.target as any).y);

      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    // cleanup on unmount
    return () => {
      sim.stop();
      svg.selectAll("*").remove();
      container.remove();
    };
  }, [nodes, links, width, height]);

  // Search handler
  useEffect(() => {
    if (!query) return setResults([]);
    const q = query.toLowerCase();
    const matches = nodes.filter((n) =>
      ((n.label || "") + " " + (n.text || "")).toLowerCase().includes(q)
    );
    setResults(matches.slice(0, 60));
  }, [query, nodes]);

  // center node utility
  const centerNode = (nodeId: string) => {
    if (!gRef.current || !svgRef.current) return;
    const node = nodes.find((n) => n.id === nodeId);
    if (!node) return;

    // if simulation has positions, use them; otherwise approximate center
    // we can access d.x,d.y because d3 stored them on our node objects
    // @ts-ignore
    const x = (node as any).x ?? width / 2;
    // @ts-ignore
    const y = (node as any).y ?? height / 2;

    const svg = d3.select(svgRef.current);
    const transform = d3.zoomTransform(svg.node() as any);
    const scale = transform.k;

    const tx = width / 2 - x * scale;
    const ty = height / 2 - y * scale;

    svg
      .transition()
      .duration(550)
      .call(
        zoomRef.current.transform,
        d3.zoomIdentity
          .translate(tx, ty)
          .scale(scale) as any as d3.ZoomTransform
      );

    // also briefly flash the node
    flashNode(nodeId);
  };

  const flashNode = (nodeId: string) => {
    // add a temporary highlight by selecting circle and animating stroke
    const svg = d3.select(svgRef.current);
    const node = svg.selectAll(".nodes g").filter((d: any) => d.id === nodeId);
    node
      .select("circle")
      .transition()
      .duration(150)
      .attr("r", 26)
      .transition()
      .duration(250)
      .attr("r", 18);
  };

  return (
    <div className="flex gap-4" style={{ width: width + 320 }}>
      <div className="flex-1 bg-white rounded-lg shadow p-2" style={{ width }}>
        <svg
          ref={svgRef}
          width={width}
          height={height}
          style={{ background: "#fafafa", borderRadius: 8 }}
        />
      </div>

      <div
        className="w-80 bg-white rounded-lg shadow p-4 flex flex-col"
        style={{ maxHeight: height }}
      >
        <div className="mb-3">
          <h3 className="text-lg font-semibold">Clause search</h3>
          <p className="text-sm text-slate-500">
            Search labels or text. Click result to center.
          </p>
        </div>

        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Find clause by keyword..."
          className="w-full border rounded p-2 mb-2"
        />

        <div className="flex-1 overflow-auto">
          {results.length === 0 && query && (
            <div className="text-sm text-slate-500">No matches</div>
          )}
          <ul>
            {results.map((r) => (
              <li
                key={r.id}
                className="cursor-pointer p-2 rounded hover:bg-slate-50"
                onClick={() => {
                  centerNode(r.id);
                  setSelected(r);
                }}
              >
                <div className="font-medium text-sm">{r.label || r.id}</div>
                <div className="text-xs text-slate-500 truncate">
                  {(r.text || "").slice(0, 140)}
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-3 border-t pt-3">
          <h4 className="text-sm font-semibold mb-1">Selected clause</h4>
          {selected ? (
            <div>
              <div className="font-medium">{selected.label || selected.id}</div>
              <div className="text-xs text-slate-600 mt-2 whitespace-pre-wrap">
                {selected.text}
              </div>
            </div>
          ) : (
            <div className="text-sm text-slate-500">
              Click a node or search a clause to view full text.
            </div>
          )}
        </div>

        <div className="mt-3 text-xs text-slate-400">
          <div>
            Tip: pass `nodes` and `links` props with RAG-extracted data. Each
            node should include `id`, `label`, and `text`.
          </div>
        </div>
      </div>
    </div>
  );
}
