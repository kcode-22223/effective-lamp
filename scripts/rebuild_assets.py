#!/usr/bin/env python3

import json
import os
import re
import shutil
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

###############################################################################
# Configuration
###############################################################################

MANIFEST_FILE = Path("catalog_manifest.json")
SOURCE_FOLDER = Path("working_images")
OUTPUT_FOLDER = Path("MockCatalog.xcassets")

###############################################################################
# Utility
###############################################################################

def log(*args):
    print(*args)

def fatal(message):
    print()
    print("=" * 80)
    print("ERROR")
    print("=" * 80)
    print(message)
    sys.exit(1)

###############################################################################
# Normalize
###############################################################################

def normalize(name):

    if name is None:
        return ""

    name = str(name)

    name = os.path.splitext(name)[0]

    replacements = [

        "_Normal",
        "_Pressed",
        "_Hover",
        "_Selected",
        "_Highlighted",
        "_Disabled",
        "_Focused",
        "_Default",
        "_Small",
        "_Large",
        "_Light",
        "_Dark",
        "_Blue",
        "_White"

    ]

    for item in replacements:

        name = re.sub(
            item + r'(@[123]x)?$',
            '',
            name,
            flags=re.I
        )

    name = re.sub(r'@[123]x$', '', name, flags=re.I)

    name = re.sub(r'_[0-9]+$', '', name)

    name = name.lower()

    name = re.sub(r'[^a-z0-9]', '', name)

    return name

###############################################################################
# Alias table
###############################################################################

ALIASES = {

    "hero4":[
        "hero4-turn-on",
        "hero4-turn-wifi-on"
    ],

    "hero3":[
        "hero3-turn-on",
        "hero3-turn-wifi-on"
    ],

    "hero5":[
        "hero5-2018-turn-on",
        "hero5-2018-turn-wifi-on"
    ],

    "hero6":[
        "hero6-7-turn-on",
        "hero6-turn-wifi-on"
    ],

    "hero7":[
        "hero7-turn-wifi-on"
    ],

    "hero_plus":[
        "hero+-turn-on",
        "hero+-turn-wifi-on"
    ],

    "hero_session":[
        "hero-session-turn-wifi-on",
        "hero5-session-turn-wifi-on"
    ],

    "vg_logo":[
        "vg-logo-small"
    ],

    "gopro_logo":[
        "gopro_logo",
        "logo",
        "logo small"
    ],

    "battery":[
        "battery-empty",
        "battery-halfway",
        "battery-full",
        "battery-low",
        "battery-charging",
        "battery-nobattery"
    ],

    "tutorial":[
        "tutorial-step-1-on",
        "tutorial-step-1-off",
        "tutorial-step-2-on",
        "tutorial-step-2-off",
        "tutorial-step-3-on",
        "tutorial-step-3-off",
        "tutorial-step-4-on",
        "tutorial-step-4-off"
    ]

}

###############################################################################
# UTI mapping
###############################################################################

UTI_EXTENSIONS = {

    "public.png":".png",
    "public.jpeg":".jpg",
    "public.jpg":".jpg",
    "public.gif":".gif",
    "com.compuserve.gif":".gif",
    "public.tiff":".tiff",
    "public.heic":".heic",
    "public.pdf":".pdf",
    "public.bmp":".bmp"

}

###############################################################################
# Validation
###############################################################################

if not MANIFEST_FILE.exists():
    fatal("catalog_manifest.json not found.")

if not SOURCE_FOLDER.exists():
    fatal("working_images folder not found.")

if OUTPUT_FOLDER.exists():
    shutil.rmtree(OUTPUT_FOLDER)

OUTPUT_FOLDER.mkdir(parents=True)

###############################################################################
# Root Contents.json
###############################################################################

with open(
    OUTPUT_FOLDER / "Contents.json",
    "w",
    encoding="utf-8"
) as fp:

    json.dump(
        {
            "info":{
                "author":"xcode",
                "version":1
            }
        },
        fp,
        indent=2
    )

###############################################################################
# Load Manifest
###############################################################################

with open(
    MANIFEST_FILE,
    "r",
    encoding="utf-8"
) as fp:

    manifest = json.load(fp)

if isinstance(manifest,list):

    manifest_entries = manifest

elif isinstance(manifest,dict):

    manifest_entries = (
        manifest.get("assets")
        or manifest.get("images")
        or manifest.get("entries")
        or []
    )

else:

    fatal("Unsupported manifest.")

log()
log("="*80)
log("Manifest")
log("="*80)
log(f"Entries: {len(manifest_entries)}")

###############################################################################
# Build Manifest Index
###############################################################################

assets=[]

for i,entry in enumerate(manifest_entries):

    name=str(entry.get("Name","")).strip()

    if not name:
        continue

    assets.append({

        "index":i,

        "entry":entry,

        "name":name,

        "normalized":normalize(name),

        "used":False

    })

###############################################################################
# Build Replacement Index
###############################################################################

replacement_files=[]

for root,dirs,files in os.walk(SOURCE_FOLDER):

    dirs.sort()

    files.sort()

    for file in files:

        if file.startswith("."):
            continue

        full=Path(root)/file

        replacement_files.append({

            "filename":file,

            "path":full,

            "stem":full.stem,

            "normalized":normalize(file),

            "extension":full.suffix.lower()

        })

log()
log("="*80)
log("Replacement Files")
log("="*80)

for item in replacement_files:

    log(item["filename"])

###############################################################################
# Candidate Scoring
###############################################################################

def score(file,asset):

    fn=file["normalized"]

    an=asset["normalized"]

    score=0

    if fn==an:
        score+=50000

    if fn.startswith(an):
        score+=25000

    if an.startswith(fn):
        score+=24000

    if fn in an:
        score+=18000

    if an in fn:
        score+=17000

    ratio=SequenceMatcher(
        None,
        fn,
        an
    ).ratio()

    score+=int(ratio*10000)

    words1=set(
        re.findall(
            "[a-z0-9]+",
            fn
        )
    )

    words2=set(
        re.findall(
            "[a-z0-9]+",
            an
        )
    )

    score+=len(words1&words2)*300

    for alias,targets in ALIASES.items():

        if fn==normalize(alias):

            for target in targets:

                if normalize(target)==an:

                    score+=35000

    return score

###############################################################################
# Build ALL Candidates
###############################################################################

log()
log("="*80)
log("Building Candidate List")
log("="*80)

candidates=[]

for file_index,file in enumerate(replacement_files):

    for asset_index,asset in enumerate(assets):

        s=score(file,asset)

        if s<5000:
            continue

        candidates.append({

            "score":s,

            "file":file_index,

            "asset":asset_index

        })

log(f"Candidates: {len(candidates)}")

###############################################################################
# Global Assignment
###############################################################################

candidates.sort(
    key=lambda x:x["score"],
    reverse=True
)

used_files=set()
used_assets=set()

matches=[]

for candidate in candidates:

    if candidate["file"] in used_files:
        continue

    if candidate["asset"] in used_assets:
        continue

    used_files.add(candidate["file"])
    used_assets.add(candidate["asset"])

    matches.append({

        "score":candidate["score"],

        "file":replacement_files[
            candidate["file"]
        ],

        "asset":assets[
            candidate["asset"]
        ]

    })

log()
log("="*80)
log("Chosen Matches")
log("="*80)

for match in matches:

    log(
        f"{match['score']:>6}  "
        f"{match['file']['filename']}  ->  "
        f"{match['asset']['name']}"
    )

duplicate_counter=defaultdict(int)

successful=0
failed=0

###############################################################################
# Generate XCAssets
###############################################################################

for match in matches:
```
    file = match["file"]

    asset = match["asset"]

    manifest = asset["entry"]

    name = asset["name"]

    duplicate_counter[name] += 1

    folder_name = name

    if duplicate_counter[name] > 1:

        folder_name = (
            f"{name}_{duplicate_counter[name]}"
        )

    asset_type = str(
        manifest.get(
            "AssetType",
            "Data"
        )
    )

    uti = str(
        manifest.get(
            "UTI",
            "public.data"
        )
    )

    is_image = (
        asset_type.lower() == "image"
    )

    if uti.startswith("public.image"):
        is_image = True

    if uti in (
        "public.png",
        "public.jpeg",
        "public.jpg",
        "public.tiff",
        "public.bmp",
        "public.heic",
        "public.pdf"
    ):
        is_image = True

    folder_suffix = (
        ".imageset"
        if is_image
        else ".dataset"
    )

    asset_folder = (
        OUTPUT_FOLDER /
        (folder_name + folder_suffix)
    )

    asset_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    extension = file["extension"]

    if (
        not extension
        and uti in UTI_EXTENSIONS
    ):

        extension = UTI_EXTENSIONS[uti]

    if not extension:

        extension = ".bin"

    output_filename = (
        folder_name +
        extension
    )

    shutil.copy2(

        file["path"],

        asset_folder /
        output_filename

    )

    contents = {

        "info": {

            "author": "xcode",

            "version": 1

        }

    }

    ###########################################################################
    # Image Assets
    ###########################################################################

    if is_image:

        scale = manifest.get(
            "Scale",
            1
        )

        try:

            scale = int(scale)

        except Exception:

            scale = 1

        if scale not in (1, 2, 3):

            scale = 1

        image = {

            "idiom":
                manifest.get(
                    "Idiom",
                    "universal"
                ),

            "filename":
                output_filename,

            "scale":
                f"{scale}x"

        }

        if "DisplayGamut" in manifest:

            image["display-gamut"] = (
                manifest["DisplayGamut"]
            )

        if "MemoryClass" in manifest:

            image["memory"] = (
                manifest["MemoryClass"]
            )

        if "Subtype" in manifest:

            image["subtype"] = (
                manifest["Subtype"]
            )

        contents["images"] = [

            image

        ]

    ###########################################################################
    # Dataset Assets
    ###########################################################################

    else:

        data = {

            "idiom":
                manifest.get(
                    "Idiom",
                    "universal"
                ),

            "filename":
                output_filename,

            "universal-type-identifier":
                uti

        }

        contents["data"] = [

            data

        ]

    ###########################################################################
    # Preserve Manifest Metadata
    ###########################################################################

    properties = {}

    PROPERTY_MAP = {

        "State": "state",

        "Value": "value",

        "Compression": "compression",

        "CompressionType":
            "compression-type",

        "GraphicsClass":
            "graphics-class",

        "TemplateRenderingMode":
            "template-rendering-intent",

        "Localization":
            "localization",

        "Appearance":
            "appearance",

        "LanguageDirection":
            "language-direction",

        "Alignment":
            "alignment",

        "ColorSpace":
            "color-space"

    }

    for source, target in PROPERTY_MAP.items():

        if source in manifest:

            properties[target] = (
                manifest[source]
            )

    ignored = {

        "Name",
        "NameIdentifier",
        "AssetType",
        "Scale",
        "Idiom",
        "UTI",
        "Compression",
        "CompressionType",
        "SHA1Digest",
        "Data Length",
        "SizeOnDisk",
        "MemoryClass",
        "DisplayGamut",
        "Subtype"

    }

    for key, value in manifest.items():

        if key in ignored:

            continue

        if key in PROPERTY_MAP:

            continue

        properties[key] = value

    if properties:

        contents["properties"] = properties

    with open(

        asset_folder /
        "Contents.json",

        "w",

        encoding="utf-8"

    ) as fp:

        json.dump(

            contents,

            fp,

            indent=2,

            ensure_ascii=False

        )

    successful += 1

################################################################################
# Validation
################################################################################

log()
log("=" * 80)
log("Validation")
log("=" * 80)

imagesets = 0
datasets = 0
broken = 0

for folder in OUTPUT_FOLDER.iterdir():

    if not folder.is_dir():
        continue

    if folder.suffix == ".imageset":
        imagesets += 1

    elif folder.suffix == ".dataset":
        datasets += 1

    if not (folder / "Contents.json").exists():

        broken += 1

log(f"Imagesets : {imagesets}")
log(f"Datasets  : {datasets}")
log(f"Broken    : {broken}")

if broken:

    fatal("One or more asset folders are invalid.")

################################################################################
# Build Reports
################################################################################

match_report = []

for match in sorted(

    matches,

    key=lambda m: (
        -m["score"],
        m["asset"]["name"].lower()
    )

):

    match_report.append({

        "ReplacementFile":
            match["file"]["filename"],

        "ManifestName":
            match["asset"]["name"],

        "Score":
            match["score"],

        "AssetType":
            match["asset"]["entry"].get(
                "AssetType",
                ""
            ),

        "UTI":
            match["asset"]["entry"].get(
                "UTI",
                ""
            )

    })
```
with open(

    "match_report.json",

    "w",

    encoding="utf-8"

) as fp:

    json.dump(

        match_report,

        fp,

        indent=2,

        ensure_ascii=False

    )

with open(

    "match_report.txt",

    "w",

    encoding="utf-8"

) as fp:

    fp.write("GoPro Asset Match Report\n")
    fp.write("=" * 80 + "\n\n")

    for match in sorted(

        matches,

        key=lambda m: (
            -m["score"],
            m["asset"]["name"].lower()
        )

    ):

        fp.write(
            f"{match['file']['filename']}\n"
        )

        fp.write(
            f"    -> {match['asset']['name']}\n"
        )

        fp.write(
            f"    Score : {match['score']}\n"
        )

        fp.write(
            f"    Type  : "
            f"{match['asset']['entry'].get('AssetType','')}\n"
        )

        fp.write(
            f"    UTI   : "
            f"{match['asset']['entry'].get('UTI','')}\n\n"
        )

################################################################################
# Review Weak Matches
################################################################################

weak = []

for match in matches:

    if match["score"] < 15000:

        weak.append(match)

if weak:

    log()
    log("=" * 80)
    log("Weak Matches")
    log("=" * 80)

    for match in weak:

        log(
            f"{match['score']:>6}  "
            f"{match['file']['filename']}  ->  "
            f"{match['asset']['name']}"
        )

################################################################################
# Unmatched Replacement Files
################################################################################

matched_paths = {

    m["file"]["path"]

    for m in matches

}

unmatched = []

for file in replacement_files:

    if file["path"] not in matched_paths:

        unmatched.append(file)

with open(

    "unmatched_files.txt",

    "w",

    encoding="utf-8"

) as fp:

    if unmatched:

        for file in unmatched:

            fp.write(
                file["filename"] + "\n"
            )

    else:

        fp.write(
            "All replacement files matched.\n"
        )

################################################################################
# Statistics
################################################################################

asset_type_count = defaultdict(int)

uti_count = defaultdict(int)

for match in matches:

    entry = match["asset"]["entry"]

    asset_type_count[
        entry.get(
            "AssetType",
            "Unknown"
        )
    ] += 1

    uti_count[
        entry.get(
            "UTI",
            "Unknown"
        )
    ] += 1

with open(

    "statistics.txt",

    "w",

    encoding="utf-8"

) as fp:

    fp.write("Asset Type Counts\n")
    fp.write("=================\n\n")

    for key in sorted(asset_type_count):

        fp.write(
            f"{key}: {asset_type_count[key]}\n"
        )

    fp.write("\n")

    fp.write("UTI Counts\n")
    fp.write("==========\n\n")

    for key in sorted(uti_count):

        fp.write(
            f"{key}: {uti_count[key]}\n"
        )

################################################################################
# Final Summary
################################################################################

log()
log("=" * 80)
log("Summary")
log("=" * 80)

log(f"Manifest entries     : {len(manifest_entries)}")
log(f"Replacement files    : {len(replacement_files)}")
log(f"Matches              : {len(matches)}")
log(f"Imagesets            : {imagesets}")
log(f"Datasets             : {datasets}")
log(f"Weak matches         : {len(weak)}")
log(f"Unused replacements  : {len(unmatched)}")
log()

log("Generated files:")

log("  MockCatalog.xcassets/")
log("  match_report.json")
log("  match_report.txt")
log("  unmatched_files.txt")
log("  statistics.txt")

if successful == 0:

    fatal("No assets were generated.")

log()
log("=" * 80)
log("Finished Successfully")
log("=" * 80)

sys.exit(0)
