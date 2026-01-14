# ============================================================
# Plotting.py
# Reines Plotting-Modul für STABRAUM
# Erwartet ein AnalysisResults-Objekt:  res = calc.run()
# ============================================================

from __future__ import annotations

import numpy as np
import matplotlib

matplotlib.use("QtAgg")  # oder TkAgg

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from matplotlib.widgets import CheckButtons, TextBox


# ------------------------------------------------------------
# Hilfsfunktion: gleiche Achsenskalierung im 3D
# ------------------------------------------------------------
def set_axes_equal_3d(ax, extra: float = 0.0):
    x_limits = np.array(ax.get_xlim3d(), dtype=float)
    y_limits = np.array(ax.get_ylim3d(), dtype=float)
    z_limits = np.array(ax.get_zlim3d(), dtype=float)

    ranges = np.array([np.ptp(lim) for lim in (x_limits, y_limits, z_limits)], dtype=float)
    max_range = float(max(ranges.max(), 1e-9))

    mids = np.array([lim.mean() for lim in (x_limits, y_limits, z_limits)], dtype=float)
    half = (1.0 + float(extra)) * max_range / 2.0

    ax.set_xlim3d(mids[0] - half, mids[0] + half)
    ax.set_ylim3d(mids[1] - half, mids[1] + half)
    ax.set_zlim3d(mids[2] - half, mids[2] + half)

    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass


# ============================================================
# StructurePlotter
# ============================================================
class StructurePlotter:
    """
    Reines Plotting.
    Erwartet ein AnalysisResults-Objekt (res = calc.run()).
    """

    # ----------------------------
    # init
    # ----------------------------
    def __init__(self, res):
        self.res = res
        self.Inp = res.Inp

        self.nodes = self.Inp.nodes
        self.na = self.Inp.members["na"]
        self.ne = self.Inp.members["ne"]

    # --------------------------------------------------------
    # Geometrie-Helfer
    # --------------------------------------------------------
    def _pt(self, n: int) -> np.ndarray:
        return np.array(
            [
                float(self.nodes["x[m]"][n - 1]),
                float(self.nodes["y[m]"][n - 1]),
                float(self.nodes["z[m]"][n - 1]),
            ],
            dtype=float,
        )

    def _tangent(self, a: int, e: int):
        Pi, Pj = self._pt(int(a)), self._pt(int(e))
        v = Pj - Pi
        L = float(np.linalg.norm(v))
        if L < 1e-15:
            raise ValueError("Elementlänge ~ 0")
        return Pi, Pj, v / L, L

    def _stable_normal(self, t: np.ndarray, prefer="y") -> np.ndarray:
        axes = {
            "x": np.array([1.0, 0.0, 0.0]),
            "y": np.array([0.0, 1.0, 0.0]),
            "z": np.array([0.0, 0.0, 1.0]),
        }
        u = axes.get(prefer, axes["y"])
        if abs(float(np.dot(t, u))) > 0.95:
            u = axes["z"] if prefer != "z" else axes["x"]

        w = np.cross(t, u)
        n = float(np.linalg.norm(w))
        if n < 1e-15:
            raise ValueError("Kein Orthogonalvektor")
        return w / n

    def _orth_unit_2d(self, xi, zi, xj, zj) -> np.ndarray:
        """
        Orthogonaler Einheitsvektor zur Stabachse in x-z-Ebene.
        """
        v = np.array([float(xj - xi), 0.0, float(zj - zi)], dtype=float)
        y_unit = np.array([0.0, 1.0, 0.0], dtype=float)
        perp = np.cross(v, y_unit)[[0, 2]]
        n = float(np.linalg.norm(perp))
        if n < 1e-15:
            raise ValueError("Elementlänge ~ 0")
        return perp / n

    def _field_map(self):
        return {
            "N": self.res.N_el_i_store,
            "VY": self.res.VY_el_i_store,
            "VZ": self.res.VZ_el_i_store,
            "MX": self.res.MX_el_i_store,
            "MY": self.res.MY_el_i_store,
            "MZ": self.res.MZ_el_i_store,
        }

    # --------------------------------------------------------
    # Dynamische Artists (2D)
    # --------------------------------------------------------
    def _mark_dyn(self, artist):
        try:
            artist._dyn = True
        except Exception:
            pass
        return artist

    def _clear_dyn(self, ax):
        for ln in list(getattr(ax, "lines", [])):
            if getattr(ln, "_dyn", False):
                ln.remove()
        for p in list(getattr(ax, "patches", [])):
            if getattr(p, "_dyn", False):
                p.remove()
        for t in list(getattr(ax, "texts", [])):
            if getattr(t, "_dyn", False):
                t.remove()

    # --------------------------------------------------------
    # Basic 2D arrows
    # --------------------------------------------------------
    def _draw_force_arrow(self, ax, x, z, dx, dz, color="k", lw=1.8, head=10):
        arr = FancyArrowPatch(
            (x, z),
            (x + dx, z + dz),
            arrowstyle="-|>",
            mutation_scale=head,
            linewidth=lw,
            color=color,
        )
        ax.add_patch(arr)
        self._mark_dyn(arr)
        return arr

    def _draw_moment_double_arrow(self, ax, x, z, M, radius=0.08, color="purple", lw=1.8):
        # Kleiner Kreis + Pfeil andeuten
        th = np.linspace(0.0, 2 * np.pi, 120)
        xs = x + radius * np.cos(th)
        zs = z + radius * np.sin(th)
        ln = ax.plot(xs, zs, color=color, lw=lw)[0]
        self._mark_dyn(ln)

        # Richtungspfeil am Kreis
        # wähle Punkt bei 45°
        t0 = np.pi / 4
        px = x + radius * np.cos(t0)
        pz = z + radius * np.sin(t0)
        # Tangente
        tx = -np.sin(t0)
        tz = np.cos(t0)
        sgn = 1.0 if float(M) >= 0.0 else -1.0
        arr = FancyArrowPatch(
            (px, pz),
            (px + sgn * 0.6 * radius * tx, pz + sgn * 0.6 * radius * tz),
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=lw,
            color=color,
        )
        ax.add_patch(arr)
        self._mark_dyn(arr)
        return ln, arr

    # --------------------------------------------------------
    # Reactions / supports helpers (STABRAUM-Style)
    # --------------------------------------------------------
    def _reaction_vector(self) -> np.ndarray:
        """
        Reaktionsvektor r = K*u - F (o.ä.)
        Du hattest das schon in deiner OutputData. Hier robust:
        - bevorzugt res.Reactions, falls vorhanden
        - sonst versucht: r = GesMat @ u_ges - FGes
        """
        if hasattr(self.res, "Reactions") and self.res.Reactions is not None:
            r = np.asarray(self.res.Reactions, dtype=float).reshape(-1)
            return r

        if hasattr(self.res, "GesMat") and hasattr(self.res, "u_ges") and hasattr(self.res, "FGes"):
            K = np.asarray(self.res.GesMat, dtype=float)
            u = np.asarray(self.res.u_ges, dtype=float).reshape(-1)
            F = np.asarray(self.res.FGes, dtype=float).reshape(-1)
            return (K @ u - F).reshape(-1)

        # fallback
        return np.zeros(int(len(self.nodes["x[m]"]) * 7), dtype=float)

    def _support_nodes(self):
        """
        RestraintData erwartet: Spalten 'Node' usw.
        """
        df = getattr(self.Inp, "RestraintData", None)
        if df is None:
            return []
        cols = [str(c).strip() for c in df.columns]
        if "Node" not in cols:
            return []
        # unique nodes, >0
        out = []
        for n in df["Node"].tolist():
            try:
                nn = int(n)
                if nn not in out:
                    out.append(nn)
            except Exception:
                pass
        return out

    def _length_ref_xz(self, frac=0.03) -> float:
        xs = np.asarray(self.nodes["x[m]"], dtype=float)
        zs = np.asarray(self.nodes["z[m]"], dtype=float)
        span = max(float(xs.max() - xs.min()), float(zs.max() - zs.min()), 1e-9)
        return float(frac) * span

    # ========================================================
    # Springs: Parsing & 3D drawing (TRANSLATION + ROTATION)
    # ========================================================
    def _get_springs_df(self):
        df = getattr(self.Inp, "SpringsData", None)
        if df is None:
            df = getattr(self.Inp, "Springs", None)
        return df

    @staticmethod
    def _spring_dof_kind(dof: int):
        """
        Mapping passend zu deinem 7-DoF Layout (wie in deinen anderen Funktionen):
          Transl: 0=FX/ux, 1=FY/uy, 3=FZ/uz
          Rot   : 5=MX, 4=MY, 2=MZ
        """
        dof = int(dof)
        trans = {0: ("TX", np.array([1.0, 0.0, 0.0])),
                 1: ("TY", np.array([0.0, 1.0, 0.0])),
                 3: ("TZ", np.array([0.0, 0.0, 1.0]))}
        rot   = {5: ("RX", np.array([1.0, 0.0, 0.0])),
                 4: ("RY", np.array([0.0, 1.0, 0.0])),
                 2: ("RZ", np.array([0.0, 0.0, 1.0]))}
        if dof in trans:
            return "trans", trans[dof][0], trans[dof][1]
        if dof in rot:
            return "rot", rot[dof][0], rot[dof][1]
        return None, f"DOF{dof}", np.array([1.0, 0.0, 0.0])

    @staticmethod
    def _pick_perp_basis(axis_hat: np.ndarray):
        axis_hat = np.asarray(axis_hat, dtype=float)
        axis_hat = axis_hat / (np.linalg.norm(axis_hat) + 1e-16)
        ex = np.array([1.0, 0.0, 0.0], dtype=float)
        ey = np.array([0.0, 1.0, 0.0], dtype=float)
        ez = np.array([0.0, 0.0, 1.0], dtype=float)

        h = ex if abs(float(np.dot(axis_hat, ex))) < 0.9 else ey
        u = np.cross(axis_hat, h)
        nu = float(np.linalg.norm(u))
        if nu < 1e-14:
            h = ez
            u = np.cross(axis_hat, h)
            nu = float(np.linalg.norm(u))

        u_hat = u / (nu + 1e-16)
        v_hat = np.cross(axis_hat, u_hat)
        v_hat = v_hat / (np.linalg.norm(v_hat) + 1e-16)
        return u_hat, v_hat

    def _draw_trans_spring_3d(self, ax, P0, axis_hat, size, nzig=7, amp_frac=0.18, color="purple", lw=1.6):
        """
        Zickzack-Feder entlang axis_hat, Start bei P0.
        """
        P0 = np.asarray(P0, dtype=float).reshape(3,)
        axis_hat = np.asarray(axis_hat, dtype=float).reshape(3,)
        axis_hat = axis_hat / (np.linalg.norm(axis_hat) + 1e-16)

        u_hat, _ = self._pick_perp_basis(axis_hat)
        amp = float(amp_frac) * float(size)

        t = np.linspace(0.0, 1.0, 2 * int(nzig) + 1)
        pts = []
        for i, ti in enumerate(t):
            P = P0 + (ti * float(size)) * axis_hat
            if 0 < i < len(t) - 1:
                sgn = 1.0 if (i % 2 == 0) else -1.0
                P = P + sgn * amp * u_hat
            pts.append(P)

        segs = [[pts[i], pts[i + 1]] for i in range(len(pts) - 1)]
        coll = Line3DCollection(segs, colors=color, linewidths=lw)
        ax.add_collection3d(coll)
        return coll

    def _draw_rot_spring_3d(self, ax, P0, axis_hat, radius, turns=1.25, n=120, color="purple", lw=1.6):
        """
        Rotationsfeder als Spirale in Ebene senkrecht zu axis_hat.
        """
        P0 = np.asarray(P0, dtype=float).reshape(3,)
        axis_hat = np.asarray(axis_hat, dtype=float).reshape(3,)
        axis_hat = axis_hat / (np.linalg.norm(axis_hat) + 1e-16)

        u_hat, v_hat = self._pick_perp_basis(axis_hat)

        th = np.linspace(0.0, 2 * np.pi * float(turns), int(n))
        # leichte Radialänderung für "Federlook"
        r = float(radius) * (0.75 + 0.25 * (th / (th.max() + 1e-16)))

        pts = [P0 + r[i] * np.cos(th[i]) * u_hat + r[i] * np.sin(th[i]) * v_hat for i in range(len(th))]
        segs = [[pts[i], pts[i + 1]] for i in range(len(pts) - 1)]
        coll = Line3DCollection(segs, colors=color, linewidths=lw)
        ax.add_collection3d(coll)
        return coll

    def _draw_springs_3d(
        self,
        ax,
        # Größen (relativ zur Modellspannweite)
        size_frac=0.06,
        rot_radius_frac=0.03,
        # Sichtbarkeit
        show_trans=True,
        show_rot=True,
        # Datenquellen
        include_springsdata=True,
        include_restraints=True,
        # Filter
        k_tol=1e-12,
        # Darstellung
        color="purple",
        label=False,
        label_fs=8,
    ):
        """
        Zeichnet Federn in 3D aus zwei Quellen:

        (A) SpringsData (CSV):
            Spalten: node_a, node_e, dof, cp/cm[MN,m]  (k-Spalte optional/robust)
            - node_a==node_e -> Feder am Knoten
            - sonst -> Feder am Mittelpunkt zwischen node_a und node_e

        (B) RestraintData:
            Spalten: Node, kx/ky/kz/krx/kry/krz (robust, case-insensitive)
            - Feder immer am Knoten

        DOF-Mapping (dein 7-DoF Layout / STABRAUM):
        transl: ux=0, uy=1, uz=3
        rot   : rx=5, ry=4, rz=2

        Benötigt folgende Helper-Methoden in deiner Klasse:
        - self._pt(n) -> np.array([x,y,z])
        - self._spring_dof_kind(dof) -> (kind, label, axis_vec)
        - self._draw_trans_spring_3d(ax, P0, axis_vec, size, color=...)
        - self._draw_rot_spring_3d(ax, P0, axis_vec, radius, color=...)
        - self._get_springs_df() -> DataFrame|None   (deine SpringsData)
        - self._iter_restraint_springs(k_tol=...) -> yields (node, dof_int, k)
        """

        # ---------------------------
        # Modell-Spannweite für Maßstab
        # ---------------------------
        xs = np.asarray(self.nodes["x[m]"], dtype=float)
        ys = np.asarray(self.nodes["y[m]"], dtype=float)
        zs = np.asarray(self.nodes["z[m]"], dtype=float)
        span = max(
            float(xs.max() - xs.min()),
            float(ys.max() - ys.min()),
            float(zs.max() - zs.min()),
            1e-9,
        )

        size = float(size_frac) * span
        rr = float(rot_radius_frac) * span

        # ---------------------------
        # Jobs sammeln: (P0, dof, labelprefix)
        # ---------------------------
        jobs = []  # list[tuple[np.ndarray, int, str|None]]

        # ---------- (A) SpringsData ----------
        if include_springsdata:
            df = None
            try:
                df = self._get_springs_df()
            except Exception:
                df = None

            if df is not None:
                df = df.copy()
                df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]

                need = ["node_a", "node_e", "dof"]
                if all(c in df.columns for c in need):
                    # k-Spalte robust finden (optional)
                    k_col = None
                    for cand in [
                        "cp/cm[MN,m]",
                        "cp/cm[MN,m ]",
                        "cp/cm",
                        "k",
                        "K",
                        "stiffness",
                        "Value",
                        "value",
                    ]:
                        if cand in df.columns:
                            k_col = cand
                            break

                    # Leere Zeilen raus (CSV-Leerzeilen)
                    if k_col is not None:
                        df = df.dropna(subset=["node_a", "node_e", "dof", k_col])
                    else:
                        df = df.dropna(subset=["node_a", "node_e", "dof"])

                    for _, row in df.iterrows():
                        try:
                            na = int(row["node_a"])
                            ne = int(row["node_e"])
                            dof = int(float(row["dof"]))
                        except Exception:
                            continue

                        # optionaler k-filter
                        if k_col is not None:
                            try:
                                kval = float(row[k_col])
                            except Exception:
                                kval = 0.0
                            if abs(kval) <= float(k_tol):
                                continue

                        try:
                            Pa = self._pt(na)
                            Pe = self._pt(ne)
                        except Exception:
                            continue

                        P0 = Pa if na == ne else 0.5 * (Pa + Pe)
                        jobs.append((np.asarray(P0, dtype=float), dof, None))

        # ---------- (B) RestraintData ----------
        if include_restraints:
            try:
                for n, dof, k in self._iter_restraint_springs(k_tol=k_tol):
                    try:
                        P0 = self._pt(int(n))
                    except Exception:
                        continue
                    jobs.append((np.asarray(P0, dtype=float), int(dof), f"N{int(n)}"))
            except Exception:
                pass

        if len(jobs) == 0:
            return []

        # ---------------------------
        # Zeichnen
        # ---------------------------
        artists = []

        for P0, dof, lab_prefix in jobs:
            try:
                kind, lab, axis = self._spring_dof_kind(int(dof))
            except Exception:
                continue

            if kind == "trans" and not show_trans:
                continue
            if kind == "rot" and not show_rot:
                continue

            axis = np.asarray(axis, dtype=float)
            na = float(np.linalg.norm(axis))
            if na < 1e-15:
                continue
            axis = axis / na

            # kleiner Offset damit Feder nicht "im Knotenpunkt" klebt
            Pbase = P0 + 0.15 * size * axis

            if kind == "trans":
                try:
                    art = self._draw_trans_spring_3d(ax, Pbase, axis, size=size, color=color)
                    artists.append(art)
                except Exception:
                    pass

            elif kind == "rot":
                try:
                    art = self._draw_rot_spring_3d(ax, Pbase, axis, radius=rr, color=color)
                    artists.append(art)
                except Exception:
                    pass

            if label:
                txt = lab if lab_prefix is None else f"{lab_prefix}:{lab}"
                try:
                    ax.text(
                        float(Pbase[0]),
                        float(Pbase[1]),
                        float(Pbase[2]),
                        txt,
                        fontsize=int(label_fs),
                        color=color,
                    )
                except Exception:
                    pass

        return artists


    # ========================================================
    # 2D Struktur (x-z) + Nummerierung
    # ========================================================
    def plot_structure_2d(self, node_labels: bool = False, elem_labels: bool = False):
        fig, ax = plt.subplots(figsize=(10, 6))

        # Stäbe zeichnen
        for idx, (a, e) in enumerate(zip(self.na, self.ne), start=1):
            Pi, Pj = self._pt(int(a)), self._pt(int(e))
            ax.plot([Pi[0], Pj[0]], [Pi[2], Pj[2]], color="black", lw=1.0)

            # Elementnummer am Mittelpunkt
            if elem_labels:
                xm = 0.5 * (Pi[0] + Pj[0])
                zm = 0.5 * (Pi[2] + Pj[2])
                ax.text(
                    xm,
                    zm,
                    f"E{idx}",
                    fontsize=9,
                    ha="center",
                    va="center",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="gray", lw=0.5),
                )

        # Knotennummern
        if node_labels:
            n_nodes = len(self.nodes["x[m]"])
            for n in range(1, n_nodes + 1):
                P = self._pt(n)
                ax.plot(P[0], P[2], marker="o", markersize=3, color="black")
                ax.text(
                    P[0],
                    P[2],
                    f"N{n}",
                    fontsize=9,
                    ha="left",
                    va="bottom",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="gray", lw=0.5),
                )

        ax.set_xlabel("X [m]")
        ax.set_ylabel("Z [m]")
        ax.set_title("Unverformte Struktur (x-z)")
        ax.grid(True)
        ax.set_aspect("equal", adjustable="datalim")
        ax.relim()
        ax.autoscale_view()
        return fig, ax

    # ========================================================
    # 2D Endwerte (statisch)
    # ========================================================
    def plot_endforces_2d(self, kind="MY", scale=5.0, invert_y=False, node_labels=False, elem_labels=False):
        fig, ax = self.plot_structure_2d(node_labels=node_labels, elem_labels=elem_labels)
        Q = self._field_map()[kind.upper()]  # (nElem,2,1)

        for i, (a, e) in enumerate(zip(self.na, self.ne)):
            Pi, Pj = self._pt(int(a)), self._pt(int(e))
            ix, iz = Pi[0], Pi[2]
            jx, jz = Pj[0], Pj[2]

            try:
                u = self._orth_unit_2d(ix, iz, jx, jz)
            except ValueError:
                continue

            qa = float(Q[i, 0, 0])
            qb = float(Q[i, 1, 0])

            def endpt(x, z, val):
                if abs(val) < 1e-15:
                    return x, z
                col = "blue" if val >= 0 else "red"
                link = 0.05 * float(scale)
                cx = x + link * u[0] * val * float(scale)
                cz = z + link * u[1] * val * float(scale)
                ax.plot([x, cx], [z, cz], color=col, lw=1)
                ax.text(cx, cz, f"{kind}={val:.3f}", color=col, fontsize=8)
                return cx, cz

            ca = endpt(ix, iz, qa)
            cb = endpt(jx, jz, qb)
            ax.plot([ca[0], cb[0]], [ca[1], cb[1]], color="black", lw=1)

        ax.legend(handles=[mpatches.Patch(color="blue", label=f"{kind} ≥ 0"),
                           mpatches.Patch(color="red", label=f"{kind} < 0")])

        if invert_y:
            ax.invert_yaxis()

        ax.relim()
        ax.autoscale_view()
        return fig, ax

    # ========================================================
    # 2D Endwerte (DYNAMISCH, Slider für scale)
    # ========================================================
    def plot_endforces_2d_interactive(self, kind="MY", scale_init=5.0, invert_y=False, node_labels=False, elem_labels=False):
        fig, ax = self.plot_structure_2d(node_labels=node_labels, elem_labels=elem_labels)
        Q = self._field_map()[kind.upper()]  # (nElem,2,1)

        smin = 0.0
        smax = max(float(scale_init) * 50.0, 10.0)

        ax.legend(handles=[mpatches.Patch(color="blue", label=f"{kind} ≥ 0"),
                           mpatches.Patch(color="red", label=f"{kind} < 0")])

        def _clear_dyn_local():
            self._clear_dyn(ax)

        def draw(scale):
            _clear_dyn_local()
            scale = float(scale)

            for i, (a, e) in enumerate(zip(self.na, self.ne)):
                Pi, Pj = self._pt(int(a)), self._pt(int(e))
                ix, iz = Pi[0], Pi[2]
                jx, jz = Pj[0], Pj[2]

                try:
                    u = self._orth_unit_2d(ix, iz, jx, jz)
                except ValueError:
                    continue

                qa = float(Q[i, 0, 0])
                qb = float(Q[i, 1, 0])

                def endpt(x, z, val):
                    if abs(val) < 1e-15:
                        return x, z
                    col = "blue" if val >= 0 else "red"
                    link = 0.05 * scale
                    cx = x + link * u[0] * val * scale
                    cz = z + link * u[1] * val * scale
                    ln = ax.plot([x, cx], [z, cz], color=col, lw=1)[0]
                    self._mark_dyn(ln)
                    txt = ax.text(cx, cz, f"{kind}={val:.3f}", color=col, fontsize=8)
                    self._mark_dyn(txt)
                    return cx, cz

                ca = endpt(ix, iz, qa)
                cb = endpt(jx, jz, qb)
                ln2 = ax.plot([ca[0], cb[0]], [ca[1], cb[1]], color="black", lw=1)[0]
                self._mark_dyn(ln2)

            ax.relim()
            ax.autoscale_view()
            ax.set_aspect("equal", adjustable="datalim")
            if invert_y:
                ax.invert_yaxis()
            fig.canvas.draw_idle()

        fig.subplots_adjust(bottom=0.20)
        ax_scale = fig.add_axes([0.15, 0.08, 0.70, 0.03])
        s_scale = Slider(ax_scale, "Scale", smin, smax, valinit=float(scale_init))
        s_scale.on_changed(lambda _: draw(s_scale.val))
        draw(scale_init)
        return fig, ax, s_scale

    # ========================================================
    # 3D verformte Struktur (interaktiv) + Nummerierung + FEDERN (NEU)
    # ========================================================
    def plot_structure_deformed_3d_interactive(
        self,
        scale_init=1.0,
        show_undeformed=True,
        node_labels=False,
        elem_labels=False,
        # NEW: springs
        show_springs=True,
        show_rot_springs=True,
        springs_size_frac=0.06,
        springs_rot_radius_frac=0.03,
        springs_label=False,
        springs_k_tol=1e-12,
    ):
        def ux(n):
            return float(self.res.u_ges[7 * (n - 1) + 0])

        def uy(n):
            return float(self.res.u_ges[7 * (n - 1) + 1])

        def uz(n):
            return float(self.res.u_ges[7 * (n - 1) + 3])

        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(projection="3d")

        # unverformte Stäbe
        if show_undeformed:
            segs = []
            for a, e in zip(self.na, self.ne):
                segs.append([self._pt(int(a)), self._pt(int(e))])
            ax.add_collection3d(Line3DCollection(segs, colors="lightgray", linewidths=1, zorder=0))

        # Springs (NEU): symbolisch, unabhängig vom Deformationsscale
        if show_springs or show_rot_springs:
            self._draw_springs_3d(
                ax,
                size_frac=float(springs_size_frac),
                rot_radius_frac=float(springs_rot_radius_frac),
                show_trans=bool(show_springs),
                show_rot=bool(show_rot_springs),
                color="purple",
                label=bool(springs_label),
                k_tol=float(springs_k_tol),
            )

        # deformierte Linien
        deformed_lines = []
        for a, e in zip(self.na, self.ne):
            a, e = int(a), int(e)
            Pi, Pj = self._pt(a), self._pt(e)

            xd = [Pi[0] + float(scale_init) * ux(a), Pj[0] + float(scale_init) * ux(e)]
            yd = [Pi[1] + float(scale_init) * uy(a), Pj[1] + float(scale_init) * uy(e)]
            zd = [Pi[2] + float(scale_init) * uz(a), Pj[2] + float(scale_init) * uz(e)]
            (ld,) = ax.plot(xd, yd, zd, lw=2, zorder=3)
            deformed_lines.append((a, e, ld))

        # Texte
        node_texts = []
        elem_texts = []

        if node_labels:
            n_nodes = len(self.nodes["x[m]"])
            for n in range(1, n_nodes + 1):
                P = self._pt(n)
                txt = ax.text(
                    P[0] + float(scale_init) * ux(n),
                    P[1] + float(scale_init) * uy(n),
                    P[2] + float(scale_init) * uz(n),
                    f"N{n}",
                    fontsize=8,
                    zorder=4,
                )
                node_texts.append((n, txt))

        if elem_labels:
            for idx, (a, e) in enumerate(zip(self.na, self.ne), start=1):
                a, e = int(a), int(e)
                Pi, Pj = self._pt(a), self._pt(e)
                xm = 0.5 * (Pi[0] + Pj[0]) + float(scale_init) * 0.5 * (ux(a) + ux(e))
                ym = 0.5 * (Pi[1] + Pj[1]) + float(scale_init) * 0.5 * (uy(a) + uy(e))
                zm = 0.5 * (Pi[2] + Pj[2]) + float(scale_init) * 0.5 * (uz(a) + uz(e))
                txt = ax.text(xm, ym, zm, f"E{idx}", fontsize=8, zorder=4)
                elem_texts.append((idx, a, e, txt))

        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.set_zlabel("Z [m]")
        ax.set_title("Verformte Struktur 3D (interaktiv) + Federn")

        set_axes_equal_3d(ax, extra=0.05)

        fig.subplots_adjust(bottom=0.18)
        ax_scale = fig.add_axes([0.15, 0.08, 0.7, 0.03])
        s_scale = Slider(ax_scale, "Scale", 0.0, float(scale_init) * 10000.0, valinit=float(scale_init))

        def update(_):
            s = float(s_scale.val)

            for a, e, line in deformed_lines:
                Pi, Pj = self._pt(a), self._pt(e)
                line.set_data_3d(
                    [Pi[0] + s * ux(a), Pj[0] + s * ux(e)],
                    [Pi[1] + s * uy(a), Pj[1] + s * uy(e)],
                    [Pi[2] + s * uz(a), Pj[2] + s * uz(e)],
                )

            for n, txt in node_texts:
                P = self._pt(n)
                txt.set_position((P[0] + s * ux(n), P[1] + s * uy(n)))
                txt.set_3d_properties(P[2] + s * uz(n), zdir="z")

            for idx, a, e, txt in elem_texts:
                Pi, Pj = self._pt(a), self._pt(e)
                xm = 0.5 * (Pi[0] + Pj[0]) + s * 0.5 * (ux(a) + ux(e))
                ym = 0.5 * (Pi[1] + Pj[1]) + s * 0.5 * (uy(a) + uy(e))
                zm = 0.5 * (Pi[2] + Pj[2]) + s * 0.5 * (uz(a) + uz(e))
                txt.set_position((xm, ym))
                txt.set_3d_properties(zm, zdir="z")

            set_axes_equal_3d(ax, extra=0.05)
            fig.canvas.draw_idle()

        s_scale.on_changed(update)
        update(None)
        return fig, ax, s_scale

    # ========================================================
    # 3D Schnittgrößen-Diagramm entlang der Stäbe (DYNAMISCH) + FEDERN (NEU)
    # ========================================================
    def plot_diagram_3d_interactive(
        self,
        kind="MY",
        scale_init=1.0,
        width_frac=0.03,
        prefer_axis="y",
        show_structure=True,
        show_end_labels=True,
        label_offset_frac=0.02,
        font_size=8,
        robust_ref=True,
        keep_view=True,
        margin_frac=0.05,
        # NEW: springs
        show_springs=True,
        show_rot_springs=True,
        springs_size_frac=0.06,
        springs_rot_radius_frac=0.03,
        springs_label=False,
        springs_k_tol=1e-12,
    ):
        """
        Festes 3D-Diagramm als Polygon-Band pro Element.
        - Positiv: Blau, Negativ: Rot (Split bei Vorzeichenwechsel)
        - Nur 1 Diagramm-Linie pro Element (Mittellinie)
        - Einheit bleibt exakt wie in deinem Solver (MN bzw. MNm).
        - Scale per TextBox (+ optional Slider)
        - Node/Elem IDs per CheckButtons
        - NEU: Federn (Translation + Rotation) symbolisch
        """
        kind = str(kind).upper()
        Q = self._field_map()[kind]  # (nElem,2,1)

        vals = np.abs(Q[:, :, 0]).ravel()
        if vals.size == 0:
            qref = 1.0
        else:
            qref = float(np.percentile(vals, 95)) if robust_ref else float(vals.max())
            qref = max(qref, 1e-12)

        xs = np.asarray(self.nodes["x[m]"], dtype=float)
        ys = np.asarray(self.nodes["y[m]"], dtype=float)
        zs = np.asarray(self.nodes["z[m]"], dtype=float)
        span = max(float(xs.max() - xs.min()), float(ys.max() - ys.min()), float(zs.max() - zs.min()), 1e-9)

        mx = float(margin_frac) * span
        xlim = (float(xs.min() - mx), float(xs.max() + mx))
        ylim = (float(ys.min() - mx), float(ys.max() + mx))
        zlim = (float(zs.min() - mx), float(zs.max() + mx))

        width = float(width_frac) * span
        label_off = float(label_offset_frac) * span

        fig = plt.figure(figsize=(11, 7))
        ax = fig.add_subplot(projection="3d")

        if show_structure:
            segs = []
            for a, e in zip(self.na, self.ne):
                segs.append([self._pt(int(a)), self._pt(int(e))])
            ax.add_collection3d(Line3DCollection(segs, colors="lightgray", linewidths=1, zorder=0))

        # NEW: springs (symbolic)
        if show_springs or show_rot_springs:
            self._draw_springs_3d(
                ax,
                size_frac=float(springs_size_frac),
                rot_radius_frac=float(springs_rot_radius_frac),
                show_trans=bool(show_springs),
                show_rot=bool(show_rot_springs),
                color="purple",
                label=bool(springs_label),
                k_tol=float(springs_k_tol),
            )

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_zlim(zlim)
        try:
            ax.set_box_aspect((1, 1, 1))
        except Exception:
            pass

        node_id_texts = []
        elem_id_texts = []

        n_nodes = len(self.nodes["x[m]"])
        for n in range(1, n_nodes + 1):
            P = self._pt(n)
            node_id_texts.append(ax.text(P[0], P[1], P[2], f"N{n}", fontsize=8, visible=False))

        for idx, (a, e) in enumerate(zip(self.na, self.ne), start=1):
            Pi, Pj = self._pt(int(a)), self._pt(int(e))
            Pm = 0.5 * (Pi + Pj)
            elem_id_texts.append(ax.text(Pm[0], Pm[1], Pm[2], f"E{idx}", fontsize=8, visible=False))

        polys = []
        lines = []
        end_texts = []

        def clear_dynamic():
            nonlocal polys, lines, end_texts
            for p in polys:
                try:
                    p.remove()
                except Exception:
                    pass
            for ln in lines:
                try:
                    ln.remove()
                except Exception:
                    pass
            for t in end_texts:
                try:
                    t.remove()
                except Exception:
                    pass
            polys, lines, end_texts = [], [], []

        def col_for(val):
            return "blue" if float(val) >= 0.0 else "red"

        def split_parts(Pi, Pj, Mi, Mj):
            Mi = float(Mi)
            Mj = float(Mj)
            if Mi == 0.0 or Mj == 0.0 or (Mi > 0 and Mj > 0) or (Mi < 0 and Mj < 0):
                return [(Pi, Pj, Mi, Mj, col_for(0.5 * (Mi + Mj)))]
            s0 = -Mi / (Mj - Mi)
            s0 = min(max(float(s0), 0.0), 1.0)
            P0 = Pi + s0 * (Pj - Pi)
            return [
                (Pi, P0, Mi, 0.0, col_for(Mi)),
                (P0, Pj, 0.0, Mj, col_for(Mj)),
            ]

        state = {"scale": float(scale_init)}

        def draw():
            clear_dynamic()

            scale = float(state["scale"])
            alpha = scale / qref

            prev_w = None
            for i, (a, e) in enumerate(zip(self.na, self.ne)):
                a, e = int(a), int(e)
                Pi, Pj, t_hat, L = self._tangent(a, e)

                w = self._stable_normal(t_hat, prefer=prefer_axis)
                if prev_w is not None and float(np.dot(w, prev_w)) < 0.0:
                    w = -w
                prev_w = w

                v = np.cross(t_hat, w)
                nv = float(np.linalg.norm(v))
                if nv < 1e-15:
                    continue
                v = v / nv

                Mi = float(Q[i, 0, 0])
                Mj = float(Q[i, 1, 0])

                for PA, PB, Ma, Mb, c in split_parts(Pi, Pj, Mi, Mj):
                    p1 = PA + 0.0 * width * v
                    p2 = PA + 0.0 * width * v + (alpha * Ma) * w
                    p3 = PB + 0.0 * width * v + (alpha * Mb) * w
                    p4 = PB + 0.0 * width * v

                    poly = Poly3DCollection(
                        [[p1, p2, p3, p4]],
                        alpha=0.25,
                        facecolor=c,
                        edgecolor=c,
                        linewidths=1.0,
                    )
                    ax.add_collection3d(poly)
                    polys.append(poly)

                    q2 = PA + (alpha * Ma) * w
                    q3 = PB + (alpha * Mb) * w
                    ln = ax.plot([q2[0], q3[0]], [q2[1], q3[1]], [q2[2], q3[2]], color=c, lw=2.0)[0]
                    lines.append(ln)

                if show_end_labels:
                    off = label_off * w
                    end_texts.append(
                        ax.text(Pi[0] + off[0], Pi[1] + off[1], Pi[2] + off[2], f"N{a}\n{Mi:+.3f}", fontsize=int(font_size))
                    )
                    end_texts.append(
                        ax.text(Pj[0] + off[0], Pj[1] + off[1], Pj[2] + off[2], f"N{e}\n{Mj:+.3f}", fontsize=int(font_size))
                    )

            ax.set_xlabel("X [m]")
            ax.set_ylabel("Y [m]")
            ax.set_zlabel("Z [m]")
            ax.set_title(f"{kind} Diagramm 3D (Polygon) | base | ref={qref:.3g}")

            if keep_view:
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.set_zlim(zlim)

            fig.canvas.draw_idle()

        fig.subplots_adjust(left=0.05, right=0.83, bottom=0.12)

        ax_chk = fig.add_axes([0.85, 0.78, 0.13, 0.12])
        for sp in ax_chk.spines.values():
            sp.set_visible(False)
        ax_chk.set_xticks([])
        ax_chk.set_yticks([])
        ax_chk.set_title("Labels", fontsize=9)

        chk = CheckButtons(ax_chk, ["Node IDs", "Elem IDs"], [False, False])

        def on_chk(label):
            if label == "Node IDs":
                vis = not node_id_texts[0].get_visible() if node_id_texts else False
                for t in node_id_texts:
                    t.set_visible(vis)
            elif label == "Elem IDs":
                vis = not elem_id_texts[0].get_visible() if elem_id_texts else False
                for t in elem_id_texts:
                    t.set_visible(vis)
            fig.canvas.draw_idle()

        chk.on_clicked(on_chk)

        ax_box = fig.add_axes([0.15, 0.04, 0.18, 0.05])
        box = TextBox(ax_box, "Scale", initial=str(scale_init))

        ax_scale = fig.add_axes([0.36, 0.05, 0.40, 0.03])
        s_scale = Slider(ax_scale, " ", 0.0, float(scale_init) * 200.0, valinit=float(scale_init))

        def on_box_submit(text):
            try:
                v = float(str(text).replace(",", "."))
            except Exception:
                return
            state["scale"] = v
            s_scale.set_val(v)
            draw()

        box.on_submit(on_box_submit)

        def on_slider(_):
            state["scale"] = float(s_scale.val)
            box.set_val(str(state["scale"]))
            draw()

        s_scale.on_changed(on_slider)

        draw()
        return fig, ax, (box, s_scale), chk

    def _get_restraints_df(self):
        df = getattr(self.Inp, "RestraintData", None)
        return df


    def _iter_restraint_springs(self, k_tol=1e-12):
        """
        Liefert Iterator über Restraint-Data Federn:
        yield (node, dof_int, k_value)

        Erwartete Spalten (robust):
        Node,
        kx, ky, kz, krx, kry, krz   (oder Varianten wie kX, kY, ...)

        DOF Mapping (dein 7-DoF Layout):
        transl: ux=0, uy=1, uz=3
        rot   : rx=5, ry=4, rz=2
        """
        df = self._get_restraints_df()
        if df is None:
            return

        df = df.copy()
        df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]

        if "Node" not in df.columns:
            return

        # robust column pick
        def pick(*names):
            for n in names:
                if n in df.columns:
                    return n
            # try case-insensitive
            low = {c.lower(): c for c in df.columns}
            for n in names:
                if n.lower() in low:
                    return low[n.lower()]
            return None

        col_kx  = pick("kx", "kX")
        col_ky  = pick("ky", "kY")
        col_kz  = pick("kz", "kZ")
        col_krx = pick("krx", "kRx", "kRX")
        col_kry = pick("kry", "kRy", "kRY")
        col_krz = pick("krz", "kRz", "kRZ")

        # DOF map
        dof_map = []
        if col_kx:  dof_map.append((0, col_kx))
        if col_ky:  dof_map.append((1, col_ky))
        if col_kz:  dof_map.append((3, col_kz))
        if col_krx: dof_map.append((5, col_krx))
        if col_kry: dof_map.append((4, col_kry))
        if col_krz: dof_map.append((2, col_krz))

        for _, row in df.iterrows():
            try:
                n = int(row["Node"])
            except Exception:
                continue

            for dof, col in dof_map:
                try:
                    k = float(row[col])
                except Exception:
                    continue
                if abs(k) <= float(k_tol):
                    continue
                yield n, int(dof), float(k)



    # ========================================================
    # 2D Support reactions (interaktiv)
    # ========================================================
    def plot_support_reactions_2d_interactive(
        self,
        invert_y=False,
        node_labels=True,
        elem_labels=False,
        show_forces=True,
        show_moments=True,
        scale_force_init=0.8,
        moment_radius_init=0.08,
        moment_scale_init=1.0,
        moment_kind_prefer="MY",
        robust_ref=True,
        Lref_frac=0.03,
        slider_force_max=10.0,
    ):
        fig, ax = self.plot_structure_2d(node_labels=node_labels, elem_labels=elem_labels)
        ax.set_title("Auflagerreaktionen (interaktiv)")

        r = self._reaction_vector()
        support_nodes = self._support_nodes()
        if not support_nodes:
            ax.text(0.5, 0.5, "Keine Auflagerknoten in RestraintData gefunden.",
                    transform=ax.transAxes, ha="center", va="center")
            return fig, ax, None

        Lref = self._length_ref_xz(frac=Lref_frac)

        Fvals = []
        for n in support_nodes:
            gdof = 7 * (n - 1)
            Fvals += [abs(float(r[gdof + 0])), abs(float(r[gdof + 3]))]
        Fvals = np.asarray(Fvals, dtype=float)
        if Fvals.size == 0:
            Fref = 1.0
        else:
            Fref = float(np.percentile(Fvals, 95)) if robust_ref else float(Fvals.max())
            Fref = max(Fref, 1e-12)

        def pick_moment_components(gdof_base):
            Mz = float(r[gdof_base + 2])
            My = float(r[gdof_base + 4])
            Mx = float(r[gdof_base + 5])
            return Mx, My, Mz

        def choose_moment(Mx, My, Mz):
            pref = moment_kind_prefer.upper()
            if pref == "MX":
                return Mx, "Mx"
            if pref == "MZ":
                return Mz, "Mz"
            return My, "My"

        def draw(scale_force, moment_radius, moment_scale):
            self._clear_dyn(ax)

            scale_force = float(scale_force)
            moment_radius = float(moment_radius)
            moment_scale = float(moment_scale)

            alphaF = (scale_force * Lref) / Fref

            for n in support_nodes:
                P = self._pt(int(n))
                x, z = float(P[0]), float(P[2])
                gdof = 7 * (int(n) - 1)

                Rx = float(r[gdof + 0])
                Rz = float(r[gdof + 3])

                Mx, My, Mz = pick_moment_components(gdof)
                Mplot, Mlab = choose_moment(Mx, My, Mz)

                if show_forces and (abs(Rx) > 1e-15 or abs(Rz) > 1e-15):
                    self._draw_force_arrow(ax, x, z, alphaF * Rx, alphaF * Rz, color="green")
                    self._mark_dyn(ax.text(x, z, f"R{n}", fontsize=8, color="green", ha="right", va="top"))
                    self._mark_dyn(ax.text(x, z, f"\nRx={Rx:+.3f} MN\nRz={Rz:+.3f} MN",
                                           fontsize=8, color="green", ha="left", va="top"))

                if show_moments and abs(Mplot) > 1e-15:
                    rr = moment_radius * moment_scale
                    self._draw_moment_double_arrow(ax, x, z, Mplot, radius=rr, color="purple")
                    self._mark_dyn(ax.text(x + rr, z + rr, f"{Mlab}={Mplot:+.3f} MNm", fontsize=8, color="purple"))

            ax.relim()
            ax.autoscale_view()
            ax.set_aspect("equal", adjustable="datalim")
            if invert_y:
                ax.invert_yaxis()
            fig.canvas.draw_idle()

        fig.subplots_adjust(bottom=0.25)

        ax_sF = fig.add_axes([0.15, 0.14, 0.70, 0.03])
        s_force = Slider(ax_sF, "Scale Force", 0.0, float(slider_force_max), valinit=float(scale_force_init))

        ax_sR = fig.add_axes([0.15, 0.09, 0.70, 0.03])
        s_rad = Slider(ax_sR, "Moment Radius", 0.0, float(moment_radius_init) * 20.0, valinit=float(moment_radius_init))

        ax_sM = fig.add_axes([0.15, 0.04, 0.70, 0.03])
        s_msc = Slider(ax_sM, "Moment Scale", 0.0, float(moment_scale_init) * 20.0, valinit=float(moment_scale_init))

        def update(_):
            draw(s_force.val, s_rad.val, s_msc.val)

        s_force.on_changed(update)
        s_rad.on_changed(update)
        s_msc.on_changed(update)

        draw(scale_force_init, moment_radius_init, moment_scale_init)
        return fig, ax, (s_force, s_rad, s_msc)

    # ========================================================
    # 2D nodal loads (deine robuste Version)
    # ========================================================
    def plot_nodal_loads_2d_interactive(
        self,
        invert_y=False,
        node_labels=True,
        elem_labels=False,
        show_forces=True,
        show_moments=True,
        scale_force_init=0.8,
        moment_radius_init=0.08,
        moment_scale_init=1.0,
        moment_kind_prefer="MY",
        robust_ref=True,
        Lref_frac=0.03,
        slider_force_max=10.0,
        debug=False,
    ):
        """
        Knotenlasten (interaktiv) – robust gegen verschiedene DoF-Schreibweisen
        und verschiedene Value-Spaltennamen.

        Erwartetes Format (lang):
        Node | Dof | Value[...]

        Unterstützte Dof-Strings:
        Fx,Fy,Fz,Mx,My,Mz
        X,Y,Z / Ux,Uy,Uz / Rx,Ry,Rz
        numerisch: 0,1,3,5,4,2 (Mapping passend zu deinem 7-DoF-Layout)
        """
        fig, ax = self.plot_structure_2d(node_labels=node_labels, elem_labels=elem_labels)
        ax.set_title("Knotenlasten (interaktiv) – aus NodalForces.csv")

        dfL = getattr(self.Inp, "NodalForces", None)
        if dfL is None:
            dfL = getattr(self.Inp, "NodalForcesData", None)
        if dfL is None:
            ax.text(0.5, 0.5, "Keine NodalForces Tabelle in Inp gefunden.",
                    transform=ax.transAxes, ha="center", va="center")
            return fig, ax, None

        dfL = dfL.copy()
        dfL.columns = [str(c).strip().replace("\ufeff", "") for c in dfL.columns]

        if "Node" not in dfL.columns or "Dof" not in dfL.columns:
            ax.text(0.5, 0.5, f"NodalForces: Spalten fehlen. Gefunden: {dfL.columns.tolist()}",
                    transform=ax.transAxes, ha="center", va="center")
            return fig, ax, None

        value_candidates = ["Value[MN/MNm]", "Value", "value", "P[N]", "P", "F", "Load"]
        val_col = next((c for c in value_candidates if c in dfL.columns), None)
        if val_col is None:
            ax.text(0.5, 0.5, f"NodalForces: keine Value-Spalte gefunden.\nSpalten: {dfL.columns.tolist()}",
                    transform=ax.transAxes, ha="center", va="center")
            return fig, ax, None

        dfL = dfL.dropna(subset=["Node", "Dof", val_col])

        if debug:
            print("NodalForces columns:", dfL.columns.tolist())
            print("Using value column:", val_col)
            print(dfL.head())

        def norm_dof(dof_raw):
            s = str(dof_raw).strip().upper()
            aliases = {
                "FX": "FX", "FY": "FY", "FZ": "FZ",
                "MX": "MX", "MY": "MY", "MZ": "MZ",
                "X": "FX", "Y": "FY", "Z": "FZ",
                "UX": "FX", "UY": "FY", "UZ": "FZ",
                "RX": "MX", "RY": "MY", "RZ": "MZ",
            }
            if s in aliases:
                return aliases[s]
            try:
                d = int(float(s))
                num_map = {0: "FX", 1: "FY", 3: "FZ", 5: "MX", 4: "MY", 2: "MZ"}
                return num_map.get(d, None)
            except Exception:
                return None

        data = {}
        for _, row in dfL.iterrows():
            try:
                n = int(row["Node"])
            except Exception:
                continue

            dof = norm_dof(row["Dof"])
            if dof is None:
                if debug:
                    print(f"Warnung: unbekannter Dof '{row['Dof']}' (Node {n})")
                continue

            try:
                val = float(row[val_col])
            except Exception:
                continue

            if n not in data:
                data[n] = {"FX": 0.0, "FY": 0.0, "FZ": 0.0, "MX": 0.0, "MY": 0.0, "MZ": 0.0}
            data[n][dof] += val

        nodes = sorted(data.keys())
        if len(nodes) == 0:
            ax.text(0.5, 0.5, "Keine gültigen Knotenlasten gefunden (DoF/Value prüfen).",
                    transform=ax.transAxes, ha="center", va="center")
            return fig, ax, None

        Fx = np.array([data[n]["FX"] for n in nodes], dtype=float)
        Fz = np.array([data[n]["FZ"] for n in nodes], dtype=float)
        Mx = np.array([data[n]["MX"] for n in nodes], dtype=float)
        My = np.array([data[n]["MY"] for n in nodes], dtype=float)
        Mz = np.array([data[n]["MZ"] for n in nodes], dtype=float)

        Lref = self._length_ref_xz(frac=Lref_frac)
        Fabs = np.hstack([np.abs(Fx), np.abs(Fz)])
        if Fabs.size == 0:
            Fref = 1.0
        else:
            Fref = float(np.percentile(Fabs, 95)) if robust_ref else float(Fabs.max())
            Fref = max(Fref, 1e-12)

        def choose_moment(mx, my, mz):
            pref = str(moment_kind_prefer).upper()
            if pref == "MX":
                return float(mx), "Mx"
            if pref == "MZ":
                return float(mz), "Mz"
            return float(my), "My"

        def draw(scale_force, moment_radius, moment_scale):
            self._clear_dyn(ax)

            scale_force = float(scale_force)
            moment_radius = float(moment_radius)
            moment_scale = float(moment_scale)

            alphaF = (scale_force * Lref) / Fref

            for n, fx, fz, mx, my, mz in zip(nodes, Fx, Fz, Mx, My, Mz):
                P = self._pt(int(n))
                x, z = float(P[0]), float(P[2])

                if show_forces and (abs(fx) > 1e-15 or abs(fz) > 1e-15):
                    self._draw_force_arrow(ax, x, z, alphaF * fx, alphaF * fz, color="orange")
                    self._mark_dyn(ax.text(x, z, f"F{n}", fontsize=8, color="orange", ha="right", va="top"))
                    self._mark_dyn(ax.text(x, z, f"\nFx={fx:+.3f} MN\nFz={fz:+.3f} MN",
                                           fontsize=8, color="orange", ha="left", va="top"))

                Mplot, Mlab = choose_moment(mx, my, mz)
                if show_moments and abs(Mplot) > 1e-15:
                    rr = moment_radius * moment_scale
                    self._draw_moment_double_arrow(ax, x, z, Mplot, radius=rr, color="brown")
                    self._mark_dyn(ax.text(x + rr, z + rr, f"{Mlab}={Mplot:+.3f} MNm", fontsize=8, color="brown"))

            ax.relim()
            ax.autoscale_view()
            ax.set_aspect("equal", adjustable="datalim")
            if invert_y:
                ax.invert_yaxis()
            fig.canvas.draw_idle()

        fig.subplots_adjust(bottom=0.25)

        ax_sF = fig.add_axes([0.15, 0.14, 0.70, 0.03])
        s_force = Slider(ax_sF, "Scale Force", 0.0, float(slider_force_max), valinit=float(scale_force_init))

        ax_sR = fig.add_axes([0.15, 0.09, 0.70, 0.03])
        s_rad = Slider(ax_sR, "Moment Radius", 0.0, float(moment_radius_init) * 20.0, valinit=float(moment_radius_init))

        ax_sM = fig.add_axes([0.15, 0.04, 0.70, 0.03])
        s_msc = Slider(ax_sM, "Moment Scale", 0.0, float(moment_scale_init) * 20.0, valinit=float(moment_scale_init))

        def update(_):
            draw(s_force.val, s_rad.val, s_msc.val)

        s_force.on_changed(update)
        s_rad.on_changed(update)
        s_msc.on_changed(update)

        draw(scale_force_init, moment_radius_init, moment_scale_init)
        return fig, ax, (s_force, s_rad, s_msc)
