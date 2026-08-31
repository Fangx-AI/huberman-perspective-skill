#!/usr/bin/env python3
"""Shared source classification for Episode resources and knowledge-graph nodes."""
from __future__ import annotations

from urllib.parse import urlparse


ACADEMIC_EXACT_HOSTS = {
    "academic.oup.com",
    "acpjournals.org",
    "ahajournals.org",
    "annualreviews.org",
    "asa.scitation.org",
    "atsjournals.org",
    "auajournals.org",
    "biologicalpsychiatryjournal.com",
    "biorxiv.org",
    "bmj.com",
    "cambridge.org",
    "cell.com",
    "classic.clinicaltrials.gov",
    "clinicaltrials.gov",
    "cochrane.org",
    "cochranelibrary.com",
    "diabetesjournals.org",
    "doi.apa.org",
    "doi.org",
    "elifesciences.org",
    "erj.ersjournals.com",
    "escholarship.org",
    "frontiersin.org",
    "gastrojournal.org",
    "global.oup.com",
    "guilfordjournals.com",
    "hindawi.com",
    "iovs.arvojournals.org",
    "jamanetwork.com",
    "jneurosci.org",
    "journal-jop.org",
    "journals.aom.org",
    "journals.biologists.com",
    "journals.healio.com",
    "journals.humankinetics.com",
    "journals.lww.com",
    "journals.physiology.org",
    "journals.plos.org",
    "journals.sagepub.com",
    "journals.uchicago.edu",
    "jstor.org",
    "karger.com",
    "liebertpub.com",
    "link.springer.com",
    "linkinghub.elsevier.com",
    "mayoclinicproceedings.org",
    "mdpi.com",
    "medrxiv.org",
    "metabolismjournal.com",
    "n.neurology.org",
    "nature.com",
    "ncbi.nlm.nih.gov",
    "nejm.org",
    "neurology.org",
    "onlinelibrary.wiley.com",
    "physoc.onlinelibrary.wiley.com",
    "pmc.ncbi.nlm.nih.gov",
    "pnas.org",
    "proceedings.neurips.cc",
    "psychiatrist.com",
    "psychiatryonline.org",
    "psycnet.apa.org",
    "pubmed.ncbi.nlm.nih.gov",
    "pubs.acs.org",
    "pubs.aip.org",
    "pubs.rsc.org",
    "researchgate.net",
    "researchprotocols.org",
    "royalsocietypublishing.org",
    "scholar.google.ca",
    "scholar.google.com",
    "science.org",
    "science.sciencemag.org",
    "sciencedirect.com",
    "sleephealthjournal.org",
    "tandfonline.com",
    "thelancet.com",
    "thieme-connect.com",
}

ACADEMIC_HOST_SUFFIXES = (
    ".biomedcentral.com",
    ".bmj.com",
    ".nature.com",
    ".oup.com",
    ".psychiatryonline.org",
    ".sciencedirect.com",
    ".springer.com",
    ".springeropen.com",
    ".wiley.com",
)


def classify_resource(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    if host in ACADEMIC_EXACT_HOSTS or host.endswith(ACADEMIC_HOST_SUFFIXES):
        return "academic-or-medical"
    if "hubermanlab.com" in host or "stanford.edu" in host:
        return "official-or-institutional"
    if "youtube.com" in host or "youtu.be" in host:
        return "video"
    return "other-resource"
