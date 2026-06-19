#!/usr/bin/env python3
import re
import sys
from pathlib import Path


EXPECTED_IMAGES = {
    "/fable_flux_logo.svg": (
        "Fable Flux Logo",
        "710",
        "565",
        "mx-auto max-w-48 w-full h-auto",
    ),
    "/hero_text.svg": (
        "Personalized Storytelling Unforgettable Lessons",
        "976",
        "163",
        "mx-auto max-w-lg w-full h-auto",
    ),
    "/fable_flux_hero.png": (
        "Fable Flux Hero",
        "1212",
        "1046",
        "mx-auto max-w-xl w-full h-auto",
    ),
    "/create_story.svg": (
        "Create Story",
        "1391",
        "146",
        "max-w-sm w-full h-auto",
    ),
    "/learn_more_btn.png": (
        "Learn More",
        "1391",
        "146",
        "max-w-sm w-full h-auto",
    ),
}


def check_home_page(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    if 'import Image from "next/image";' not in source:
        raise SystemExit("Home page must import next/image.")
    if re.search(r"<img\b", source, flags=re.IGNORECASE):
        raise SystemExit("Home page must not restore raw img elements.")

    images = re.findall(r"<Image\b(.*?)/>", source, flags=re.DOTALL)
    if len(images) != len(EXPECTED_IMAGES):
        raise SystemExit("Home page must keep exactly five optimized image elements.")

    observed = {}
    for image in images:
        strings = dict(re.findall(r'(src|alt|className)="([^"]*)"', image))
        numbers = dict(re.findall(r'(width|height)=\{(\d+)\}', image))
        src = strings.get("src")
        if not src:
            raise SystemExit("Every optimized home page image must declare a source.")
        if src in observed:
            raise SystemExit("Home page image sources must be unique.")
        observed[src] = (
            strings.get("alt"),
            numbers.get("width"),
            numbers.get("height"),
            strings.get("className"),
        )

    if observed != EXPECTED_IMAGES:
        raise SystemExit("Home page optimized image mappings or dimensions changed.")


def check_plan(path: Path) -> None:
    plan = path.read_text(encoding="utf-8")
    required = (
        "status: completed",
        "frontend lint",
        "production build",
        "hostile mutations were rejected",
    )
    if any(value not in plan for value in required):
        raise SystemExit(
            "Home image plan must record completed lint, build, and mutation verification."
        )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: check-home-next-image.py HOME_PAGE PLAN")
    check_home_page(Path(sys.argv[1]))
    check_plan(Path(sys.argv[2]))
