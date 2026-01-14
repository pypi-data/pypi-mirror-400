"""Edge building for the instantiated output graph.

Reference:
https://ratio-case.gitlab.io/docs/reference/esl_reference/dependency-derivations.html
"""

from collections import defaultdict
from copy import deepcopy
from itertools import chain
from typing import Any, Dict, Generator, Iterable, List, Optional, Set, Tuple

from ragraph.edge import Edge
from ragraph.node import Node

from raesl import logger
from raesl.compile import diagnostics
from raesl.compile.instantiating.node_building import NodeStore


class EdgeStore:
    """Edge storage with multiple categories for quicker access to specific subsets."""

    categories = ["edges"]  # Updated in EdgeFactory init.

    def __init__(self):
        for cat in self.categories:
            setattr(self, cat, list())

    def clear(self):
        """Clear all edge categories."""
        for cat in self.categories:
            getattr(self, cat).clear()

    def add(self, edge: Edge, *args):
        """Add node to :obj:`self.nodes` and any other specified maps in args."""
        self.edges.append(edge)
        for m in args:
            getattr(self, m).append(edge)
        logger.debug(f"Added ragraph.edge.Edge {edge} to edges and {args}.")

    def consume(self, edges: Iterable[Edge], *args):
        """Add any edges from an iterable to given categories."""
        for e in edges:
            self.add(e, *args)


class EdgeFactory:
    def __init__(
        self,
        diag_store: diagnostics.DiagnosticStore,
        node_store: Optional[NodeStore] = None,
    ):
        self.diag_store = diag_store
        self.node_store = node_store

        # Set categories dynamically.
        EdgeStore.categories = ["edges"] + [i[6:] for i in dir(self) if i.startswith("_make_")]
        self.edge_store = EdgeStore()

    def _add(self, edge: Edge, *args):
        """Proxy for :obj:`EdgeStore.add`."""
        self.edge_store.add(edge, *args)

    def _consume(self, edges: Iterable[Edge], *args):
        """Proxy for :obj:`EdgeStore.consume`."""
        self.edge_store.consume(edges, *args)

    def _make(self, cat: str) -> List[Edge]:
        """Make an edge category if it is still empty and return it for quick access."""
        if not getattr(self.edge_store, cat):
            func = getattr(self, f"_make_{cat}")
            func()

        return getattr(self.edge_store, cat)

    def make_edges(self, node_store: Optional[NodeStore] = None) -> List[Edge]:
        """Derive edges from a :obj:`NodeStore` object."""
        # Clear edge lists
        self.edge_store.clear()

        # Set provided node_store or try an keep the current one.
        self.node_store = self.node_store if node_store is None else node_store
        if self.node_store is None:
            return list()

        for cat in self.edge_store.categories:
            # Make edges if list is empty. This guarantees each category is only
            # generated once regardless of them calling eachother internally.
            if cat == "edges":
                continue
            self._make(cat)

        return self.edge_store.edges

    def _make_evf(self):
        """Compute functional dependencies between variable nodes."""
        nodes = self.node_store.nodes
        tfs = [
            n
            for n in self.node_store.transforms.values()
            if not nodes[n.annotations.esl_info.get("body").get("active")].children
        ]  # Only transforms where the active component doesn't have children.

        for t in tfs:
            for vi in t.annotations.esl_info["body"]["input_variables"]:
                for vj in t.annotations.esl_info["body"]["output_variables"]:
                    self._add(
                        Edge(
                            source=nodes[vi],
                            target=nodes[vj],
                            kind="functional_dependency",
                            labels=[nodes[vi].annotations.esl_info["type_ref"]],
                            annotations=dict(
                                esl_info=dict(reason=dict(function_specifications=[t.name]))
                            ),
                        ),
                        "evf",
                    )

    def _make_evb(self):
        """Compute logical dependencies between variables for behavior specs."""
        for b in self.node_store.behaviors.values():
            for c in b.annotations.esl_info["cases"]:
                self._consume(
                    _generate_evbc(behavior=b, case=c, nodes=self.node_store.nodes),
                    "evb",
                )

    def _make_evd(self):
        """Compute design dependencies between variables."""
        nodes = self.node_store.nodes
        designs = self.node_store.designs.values()
        relations = self.node_store.relations.values()

        for d in designs:
            for r in d.annotations.esl_info["body"]:
                vi = nodes[r["subject"]]

                bound = r.get("bound")
                if bound is None:
                    # Mim / max requirement
                    continue

                vj = nodes.get(bound["value"])

                if not vj:
                    continue

                self._add(
                    Edge(
                        source=vi,
                        target=vj,
                        kind="design_dependency",
                        labels=[vi.annotations.esl_info["type_ref"]],
                        annotations=dict(
                            esl_info=dict(reason=dict(design_specifications=[d.name]))
                        ),
                    ),
                    "evd",
                )

                self._add(
                    Edge(
                        source=vj,
                        target=vi,
                        kind="design_dependency",
                        labels=[vj.annotations.esl_info["type_ref"]],
                        annotations=dict(
                            esl_info=dict(reason=dict(design_specifications=[d.name]))
                        ),
                    ),
                    "evd",
                )

        for r in relations:
            for vi in (
                r.annotations.esl_info["required_variables"]
                + r.annotations.esl_info["related_variables"]
            ):
                for vj in (
                    r.annotations.esl_info["returned_variables"]
                    + r.annotations.esl_info["related_variables"]
                ):
                    if vi == vj:
                        continue

                    self._add(
                        Edge(
                            source=nodes[vi],
                            target=nodes[vj],
                            kind="design_dependency",
                            labels=[nodes[vi].annotations.esl_info["type_ref"]],
                            annotations=dict(
                                esl_info=dict(reason=dict(relation_specifications=[r.name]))
                            ),
                        ),
                        "evd",
                    )

    def _make_ecf(self):
        """Compute function dependencies between component nodes."""
        nodes = self.node_store.nodes
        transforms = self.node_store.transforms.values()
        goals = self.node_store.goals.values()

        nt_dict = defaultdict(list)
        for t in transforms:
            nt_dict[t.annotations.esl_info["body"]["active"]].append(t)

        for g in goals:
            src = nodes[g.annotations.esl_info["body"]["active"]]
            trg = nodes[g.annotations.esl_info["body"]["passive"]]

            lbs = [
                nodes[v].annotations.esl_info["type_ref"]
                for v in g.annotations.esl_info["body"]["variables"]
            ]

            self._add(
                Edge(
                    source=src,
                    target=trg,
                    kind="functional_dependency",
                    labels=lbs,
                    annotations=dict(esl_info=dict(reason=dict(function_specifications=[g.name]))),
                ),
                "ecf",
            )

            self._add(
                Edge(
                    source=trg,
                    target=src,
                    kind="functional_dependency",
                    labels=lbs,
                    annotations=dict(esl_info=dict(reason=dict(function_specifications=[g.name]))),
                ),
                "ecf",
            )

            gvars = set(g.annotations.esl_info["body"]["variables"])
            for c in src.descendants:
                for t in nt_dict[c.name]:
                    t_out_vars = set(t.annotations.esl_info["body"]["output_variables"])

                    shared_v = gvars.intersection(t_out_vars)
                    if not shared_v:
                        continue

                    lbs = [nodes[v].annotations.esl_info["type_ref"] for v in shared_v]
                    self._add(
                        Edge(
                            source=c,
                            target=trg,
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(reason=dict(function_specifications=[g.name, t.name]))
                            ),
                        ),
                        "ecf",
                    )

                    self._add(
                        Edge(
                            source=trg,
                            target=c,
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(reason=dict(function_specifications=[g.name, t.name]))
                            ),
                        ),
                        "ecf",
                    )

            for c in trg.descendants:
                for t in nt_dict[c.name]:
                    t_in_vars = set(t.annotations.esl_info["body"]["input_variables"])

                    shared_v = gvars.intersection(t_in_vars)
                    if not shared_v:
                        continue

                    lbs = [nodes[v].annotations.esl_info["type_ref"] for v in shared_v]
                    self._add(
                        Edge(
                            source=src,
                            target=c,
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(reason=dict(function_specifications=[t.name, g.name]))
                            ),
                        ),
                        "ecf",
                    )

                    self._add(
                        Edge(
                            source=c,
                            target=src,
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(reason=dict(function_specifications=[t.name, g.name]))
                            ),
                        ),
                        "ecf",
                    )

        for ti in transforms:
            for tj in transforms:
                ci = ti.annotations.esl_info["body"]["active"]
                cj = tj.annotations.esl_info["body"]["active"]

                if ti is tj or ci == cj:
                    continue

                ti_in_vars = set(ti.annotations.esl_info["body"]["input_variables"])
                ti_out_vars = set(ti.annotations.esl_info["body"]["output_variables"])
                tj_in_vars = set(tj.annotations.esl_info["body"]["input_variables"])
                tj_out_vars = set(tj.annotations.esl_info["body"]["output_variables"])
                shared_vars_ij = ti_out_vars.intersection(tj_in_vars)
                shared_vars_ji = tj_out_vars.intersection(ti_in_vars)

                if shared_vars_ij:
                    lbs = [nodes[v].annotations.esl_info["type_ref"] for v in shared_vars_ij]
                    self._add(
                        Edge(
                            source=nodes[ci],
                            target=nodes[cj],
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(
                                    reason=dict(function_specifications=[ti.name, tj.name])
                                )
                            ),
                        ),
                        "ecf",
                    )

                    self._add(
                        Edge(
                            source=nodes[cj],
                            target=nodes[ci],
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(
                                    reason=dict(function_specifications=[ti.name, tj.name])
                                )
                            ),
                        ),
                        "ecf",
                    )

                if shared_vars_ji:
                    lbs = [nodes[v].annotations.esl_info["type_ref"] for v in shared_vars_ji]
                    self._add(
                        Edge(
                            source=nodes[cj],
                            target=nodes[ci],
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(
                                    reason=dict(function_specifications=[tj.name, ti.name])
                                )
                            ),
                        ),
                        "ecf",
                    )

                    self._add(
                        Edge(
                            source=nodes[ci],
                            target=nodes[cj],
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(
                                    reason=dict(function_specifications=[tj.name, ti.name])
                                )
                            ),
                        ),
                        "ecf",
                    )

    def _make_ecb(self):
        """Compute logical dependencies between components."""
        nodes = self.node_store.nodes
        goals = self.node_store.goals.values()
        transforms = self.node_store.transforms.values()

        evb = self._make("evb")
        ev_dict = defaultdict(list)
        for e in evb:
            ev_dict[(e.source, e.target)].append(e)

        mfv = self._make("mfv")
        vf_dict = defaultdict(list)
        for e in mfv:
            vf_dict[e.target.name].append(e.source)

        # Check goal-goal behavior dependencies.
        for sources in [goals, transforms]:
            for targets in [goals, transforms]:
                for gi in sources:
                    for gj in targets:
                        edge = _get_component_behavior_dependency(
                            nodes=nodes,
                            src=gi,
                            trg=gj,
                            ev_dict=ev_dict,
                            vf_dict=vf_dict,
                        )
                        if edge is not None:
                            self._add(edge, "ecb")

    def _make_ecd(self):
        """Create design dependencies between components."""
        nodes = self.node_store.nodes
        cmps = self.node_store.components.values()

        evd = self._make("evd")

        e_dict = {(e.source.name, e.target.name): e for e in evd}
        for ci in cmps:
            for pi in ci.annotations.esl_info["property_variables"]:
                for cj in cmps:
                    for pj in cj.annotations.esl_info["property_variables"]:
                        if (pi, pj) not in e_dict:
                            continue

                        # Migrate edge up tree
                        for ai in [ci] + ci.ancestors:
                            for aj in [cj] + cj.ancestors:
                                if ai == aj:
                                    continue
                                self._add(
                                    Edge(
                                        source=ai,
                                        target=aj,
                                        kind="design_dependency",
                                        labels=[nodes[pi].annotations.esl_info["type_ref"]],
                                        annotations=dict(
                                            esl_info=dict(
                                                reason=e_dict[(pi, pj)].annotations.esl_info[
                                                    "reason"
                                                ]
                                            )
                                        ),
                                    ),
                                    "ecd",
                                )

    def _make_eft(self):
        """Create traceability dependencies between function specifications."""
        nodes = self.node_store.nodes
        cps = self.node_store.components.values()
        gls = self.node_store.goals.values()
        tfs = self.node_store.transforms.values()

        ctd: Dict[str, List[Node]] = defaultdict(list)
        for t in tfs:
            ctd[t.annotations.esl_info["body"]["active"]].append(t)

        cgd: Dict[str, List[Node]] = defaultdict(list)
        for g in gls:
            cgd[g.annotations.esl_info["body"]["active"]].append(g)

        for c in cps:
            if not c.children or not ctd.get(c.name):
                continue

            child_ts: List[Node] = []
            child_gs: List[Node] = []
            for child in c.children:
                child_ts.extend(ctd[child.name])
                child_gs.extend(cgd[child.name])

            evf_c = []

            for t in child_ts:
                for vi in t.annotations.esl_info["body"]["input_variables"]:
                    for vj in t.annotations.esl_info["body"]["output_variables"]:
                        evf_c.append(
                            Edge(
                                source=nodes[vi],
                                target=nodes[vj],
                                kind="functional_dependency",
                                labels=[nodes[vi].annotations.esl_info["type_ref"]],
                                annotations=dict(
                                    esl_info=dict(reason=dict(function_specifications=[t.name]))
                                ),
                            )
                        )

            for t in ctd[c.name]:
                srcs = [nodes[v] for v in t.annotations.esl_info["body"]["input_variables"]]
                trgs = [nodes[v] for v in t.annotations.esl_info["body"]["output_variables"]]

                paths = _get_paths_between_all(srcs=srcs, trgs=set(trgs), edges=evf_c)

                pathvars = set()
                for path in paths:
                    pathvars.update(set(path))

                for child_t in child_ts:
                    shared_path_variables = set(
                        child_t.annotations.esl_info["body"]["output_variables"]
                    ).intersection(pathvars)
                    if shared_path_variables:
                        shared_path_variables = sorted(shared_path_variables)
                        self._add(
                            Edge(
                                source=t,
                                target=child_t,
                                kind="traceability_dependency",
                                annotations=dict(
                                    esl_info=dict(reason=dict(path_variables=shared_path_variables))
                                ),
                            ),
                            "eft",
                        )

                for child_g in child_gs:
                    shared_path_variables = set(
                        child_g.annotations.esl_info["body"]["variables"]
                    ).intersection(pathvars)
                    if shared_path_variables:
                        shared_path_variables = sorted(shared_path_variables)
                        self._add(
                            Edge(
                                source=t,
                                target=child_g,
                                kind="traceability_dependency",
                                annotations=dict(
                                    esl_info=dict(reason=dict(path_variables=shared_path_variables))
                                ),
                            ),
                            "eft",
                        )

    def _make_eff(self):
        """Creating all functional dependencies between between goals and transforms."""
        nodes = self.node_store.nodes
        gls = self.node_store.goals.values()
        tfs = self.node_store.transforms.values()

        for t1 in tfs:
            for t2 in tfs:
                if (
                    t1.annotations.esl_info["body"]["active"]
                    != t2.annotations.esl_info["body"]["active"]
                ):
                    continue

                vout = set(t1.annotations.esl_info["body"]["output_variables"])
                vin = set(t2.annotations.esl_info["body"]["input_variables"])
                v_shared = vout.intersection(vin)

                if not v_shared:
                    continue
                v_shared = sorted(v_shared)

                lbs = [nodes[v].annotations.esl_info["type_ref"] for v in v_shared]
                self._add(
                    Edge(
                        source=t1,
                        target=t2,
                        kind="functional_dependency",
                        labels=lbs,
                        annotations=dict(esl_info=dict(reason=dict(shared_variables=v_shared))),
                    ),
                    "eff",
                )

            for g in gls:
                tvin = set(t1.annotations.esl_info["body"]["input_variables"])
                tvout = set(t1.annotations.esl_info["body"]["output_variables"])
                gv = set(g.annotations.esl_info["body"]["variables"])

                vin_shared = tvin.intersection(gv)
                if vin_shared:
                    vin_shared = sorted(vin_shared)
                    lbs = [nodes[v].annotations.esl_info["type_ref"] for v in vin_shared]
                    self._add(
                        Edge(
                            source=g,
                            target=t1,
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(reason=dict(shared_variables=vin_shared))
                            ),
                        ),
                        "eff",
                    )
                vout_shared = tvout.intersection(gv)
                if vout_shared:
                    vout_shared = sorted(vout_shared)
                    lbs = [nodes[v].annotations.esl_info["type_ref"] for v in vout_shared]
                    self._add(
                        Edge(
                            source=t1,
                            target=g,
                            kind="functional_dependency",
                            labels=lbs,
                            annotations=dict(
                                esl_info=dict(reason=dict(shared_variables=vout_shared))
                            ),
                        ),
                        "eff",
                    )

    def _make_efb(self):
        """Compute behavior dependencies between goal- and transformation specs."""
        nodes = self.node_store.nodes
        gls = self.node_store.goals.values()
        tfs = self.node_store.transforms.values()

        evb = self._make("evb")

        evdict = defaultdict(list)
        for e in evb:
            evdict[(e.source, e.target)].append(e)

        mfv = self._make("mfv")
        vf_dict = defaultdict(list)
        for e in mfv:
            vf_dict[e.target.name].append(e.source)

        for t1 in tfs:
            for t2 in tfs:
                if (
                    t1.annotations.esl_info["body"]["active"]
                    != t2.annotations.esl_info["body"]["active"]
                ):
                    continue

                edge = _get_function_behavior_dependency(
                    nodes=nodes, src=t1, trg=t2, ev_dict=evdict, vf_dict=vf_dict
                )
                if edge is not None:
                    self._add(edge, "efb")

            for g in gls:
                edge = _get_function_behavior_dependency(
                    nodes=nodes, src=t1, trg=g, ev_dict=evdict, vf_dict=vf_dict
                )
                if edge is not None:
                    self._add(edge, "efb")

                edge = _get_function_behavior_dependency(
                    nodes=nodes, src=g, trg=t1, ev_dict=evdict, vf_dict=vf_dict
                )
                if edge is not None:
                    self._add(edge, "efb")

    def _make_ehb(self):
        """Creating logical dependencies between behavior specifications."""
        nodes = self.node_store.nodes
        bhs = self.node_store.behaviors.values()

        for bi in bhs:
            for bj in bhs:
                if bi == bj:
                    continue

                vis = []
                for case in bi.annotations.esl_info["cases"]:
                    for tc in case["then_clauses"]:
                        vis.extend([nodes[r["subject"]] for r in tc["body"]])

                vjs = []
                for case in bj.annotations.esl_info["cases"]:
                    for wc in case["when_clauses"]:
                        vjs.extend([nodes[r["subject"]] for r in wc["body"]])

                shared_vars = set(vis).intersection(set(vjs))
                if not shared_vars:
                    continue
                shared_vars = sorted(shared_vars, key=lambda x: x.name)

                lbs = [v.annotations.esl_info["type_ref"] for v in shared_vars]
                self._add(
                    Edge(
                        source=bi,
                        target=bj,
                        kind="logical_dependency",
                        labels=lbs,
                        annotations=dict(
                            esl_info=dict(
                                reason=dict(shared_variables=[v.name for v in shared_vars])
                            )
                        ),
                    ),
                    "ehb",
                )

    def _make_ehc(self):
        """Creating coordination dependencies between behavior specifications."""
        nodes = self.node_store.nodes
        bhs = self.node_store.behaviors.values()

        for bi in bhs:
            for bj in bhs:
                if bi == bj:
                    continue

                vis = []
                for case in bi.annotations.esl_info["cases"]:
                    for tc in case["then_clauses"]:
                        vis.extend([nodes[r["subject"]] for r in tc["body"]])

                vjs = []
                for case in bj.annotations.esl_info["cases"]:
                    for tc in case["then_clauses"]:
                        vjs.extend([nodes[r["subject"]] for r in tc["body"]])

                shared_vars = set(vis).intersection(set(vjs))
                if not shared_vars:
                    continue
                shared_vars = sorted(shared_vars, key=lambda x: x.name)

                lbs = [v.annotations.esl_info["type_ref"] for v in shared_vars]
                self._add(
                    Edge(
                        source=bi,
                        target=bj,
                        kind="coordination_dependency",
                        labels=lbs,
                        annotations=dict(
                            esl_info=dict(
                                reason=dict(shared_variables=[v.name for v in shared_vars])
                            )
                        ),
                    ),
                    "ehc",
                )

    def _make_edc(self):
        """Create coordination dependencies between design specifications."""
        nodes = self.node_store.nodes
        dss = self.node_store.designs.values()

        for di in dss:
            vis = set()
            for r in di.annotations.esl_info["body"]:
                vis.add(nodes[r["subject"]])
            for dj in dss:
                if di == dj:
                    continue
                vjs = set()
                for r in dj.annotations.esl_info["body"]:
                    vjs.add(nodes[r["subject"]])

                shared_vars = vis.intersection(vjs)
                if not shared_vars:
                    continue
                shared_vars = sorted(shared_vars, key=lambda x: x.name)

                self._add(
                    Edge(
                        source=di,
                        target=dj,
                        kind="coordination_dependency",
                        labels=[v.annotations.esl_info["type_ref"] for v in shared_vars],
                        annotations=dict(
                            esl_info=dict(
                                reason=(dict(shared_variables=[v.name for v in shared_vars]))
                            )
                        ),
                    ),
                    "edc",
                )

    def _make_enc(self):
        """Create coordination dependencies between needs."""
        nds = self.node_store.needs.values()
        for ni in nds:
            for nj in nds:
                if ni == nj:
                    continue

                if not ni.annotations.esl_info["subject"] == nj.annotations.esl_info["subject"]:
                    continue

                self._add(
                    Edge(
                        source=ni,
                        target=nj,
                        kind="coordination_dependency",
                        labels=["shared subject"],
                        annotations=dict(
                            esl_info=dict(
                                reason=dict(shared_subject=ni.annotations.esl_info["subject"])
                            )
                        ),
                    ),
                    "enc",
                )

    def _make_erc(self):
        """Create coordination dependencies between relations."""
        nodes = self.node_store.nodes
        rls = self.node_store.relations.values()

        for ri in rls:
            for rj in rls:
                if ri == rj:
                    continue

                vris = set(
                    ri.annotations.esl_info["related_variables"]
                    + ri.annotations.esl_info["returned_variables"]
                )

                vrjs = set(
                    rj.annotations.esl_info["required_variables"]
                    + rj.annotations.esl_info["related_variables"]
                )

                shared_vars = vris.intersection(vrjs)
                if not shared_vars:
                    continue
                shared_vars = sorted(shared_vars)
                self._add(
                    Edge(
                        source=ri,
                        target=rj,
                        kind="coordination_dependency",
                        labels=[nodes[v].annotations.esl_info["type_ref"] for v in shared_vars],
                        annotations=dict(esl_info=dict(reason=dict(shared_vars=shared_vars))),
                    ),
                    "erc",
                )

    def _make_mcf(self):
        """Compute mapping relations between components and functions."""
        nodes = self.node_store.nodes
        n2c = self.node_store.components
        gls = self.node_store.goals.values()
        tfs = self.node_store.transforms.values()
        ctd = defaultdict(list)

        for t in tfs:
            ctd[nodes[t.annotations.esl_info["body"]["active"]]].append(t)
            lbs = [
                nodes[v].annotations.esl_info["type_ref"]
                for v in t.annotations.esl_info["body"]["input_variables"]
                + t.annotations.esl_info["body"]["output_variables"]
            ]

            self._add(
                Edge(
                    source=n2c[t.annotations.esl_info["body"]["active"]],
                    target=t,
                    labels=lbs,
                    kind="mapping_dependency",
                ),
                "mcf",
            )

        for g in gls:
            gvs = set([nodes[v] for v in g.annotations.esl_info["body"]["variables"]])
            lbs = [v.annotations.esl_info["type_ref"] for v in gvs]
            a = n2c[g.annotations.esl_info["body"]["active"]]
            p = n2c[g.annotations.esl_info["body"]["passive"]]

            self._add(Edge(source=a, target=g, labels=lbs, kind="mapping_dependency"), "mcf")
            self._add(Edge(source=p, target=g, labels=lbs, kind="mapping_dependency"), "mcf")

            for d in a.descendants:
                if not ctd.get(d):
                    continue

                for t in ctd[d]:
                    outvars = set(
                        nodes[v] for v in t.annotations.esl_info["body"]["output_variables"]
                    )
                    shared_vars = outvars.intersection(gvs)

                    if shared_vars:
                        self._add(
                            Edge(
                                source=d,
                                target=g,
                                labels=[v.annotations.esl_info["type_ref"] for v in shared_vars],
                                kind="mapping_dependency",
                            ),
                            "mcf",
                        )

            for d in p.descendants:
                for t in ctd[d]:
                    invars = set(
                        nodes[v] for v in t.annotations.esl_info["body"]["input_variables"]
                    )
                    shared_vars = invars.intersection(gvs)

                    if shared_vars:
                        self._add(
                            Edge(
                                source=d,
                                target=g,
                                labels=[v.annotations.esl_info["type_ref"] for v in shared_vars],
                                kind="mapping_dependency",
                            ),
                            "mcf",
                        )

    def _make_mcv(self):
        """Create mapping relations between components and variables."""
        nodes = self.node_store.nodes
        cmps = self.node_store.components.values()
        mcf = self._make("mcf")

        # Get mapping relations from function specs.
        for m in mcf:
            f = m.target
            if m.target.annotations.esl_info["sub_kind"] == "goal":
                vrs = m.target.annotations.esl_info["body"]["variables"]
            if m.target.annotations.esl_info["sub_kind"] == "transformation":
                vrs = (
                    f.annotations.esl_info["body"]["input_variables"]
                    + f.annotations.esl_info["body"]["output_variables"]
                )

            for v in vrs:
                self._add(
                    Edge(
                        source=m.source,
                        target=nodes[v],
                        labels=[nodes[v].annotations.esl_info["type_ref"]],
                        annotations=dict(
                            esl_info=dict(reason=dict(function_specifications=[f.name]))
                        ),
                        kind="mapping_dependency",
                    ),
                    "mcv",
                )

        # Get mapping relations from properties
        for c in cmps:
            for v in c.annotations.esl_info["property_variables"]:
                self._add(
                    Edge(
                        source=c,
                        target=nodes[v],
                        labels=[nodes[v].annotations.esl_info["type_ref"]],
                        annotations=dict(esl_info=dict(reason={})),
                        kind="mapping_dependency",
                    ),
                    "mcv",
                )

    def _make_mcb(self):
        """Create mapping dependencies between components and behavior specs."""
        nodes = self.node_store.nodes
        tss = self.node_store.transforms.values()
        cmps = self.node_store.components.values()
        bhs = self.node_store.behaviors.values()

        cvd = defaultdict(set)
        for t in tss:
            c = nodes[t.annotations.esl_info["body"]["active"]]
            vs = t.annotations.esl_info["body"]["output_variables"]
            for v in vs:
                cvd[c, v].add(v)

        for c in cmps:
            for v in c.annotations.esl_info["property_variables"]:
                cvd[c, v].add(v)

        bvd = defaultdict(set)
        for b in bhs:
            for case in b.annotations.esl_info["cases"]:
                for tc in case["then_clauses"]:
                    for v in [r["subject"] for r in tc["body"]]:
                        bvd[b, v].add(v)

        shared_var_dict = defaultdict(list)
        for c, v in cvd:
            for b in bhs:
                if not bvd.get((b, v)):
                    continue
                shared_var_dict[c, b].append(v)

        for (c, b), vs in shared_var_dict.items():
            self._add(
                Edge(
                    source=c,
                    target=b,
                    kind="mapping_dependency",
                    labels=[nodes[v].annotations.esl_info["type_ref"] for v in vs],
                ),
                "mcb",
            )

    def _make_mfb(self):
        """Create mapping dependencies between function specs and behavior specs."""
        bhs = self.node_store.behaviors.values()
        mfv = self._make("mfv")
        mbv = self._make("mbv")

        mfvd = {}
        for e in mfv:
            mfvd[e.source, e.target] = e
        mbvd = {}
        for e in mbv:
            mbvd[e.source, e.target] = e

        shared_var_dict = defaultdict(list)

        for f, v in mfvd:
            for b in bhs:
                if not mbvd.get((b, v)):
                    continue
                shared_var_dict[f, b].append(v)

        for (f, b), vs in shared_var_dict.items():
            self._add(
                Edge(
                    source=f,
                    target=b,
                    kind="mapping_dependency",
                    labels=[v.annotations.esl_info["type_ref"] for v in vs],
                ),
                "mfb",
            )

    def _make_mbv(self):
        """Create mapping relations between behavior specifications and variables."""
        nodes = self.node_store.nodes
        bhs = self.node_store.behaviors.values()
        for b in bhs:
            vs = []
            for case in b.annotations.esl_info["cases"]:
                for wc in case["when_clauses"]:
                    vs.extend([nodes[r["subject"]] for r in wc["body"]])

                for tc in case["then_clauses"]:
                    vs.extend([nodes[r["subject"]] for r in tc["body"]])

            for v in vs:
                self._add(
                    Edge(
                        source=b,
                        target=v,
                        kind="mapping_dependency",
                        labels=[v.annotations.esl_info["type_ref"]],
                    ),
                    "mbv",
                )

    def _make_mcd(self):
        """Create mapping relations between components and design requirements."""
        nodes = self.node_store.nodes
        cmps = self.node_store.components.values()
        dss = self.node_store.designs.values()
        mcv = self._make("mcv")

        cvd: Dict[str, Set[str]] = defaultdict(set)
        for e in mcv:
            cvd[e.source].add(e.target)

        for c in cmps:
            for d in dss:
                vds = set()
                for r in d.annotations.esl_info["body"]:
                    vds.add(nodes[r["subject"]])

                    bound = r.get("bound")
                    if bound is None:
                        # Mim / max requirement
                        continue

                    if nodes.get(bound["value"]):
                        vds.add(nodes[bound["value"]])

                    shared_vars = cvd[c].intersection(vds)
                    if not shared_vars:
                        continue
                    shared_vars = sorted(shared_vars, key=lambda x: x.name)

                    self._add(
                        Edge(
                            source=c,
                            target=d,
                            kind="mapping_dependency",
                            labels=[v.annotations.esl_info["type_ref"] for v in shared_vars],
                            annotations=dict(
                                esl_info=dict(
                                    reason=dict(shared_variables=[v.name for v in shared_vars])
                                )
                            ),
                        ),
                        "mcd",
                    )

    def _make_mcr(self):
        """Create mapping relations between components and relations."""
        nodes = self.node_store.nodes
        rls = self.node_store.relations.values()
        mcv = self._make("mcv")

        cvd = defaultdict(set)
        for e in mcv:
            cvd[e.source].add(e.target.name)

        rvd = defaultdict(set)
        for r in rls:
            rvd[r] = set(
                r.annotations.esl_info["required_variables"]
                + r.annotations.esl_info["related_variables"]
                + r.annotations.esl_info["returned_variables"]
            )

        for c, cvs in cvd.items():
            for r, rvs in rvd.items():
                shared_vars = cvs.intersection(rvs)
                if not shared_vars:
                    continue
                shared_vars = sorted(shared_vars)
                self._add(
                    Edge(
                        source=c,
                        target=r,
                        kind="mapping_dependency",
                        labels=[nodes[v].annotations.esl_info["type_ref"] for v in shared_vars],
                        annotations=dict(esl_info=dict(reason=dict(shared_vars=shared_vars))),
                    ),
                    "mcr",
                )

    def _make_mfv(self):
        """Construct mapping dependencies between function specs and variables."""
        nodes = self.node_store.nodes
        tfs = self.node_store.transforms.values()
        gls = self.node_store.goals.values()

        for t in tfs:
            vs = [
                nodes[v]
                for v in t.annotations.esl_info["body"]["input_variables"]
                + t.annotations.esl_info["body"]["output_variables"]
            ]
            for v in vs:
                self._add(
                    Edge(
                        source=t,
                        target=v,
                        kind="mapping_dependency",
                        labels=[v.annotations.esl_info["type_ref"]],
                    ),
                    "mfv",
                )

        for g in gls:
            vs = [nodes[v] for v in g.annotations.esl_info["body"]["variables"]]
            for v in vs:
                self._add(
                    Edge(
                        source=g,
                        target=v,
                        kind="mapping_dependency",
                        labels=[v.annotations.esl_info["type_ref"]],
                    ),
                    "mfv",
                )

    def _make_mfd(self):
        """Construct mapping dependencies between function specs and design specs."""
        nodes = self.node_store.nodes
        gls = self.node_store.goals.values()
        tfs = self.node_store.transforms.values()
        dss = self.node_store.designs.values()

        fvd: Dict[str, Set[str]] = defaultdict(set)
        for g in gls:
            fvd[g] |= set(g.annotations.esl_info["body"]["variables"])
        for t in tfs:
            fvd[t] |= set(
                t.annotations.esl_info["body"]["input_variables"]
                + t.annotations.esl_info["body"]["output_variables"]
            )

        dvd: Dict[str, Set[str]] = defaultdict(set)
        for d in dss:
            for r in d.annotations.esl_info["body"]:
                dvd[d].add(r["subject"])

        for f in chain(gls, tfs):
            for d in dss:
                shared_vars = fvd[f].intersection(dvd[d])
                if not shared_vars:
                    continue
                shared_vars = sorted(shared_vars)
                self._add(
                    Edge(
                        source=f,
                        target=d,
                        kind="mapping_dependency",
                        labels=[nodes[v].annotations.esl_info["type_ref"] for v in shared_vars],
                        annotations=dict(esl_info=dict(reason=dict(shared_vars=shared_vars))),
                    ),
                    "mfd",
                )

    def _make_mfr(self):
        """Create mapping dependencies between functions specs and relation specs."""
        nodes = self.node_store.nodes
        gls = self.node_store.goals.values()
        tfs = self.node_store.transforms.values()
        rls = self.node_store.relations.values()

        fvd: Dict[str, Set[str]] = defaultdict(set)
        for g in gls:
            fvd[g] |= set(g.annotations.esl_info["body"]["variables"])

        for t in tfs:
            fvd[t] |= set(
                t.annotations.esl_info["body"]["input_variables"]
                + t.annotations.esl_info["body"]["output_variables"]
            )

        rvd: Dict[str, Set[str]] = defaultdict(set)
        for r in rls:
            rvd[r] = set(
                r.annotations.esl_info["required_variables"]
                + r.annotations.esl_info["related_variables"]
                + r.annotations.esl_info["returned_variables"]
            )

        for f, fvs in fvd.items():
            for r, rvs in rvd.items():
                shared_vars = fvs.intersection(rvs)
                if not shared_vars:
                    continue
                shared_vars = sorted(shared_vars)
                self._add(
                    Edge(
                        source=f,
                        target=r,
                        kind="mapping_dependency",
                        labels=[nodes[v].annotations.esl_info["type_ref"] for v in shared_vars],
                        annotations=dict(esl_info=dict(reason=dict(shared_vars=shared_vars))),
                    ),
                    "mfr",
                )

    def _make_mbd(self):
        """Create mapping dependencies between behavior requirements and design
        specifications.
        """
        nodes = self.node_store.nodes
        bhs = self.node_store.behaviors.values()
        dss = self.node_store.designs.values()

        bvd: Dict[Node, Set[str]] = defaultdict(set)
        for b in bhs:
            for case in b.annotations.esl_info["cases"]:
                for tc in case["then_clauses"]:
                    bvd[b] |= set([r["subject"] for r in tc["body"]])

        dvd: Dict[Node, Set[str]] = defaultdict(set)
        for d in dss:
            for r in d.annotations.esl_info["body"]:
                dvd[d].add(r["subject"])

        for b, bvs in bvd.items():
            for d, dvs in dvd.items():
                shared_vars = bvs.intersection(dvs)
                if shared_vars:
                    shared_vars = sorted(shared_vars)
                    self._add(
                        Edge(
                            source=b,
                            target=d,
                            kind="mapping_dependency",
                            labels=[nodes[v].annotations.esl_info["type_ref"] for v in shared_vars],
                            annotations=dict(esl_info=dict(reason=dict(shared_vars=shared_vars))),
                        ),
                        "mbd",
                    )

    def _make_mbr(self):
        """Create mapping dependencies between behavior requirements and relation
        specifications.
        """
        nodes = self.node_store.nodes
        bhs = self.node_store.behaviors.values()
        rls = self.node_store.relations.values()

        bvd: Dict[Node, Set[str]] = defaultdict(set)
        for b in bhs:
            for case in b.annotations.esl_info["cases"]:
                for tc in case["then_clauses"]:
                    bvd[b] |= set([r["subject"] for r in tc["body"]])
                for wc in case["when_clauses"]:
                    bvd[b] |= set([r["subject"] for r in wc["body"]])

        rvd: Dict[Node, Set[str]] = defaultdict(set)
        for r in rls:
            rvd[r] = set(
                r.annotations.esl_info["required_variables"]
                + r.annotations.esl_info["related_variables"]
                + r.annotations.esl_info["returned_variables"]
            )

        for b, bvs in bvd.items():
            for r, rvs in rvd.items():
                shared_vars = bvs.intersection(rvs)
                if shared_vars:
                    shared_vars = sorted(shared_vars)
                    self._add(
                        Edge(
                            source=b,
                            target=r,
                            kind="mapping_dependency",
                            labels=[nodes[v].annotations.esl_info["type_ref"] for v in shared_vars],
                            annotations=dict(esl_info=dict(reason=dict(shared_vars=shared_vars))),
                        ),
                        "mbr",
                    )

    def _make_mvd(self):
        """Create mapping dependencies between variables and design specifications."""
        nodes = self.node_store.nodes
        dss = self.node_store.designs.values()

        for d in dss:
            dvs = []
            for r in d.annotations.esl_info["body"]:
                dvs.append(r["subject"])

                bound = r.get("bound")
                if bound is None:
                    # Mim / max requirement
                    continue

                if nodes.get(bound["value"]):
                    dvs.append(bound["value"])

            for v in dvs:
                self._add(
                    Edge(
                        source=nodes[v],
                        target=d,
                        kind="mapping_dependency",
                        labels=[nodes[v].annotations.esl_info["type_ref"]],
                    ),
                    "mvd",
                )

    def _make_mvr(self):
        """Create mapping relations between variables and relation specifications."""
        nodes = self.node_store.nodes
        rls = self.node_store.relations.values()

        for r in rls:
            rvs = (
                r.annotations.esl_info["required_variables"]
                + r.annotations.esl_info["related_variables"]
                + r.annotations.esl_info["returned_variables"]
            )

            for v in rvs:
                self._add(
                    Edge(
                        source=nodes[v],
                        target=r,
                        kind="mapping_dependency",
                        labels=[nodes[v].annotations.esl_info["type_ref"]],
                    ),
                    "mvr",
                )

    def _make_mdr(self):
        """Create mapping dependencies between design specs and relation specs."""
        nodes = self.node_store.nodes
        dss = self.node_store.designs.values()
        rls = self.node_store.relations.values()

        dvd: Dict[Node, Set[str]] = defaultdict(set)
        for d in dss:
            for r in d.annotations.esl_info["body"]:
                dvd[d].add(r["subject"])

                bound = r.get("bound")
                if bound is None:
                    # Mim / max requirement
                    continue

                if nodes.get(bound["value"]):
                    dvd[d].add(bound["value"])

        rvd: Dict[Node, Set[str]] = defaultdict(set)
        for r in rls:
            rvd[r] = set(
                r.annotations.esl_info["required_variables"]
                + r.annotations.esl_info["related_variables"]
                + r.annotations.esl_info["returned_variables"]
            )

        for d, dvs in dvd.items():
            for r, rvs in rvd.items():
                shared_vars = dvs.intersection(rvs)
                if shared_vars:
                    shared_vars = sorted(shared_vars)
                    self._add(
                        Edge(
                            source=d,
                            target=r,
                            kind="mapping_dependency",
                            labels=[nodes[v].annotations.esl_info["type_ref"] for v in shared_vars],
                            annotations=dict(esl_info=dict(reason=dict(shared_vars=shared_vars))),
                        ),
                        "mdr",
                    )

    def _make_mnx(self):
        """Create mapping dependencies between needs and all other elements."""
        nodes = self.node_store.nodes
        nds = self.node_store.needs.values()
        for n in nds:
            s = nodes[n.annotations.esl_info["subject"]]
            self._add(
                Edge(source=s, target=n, kind="mapping_dependency", labels=["mapping"]),
                "mnx",
            )


def _generate_evbc(
    behavior: Node, case: Dict[str, Any], nodes: Dict[str, Node]
) -> Generator[Edge, None, None]:
    """Compute logical dependencies between variables for a behavior case specification.

    Arguments:
        behavior: Behavior specification that contains the case from which the logical
            dependencies must be derived.
        case: The case from which the logical dependencies must be derived.
        nodes: Dictionary of node name to Node object.

    Yields:
        Corresponding edges.
    """
    wv = []
    for wc in case["when_clauses"]:
        wv.extend([r["subject"] for r in wc["body"]])

    tv = []
    for tc in case["then_clauses"]:
        tv.extend([r["subject"] for r in tc["body"]])

    for vi in wv:
        for vj in tv:
            yield Edge(
                source=nodes[vi],
                target=nodes[vj],
                kind="logical_dependency",
                labels=[nodes[vi].annotations.esl_info["type_ref"]],
                annotations=dict(
                    esl_info=dict(reason=dict(behavior_specifications=[behavior.name]))
                ),
            )


def _get_component_behavior_dependency(
    nodes: Dict[str, Node],
    src: Node,
    trg: Node,
    ev_dict: Dict[Tuple[Node, Node], List[Edge]],
    vf_dict: Dict[str, List[Node]],
) -> Optional[Edge]:
    """Check if two component nodes have a behavior dependency.

    Arguments:
        nodes: Dictionary from node to node name.
        src: The source node for which the dependency must be checked.
        trg: THe target node for which the dependency must be checked.
        ev_dict: Dictionary of node pairs to list of edges.
        vf_dict: Dictionary of variable name to function spec nodes.

    Returns:
        An Edge if a behavior dependency exists. Otherwise None.
    """
    vis, vjs = [], []
    if src.annotations.esl_info["sub_kind"] == "goal":
        vis = [nodes[v] for v in src.annotations.esl_info["body"]["variables"]]
    elif src.annotations.esl_info["sub_kind"] == "transformation":
        vis = [nodes[v] for v in src.annotations.esl_info["body"]["output_variables"]]
    if trg.annotations.esl_info["sub_kind"] == "goal":
        vjs = [nodes[v] for v in trg.annotations.esl_info["body"]["variables"]]
    elif trg.annotations.esl_info["sub_kind"] == "transformation":
        vjs = [nodes[v] for v in trg.annotations.esl_info["body"]["output_variables"]]

    # Add properties
    ci = nodes[src.annotations.esl_info["body"]["active"]]
    cj = nodes[trg.annotations.esl_info["body"]["active"]]

    if ci == cj:
        return None

    if ci.annotations.esl_info.get("property_variables"):
        vis += [nodes[v] for v in ci.annotations.esl_info["property_variables"]]

    if cj.annotations.esl_info.get("property_variables"):
        vjs += [nodes[v] for v in cj.annotations.esl_info["property_variables"]]

    reasons = set()
    vrs = []
    edges = []
    for v in ev_dict.values():
        edges.extend(v)

    paths = _get_paths_between_all(srcs=vis, trgs=vjs, edges=edges)
    for path in paths:
        if len(path) == 2:
            vi, vj = path[0], path[1]
            edges = ev_dict.get((nodes[vi], nodes[vj]), [])
            for e in edges:
                reasons.update(e.annotations.esl_info["reason"]["behavior_specifications"])
            vrs.extend([nodes[path[0]], nodes[path[-1]]])
        else:
            # Check id none of the intermediate path variables relate to a function
            # spec. If so proceed.
            transformation_check = True
            for v in path[1:-1]:
                if v in vf_dict:
                    transformation_check = False
                    break

            if transformation_check:
                for vi, vj in zip(path[:-1], path[1:]):
                    edges = ev_dict.get((nodes[vi], nodes[vj]))
                    for e in edges:
                        reasons.update(e.annotations.esl_info["reason"]["behavior_specifications"])

            vrs.extend([nodes[path[0]], nodes[path[-1]]])

    if reasons:
        lbs = [v.annotations.esl_info["type_ref"] for v in vrs]
        return Edge(
            source=ci,
            target=cj,
            kind="logical_dependency",
            labels=lbs,
            annotations=dict(
                esl_info=dict(
                    reason=dict(
                        behavior_specifications=sorted(reasons),
                        function_specifications=[src.name, trg.name],
                    )
                )
            ),
        )
    else:
        return None


def _get_paths_between_all(srcs=List[Node], trgs=List[Node], edges=List[Edge]) -> List[List[str]]:
    """Compute paths between nodes. Based on depth first search.

    Arguments:
         srcs: List of starting nodes of paths.
         trgs: Set of ending nodes of path.
         edges: List of edges between nodes.

    Yields:
        List of lists of node names.
    """
    paths = []

    ed: Dict[str, Dict[str, Edge]] = defaultdict(dict)
    for e in edges:
        ed[e.source][e.target] = e

    for src in srcs:
        paths.extend(_get_paths(src=src, edge_dct=ed, trgs=trgs, visited=[]))

    return paths


def _get_paths(
    src: Node,
    edge_dct: Dict[Node, Dict[Node, Edge]],
    trgs: Set[Node],
    visited: List[Node] = [],
) -> List[List[str]]:
    """Collection all paths (list of node names) between the source node and the set of
    target nodes.

    Arguments:
        src: The source nodes where all paths should start.
        edge_dct: Dictionary of Node to Node to Edge. Contains the edges to be
            considered when searching for paths.
        trgs: Set of node where the paths should end.
        visited: List of nodes already visited. Required to prevent running in cycles.

    Returns:
        List of lists of node names.
    """
    visited.append(src.name)
    paths: List[List[str]] = []
    edges = edge_dct.get(src)
    if not edges:
        return paths

    for n in edges:
        if n.name in visited:
            # node has already been visited. Loop entered
            continue
        elif n in trgs:
            # A target has been reached
            visited.append(n.name)
            paths.append(visited)
        else:
            new_path = deepcopy(visited)
            paths.extend(_get_paths(src=n, edge_dct=edge_dct, trgs=trgs, visited=new_path))

    return paths


def _get_function_behavior_dependency(
    nodes: Dict[str, Node],
    src: Node,
    trg: Node,
    ev_dict: Dict[Tuple[Node, Node], Edge],
    vf_dict: Dict[str, List[Node]],
) -> Optional[Edge]:
    """Check if two function spec nodes have a behavior dependency.

    Arguments:
        nodes: Dictionary from node to node name.
        src: The source node for which the dependency must be checked.
        trg: THe target node for which the dependency must be checked.
        ev_dict: Dictionary of node pairs to edge.
        vf_dict: Dictionary of variable names to function specs.

    Returns:
        An Edge if a behavior dependency exists. Otherwise None.
    """
    vis, vjs = [], []
    if src.annotations.esl_info["sub_kind"] == "goal":
        vis = [nodes[v] for v in src.annotations.esl_info["body"]["variables"]]
    elif src.annotations.esl_info["sub_kind"] == "transformation":
        vis = [nodes[v] for v in src.annotations.esl_info["body"]["output_variables"]]
    if trg.annotations.esl_info["sub_kind"] == "goal":
        vjs = [nodes[v] for v in trg.annotations.esl_info["body"]["variables"]]
    elif trg.annotations.esl_info["sub_kind"] == "transformation":
        vjs = [nodes[v] for v in trg.annotations.esl_info["body"]["output_variables"]]

    reasons = set()
    vrs = []
    edges = []
    for v in ev_dict.values():
        edges.extend(v)

    paths = _get_paths_between_all(srcs=vis, trgs=vjs, edges=edges)
    for path in paths:
        if len(path) == 2:
            vi, vj = path[0], path[1]
            edges = ev_dict.get((nodes[vi], nodes[vj]), [])
            for e in edges:
                reasons.update(e.annotations.esl_info["reason"]["behavior_specifications"])
            vrs.extend([nodes[path[0]], nodes[path[-1]]])
        else:
            # Check id none of the intermediate path variables relate to a function
            # spec. If so proceed.
            transformation_check = True
            for v in path[1:-1]:
                if v in vf_dict:
                    transformation_check = False
                    break

            if transformation_check:
                for vi, vj in zip(path[:-1], path[1:]):
                    edges = ev_dict.get((nodes[vi], nodes[vj]))
                    for e in edges:
                        reasons.update(e.annotations.esl_info["reason"]["behavior_specifications"])

            vrs.extend([nodes[path[0]], nodes[path[-1]]])

    if reasons:
        lbs = [v.annotations.esl_info["type_ref"] for v in vrs]
        return Edge(
            source=src,
            target=trg,
            kind="logical_dependency",
            labels=lbs,
            annotations=dict(esl_info=dict(reason=dict(behavior_specifications=sorted(reasons)))),
        )
    else:
        return None
