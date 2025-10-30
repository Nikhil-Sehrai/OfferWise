# home/views.py
from __future__ import annotations
from typing import Dict, Any, Tuple
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods

# Seeded demo bands (P25, P50, P75)
BANDS: Dict[Tuple[str, str], Tuple[float, float, float]] = {
    ('Analyst','BLR'): (7.0, 8.5, 10.0),
    ('AE','BLR'): (8.0, 10.0, 12.0),
    ('Area Sales Exec','BLR'): (6.0, 7.0, 8.0),

    ('Analyst','DEL'): (7.5, 9.0, 10.5),
    ('AE','DEL'): (8.5, 10.5, 12.5),
    ('Area Sales Exec','DEL'): (6.5, 7.5, 8.5),

    ('Analyst','MUM'): (7.2, 8.8, 10.3),
    ('AE','MUM'): (8.2, 10.2, 12.2),
    ('Area Sales Exec','MUM'): (6.2, 7.2, 8.2),
}

# ---------- Helpers ------------------------------------------------------------

def _to_float(val: str | None, default: float = 0.0) -> float:
    try:
        return float(val) if val not in (None, "") else default
    except ValueError:
        return default

def _ensure_offer_in_session(req: HttpRequest) -> Dict[str, Any]:
    offer = req.session.get("offer", {})
    return {
        "role":  offer.get("role", "Analyst"),
        "level": offer.get("level", "L4"),
        "city":  offer.get("city", "BLR"),
        "base":  float(offer.get("base", 0.0)),
        "bonus": float(offer.get("bonus", 0.0)),
        "jb":    float(offer.get("jb", 0.0)),
    }

def _save_offer(req: HttpRequest, offer: Dict[str, Any]) -> None:
    req.session["offer"] = offer
    req.session.modified = True

def _save_benchmarks(req: HttpRequest, bm: Dict[str, float]) -> None:
    req.session["benchmarks"] = bm
    req.session.modified = True

def _calc_bands(role: str, city: str, base: float) -> Dict[str, float]:
    p25, p50, p75 = BANDS.get((role, city), (
        base * 0.9 if base else 7.0,
        base or 8.5,
        (base or 8.5) * 1.2
    ))
    return {"p25": round(p25, 2), "p50": round(p50, 2), "p75": round(p75, 2)}

def _ctx(req: HttpRequest) -> Dict[str, Any]:
    offer = _ensure_offer_in_session(req)
    bm = req.session.get("benchmarks", {})
    return {**offer, **bm}

# ---------- Views --------------------------------------------------------------

def home(req: HttpRequest) -> HttpResponse:
    return render(req, "home.html")

@require_http_methods(["GET", "POST"])
def offer_new(req: HttpRequest) -> HttpResponse:
    # GET → form
    if req.method == "GET":
        return render(req, "offer_form.html")

    # POST → save offer + bands → show benchmarks
    role  = (req.POST.get("role") or "Analyst").strip()
    level = (req.POST.get("level") or "L4").strip()
    city  = (req.POST.get("city") or "BLR").strip()
    base  = _to_float(req.POST.get("base"), 0.0)
    bonus = _to_float(req.POST.get("bonus"), 0.0)
    jb    = _to_float(req.POST.get("jb"), 0.0)

    offer = {"role": role, "level": level, "city": city, "base": base, "bonus": bonus, "jb": jb}
    _save_offer(req, offer)
    bm = _calc_bands(role, city, base)
    _save_benchmarks(req, bm)

    return render(req, "benchmarks.html", {**offer, **bm})

@require_http_methods(["GET", "POST"])
def benchmarks(req: HttpRequest) -> HttpResponse:
    # If form posted directly here, save then compute bands
    if req.method == "POST":
        role  = (req.POST.get("role") or "Analyst").strip()
        level = (req.POST.get("level") or "L4").strip()
        city  = (req.POST.get("city") or "BLR").strip()
        base  = _to_float(req.POST.get("base"), 0.0)
        bonus = _to_float(req.POST.get("bonus"), 0.0)
        jb    = _to_float(req.POST.get("jb"), 0.0)
        _save_offer(req, {"role": role, "level": level, "city": city, "base": base, "bonus": bonus, "jb": jb})
        _save_benchmarks(req, _calc_bands(role, city, base))

    offer = _ensure_offer_in_session(req)
    bm = req.session.get("benchmarks")
    if not bm:
        bm = _calc_bands(offer["role"], offer["city"], offer["base"])
        _save_benchmarks(req, bm)

    return render(req, "benchmarks.html", {**offer, **bm})

def simulator(req: HttpRequest) -> HttpResponse:
    ctx = _ctx(req)
    # Defensive: don’t render simulator if base/bonus/jb are all zero
    if (ctx.get("base", 0.0) + ctx.get("bonus", 0.0) + ctx.get("jb", 0.0)) == 0.0:
        return redirect("offer_new")
    return render(req, "simulator.html", ctx)

def script_studio(req: HttpRequest) -> HttpResponse:
    ctx = _ctx(req)
    if (ctx.get("base", 0.0) + ctx.get("bonus", 0.0) + ctx.get("jb", 0.0)) == 0.0:
        return redirect("offer_new")
    return render(req, "script_studio.html", ctx)

def review(req: HttpRequest) -> HttpResponse:
    return render(req, "review.html")

def learning_hub(req: HttpRequest) -> HttpResponse:
    return render(req, "learning_hub.html")
