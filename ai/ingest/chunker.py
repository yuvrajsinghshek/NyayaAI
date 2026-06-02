# ============================================
# NyayaAI — Smart Chunker
# Takes extracted pages and splits into chunks
# Each chunk is small enough for ChromaDB
# Overlap keeps context between chunks intact
# ============================================

import re
from ai.config import CHUNK_SIZE, CHUNK_OVERLAP, CATEGORIES
import logging

log = logging.getLogger(__name__)

# keyword map — detects which topic a chunk belongs to
# if any keyword found in chunk text — assign that category
SECTION_KEYWORDS = {
    "Digital Arrest Scam"       : ["digital arrest", "scam alert",
                                    "advisory"],
    "Scam Modus Operandi"       : ["modus operandi", "impersonation",
                                    "ivr calling", "intimidation",
                                    "digital confinement"],
    "Cybercrime Prevention Tips": ["precaution", "prevention",
                                    "stop think", "verify identity",
                                    "never share"],
    "NCRP Portal Usage"         : ["cybercrime.gov.in", "ncrp",
                                    "reporting portal", "1930"],
    "Complaint Filing Process"  : ["file complaint", "report and track",
                                    "anonymous", "register complaint"],
    "Evidence and Legal Process": ["evidence", "hash value", "fir",
                                    "false complaint", "withdraw"],
    "Money Mule Operations"     : ["money mule", "mule account",
                                    "otp based", "f2f", "commission"],
    "Underground Banking Trends": ["underground banking",
                                    "telegram channel",
                                    "merchant qr", "mqr",
                                    "bulk upload"],
    "USDT Crypto Laundering"    : ["usdt", "crypto",
                                    "inr conversion",
                                    "gaming fund", "stock fund"],
    "Illegal Loan Apps"         : ["loan app", "offshore", "nbfc",
                                    "play store", "blackmail"],
    "Banking Fraud Indicators"  : ["mule account statement",
                                    "pass through", "inflow",
                                    "outflow", "red flag"],
    "Regulatory Recommendations": ["recommendation", "npci",
                                    "upi ecosystem", "fintech"]
}


def detect_category(text):
    # lowercase for case insensitive matching
    text_lower = text.lower()

    # check each category keywords against chunk text
    # return first matching category
    for category, keywords in SECTION_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return category

    # no keyword matched — return general category
    return "General Cybercrime"


def chunk_single_page(page, chunk_id_start):
    # split page text into list of words
    words    = page["text"].split()
    chunks   = []
    chunk_id = chunk_id_start
    start    = 0

    # skip pages with very few words
    if len(words) < 50:
        return chunks, chunk_id

    while start < len(words):
        end         = min(start + CHUNK_SIZE, len(words))
        chunk_words = " ".join(words[start:end])

        # detect which topic this chunk belongs to
        category = detect_category(chunk_words)

        # build source string for display in frontend
        if page["page_no"] == "FAQ":
            source = page["source_name"]
        else:
            source = f"{page['source_name']} — Page {page['page_no']}"

        chunks.append({
            "chunk_id"   : f"chunk_{chunk_id:04d}",
            "text"       : chunk_words,
            "word_count" : len(words[start:end]),
            "category"   : category,
            "source"     : source,
            "source_key" : page["source_key"],
            "file_type"  : page["file_type"]
        })

        chunk_id += 1

        # calculate next start with overlap
        next_start = end - CHUNK_OVERLAP

        # ensure start always moves forward — prevents infinite loop
        if next_start <= start:
            next_start = start + CHUNK_SIZE
        start = next_start

        # stop when end of words reached
        if end >= len(words):
            break

    return chunks, chunk_id


def chunk_all(pages_data):
    # process all pages and split into chunks
    all_chunks = []
    chunk_id   = 0

    for page in pages_data:
        chunks, chunk_id = chunk_single_page(page, chunk_id)
        all_chunks.extend(chunks)

    log.info(f"✅ Total chunks created: {len(all_chunks)}")
    return all_chunks
